package handler

import (
	"context"
	"strconv"

	"github.com/gofiber/fiber/v2"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Handler struct {
	db *pgxpool.Pool
}

func New(db *pgxpool.Pool) *Handler {
	return &Handler{db: db}
}

// GetStats returns overall statistics
func (h *Handler) GetStats(c *fiber.Ctx) error {
	ctx := context.Background()

	var totalIncidents, totalVictims, totalDeaths, totalHospitalized int
	var provincesAffected int

	h.db.QueryRow(ctx, `
		SELECT 
			COUNT(*), 
			COALESCE(SUM(victim_count), 0),
			COALESCE(SUM(deaths), 0),
			COALESCE(SUM(hospitalized), 0)
		FROM incidents
	`).Scan(&totalIncidents, &totalVictims, &totalDeaths, &totalHospitalized)

	h.db.QueryRow(ctx, `
		SELECT COUNT(DISTINCT province_id) FROM incidents WHERE province_id IS NOT NULL
	`).Scan(&provincesAffected)

	// Get aggregate data (KPAI, JPPI, etc.)
	type AggData struct {
		Source      string `json:"source"`
		Org         string `json:"org"`
		Total       int    `json:"total"`
		PeriodStart string `json:"period_start"`
		PeriodEnd   string `json:"period_end"`
		Notes       string `json:"notes"`
	}

	rows, _ := h.db.Query(ctx, `
		SELECT source_name, COALESCE(source_org, ''), total_victims, 
			   COALESCE(TO_CHAR(period_start, 'YYYY-MM-DD'), ''),
			   COALESCE(TO_CHAR(period_end, 'YYYY-MM-DD'), ''),
			   COALESCE(notes, '')
		FROM aggregate_data ORDER BY total_victims DESC
	`)
	defer rows.Close()

	var aggregates []AggData
	for rows.Next() {
		var a AggData
		rows.Scan(&a.Source, &a.Org, &a.Total, &a.PeriodStart, &a.PeriodEnd, &a.Notes)
		aggregates = append(aggregates, a)
	}

	return c.JSON(fiber.Map{
		"total_incidents":    totalIncidents,
		"total_victims":     totalVictims,
		"total_deaths":      totalDeaths,
		"total_hospitalized": totalHospitalized,
		"provinces_affected": provincesAffected,
		"aggregate_data":    aggregates,
	})
}

// GetIncidents returns paginated incidents
func (h *Handler) GetIncidents(c *fiber.Ctx) error {
	ctx := context.Background()

	page, _ := strconv.Atoi(c.Query("page", "1"))
	limit, _ := strconv.Atoi(c.Query("limit", "20"))
	provinceID := c.Query("province_id")
	sortBy := c.Query("sort", "incident_date")
	order := c.Query("order", "DESC")

	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}
	if order != "ASC" && order != "DESC" {
		order = "DESC"
	}
	allowedSorts := map[string]bool{"incident_date": true, "victim_count": true, "created_at": true}
	if !allowedSorts[sortBy] {
		sortBy = "incident_date"
	}

	offset := (page - 1) * limit

	// Build query
	baseQuery := `
		FROM incidents i
		LEFT JOIN provinces p ON i.province_id = p.id
		LEFT JOIN districts d ON i.district_id = d.id
	`
	where := " WHERE 1=1"
	args := []interface{}{}
	argIdx := 1

	if provinceID != "" {
		where += " AND i.province_id = $" + strconv.Itoa(argIdx)
		pid, _ := strconv.Atoi(provinceID)
		args = append(args, pid)
		argIdx++
	}

	// Count
	var total int
	countQuery := "SELECT COUNT(*) " + baseQuery + where
	h.db.QueryRow(ctx, countQuery, args...).Scan(&total)

	// Fetch
	selectQuery := `
		SELECT i.id, i.title, COALESCE(i.description, ''), i.victim_count, 
			   i.hospitalized, i.deaths,
			   COALESCE(TO_CHAR(i.incident_date, 'YYYY-MM-DD'), ''),
			   COALESCE(p.name, ''), COALESCE(d.name, ''),
			   COALESCE(i.location_detail, ''),
			   i.menu_items, i.symptoms,
			   COALESCE(i.source_url, ''), COALESCE(i.source_name, ''),
			   i.verified
	` + baseQuery + where + " ORDER BY i." + sortBy + " " + order + " NULLS LAST"

	selectQuery += " LIMIT $" + strconv.Itoa(argIdx) + " OFFSET $" + strconv.Itoa(argIdx+1)
	args = append(args, limit, offset)

	rows, err := h.db.Query(ctx, selectQuery, args...)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}
	defer rows.Close()

	type Incident struct {
		ID             int      `json:"id"`
		Title          string   `json:"title"`
		Description    string   `json:"description"`
		VictimCount    int      `json:"victim_count"`
		Hospitalized   int      `json:"hospitalized"`
		Deaths         int      `json:"deaths"`
		IncidentDate   string   `json:"incident_date"`
		Province       string   `json:"province"`
		District       string   `json:"district"`
		LocationDetail string   `json:"location_detail"`
		MenuItems      []string `json:"menu_items"`
		Symptoms       []string `json:"symptoms"`
		SourceURL      string   `json:"source_url"`
		SourceName     string   `json:"source_name"`
		Verified       bool     `json:"verified"`
	}

	var incidents []Incident
	for rows.Next() {
		var inc Incident
		rows.Scan(
			&inc.ID, &inc.Title, &inc.Description, &inc.VictimCount,
			&inc.Hospitalized, &inc.Deaths, &inc.IncidentDate,
			&inc.Province, &inc.District, &inc.LocationDetail,
			&inc.MenuItems, &inc.Symptoms,
			&inc.SourceURL, &inc.SourceName, &inc.Verified,
		)
		incidents = append(incidents, inc)
	}

	return c.JSON(fiber.Map{
		"data":  incidents,
		"total": total,
		"page":  page,
		"limit": limit,
	})
}

// GetIncidentByID returns a single incident
func (h *Handler) GetIncidentByID(c *fiber.Ctx) error {
	ctx := context.Background()
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "invalid id"})
	}

	type Incident struct {
		ID             int      `json:"id"`
		Title          string   `json:"title"`
		Description    string   `json:"description"`
		VictimCount    int      `json:"victim_count"`
		Hospitalized   int      `json:"hospitalized"`
		Deaths         int      `json:"deaths"`
		IncidentDate   string   `json:"incident_date"`
		Province       string   `json:"province"`
		District       string   `json:"district"`
		LocationDetail string   `json:"location_detail"`
		MenuItems      []string `json:"menu_items"`
		Symptoms       []string `json:"symptoms"`
		SourceURL      string   `json:"source_url"`
		SourceName     string   `json:"source_name"`
		Verified       bool     `json:"verified"`
	}

	var inc Incident
	err = h.db.QueryRow(ctx, `
		SELECT i.id, i.title, COALESCE(i.description, ''), i.victim_count,
			   i.hospitalized, i.deaths,
			   COALESCE(TO_CHAR(i.incident_date, 'YYYY-MM-DD'), ''),
			   COALESCE(p.name, ''), COALESCE(d.name, ''),
			   COALESCE(i.location_detail, ''),
			   i.menu_items, i.symptoms,
			   COALESCE(i.source_url, ''), COALESCE(i.source_name, ''),
			   i.verified
		FROM incidents i
		LEFT JOIN provinces p ON i.province_id = p.id
		LEFT JOIN districts d ON i.district_id = d.id
		WHERE i.id = $1
	`, id).Scan(
		&inc.ID, &inc.Title, &inc.Description, &inc.VictimCount,
		&inc.Hospitalized, &inc.Deaths, &inc.IncidentDate,
		&inc.Province, &inc.District, &inc.LocationDetail,
		&inc.MenuItems, &inc.Symptoms,
		&inc.SourceURL, &inc.SourceName, &inc.Verified,
	)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "incident not found"})
	}

	return c.JSON(inc)
}

// GetProvinceStats returns victim stats per province
func (h *Handler) GetProvinceStats(c *fiber.Ctx) error {
	ctx := context.Background()

	rows, err := h.db.Query(ctx, `
		SELECT p.id, p.name, 
			   COUNT(i.id) as incident_count,
			   COALESCE(SUM(i.victim_count), 0) as total_victims,
			   COALESCE(SUM(i.deaths), 0) as total_deaths
		FROM provinces p
		LEFT JOIN incidents i ON i.province_id = p.id
		GROUP BY p.id, p.name
		HAVING COUNT(i.id) > 0
		ORDER BY total_victims DESC
	`)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}
	defer rows.Close()

	type ProvStat struct {
		ID            int    `json:"id"`
		Name          string `json:"name"`
		IncidentCount int    `json:"incident_count"`
		TotalVictims  int    `json:"total_victims"`
		TotalDeaths   int    `json:"total_deaths"`
	}

	var stats []ProvStat
	for rows.Next() {
		var s ProvStat
		rows.Scan(&s.ID, &s.Name, &s.IncidentCount, &s.TotalVictims, &s.TotalDeaths)
		stats = append(stats, s)
	}

	return c.JSON(stats)
}

// GetTimeline returns incidents grouped by month
func (h *Handler) GetTimeline(c *fiber.Ctx) error {
	ctx := context.Background()

	rows, err := h.db.Query(ctx, `
		SELECT TO_CHAR(incident_date, 'YYYY-MM') as month,
			   COUNT(*) as incident_count,
			   COALESCE(SUM(victim_count), 0) as total_victims
		FROM incidents
		WHERE incident_date IS NOT NULL
		GROUP BY month
		ORDER BY month ASC
	`)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}
	defer rows.Close()

	type TimelineEntry struct {
		Month         string `json:"month"`
		IncidentCount int    `json:"incident_count"`
		TotalVictims  int    `json:"total_victims"`
	}

	var timeline []TimelineEntry
	for rows.Next() {
		var t TimelineEntry
		rows.Scan(&t.Month, &t.IncidentCount, &t.TotalVictims)
		timeline = append(timeline, t)
	}

	return c.JSON(timeline)
}

// GetSources returns credible source references
func (h *Handler) GetSources(c *fiber.Ctx) error {
	ctx := context.Background()

	rows, err := h.db.Query(ctx, `
		SELECT id, source_name, COALESCE(source_org, ''), total_victims,
			   COALESCE(TO_CHAR(period_start, 'YYYY-MM-DD'), ''),
			   COALESCE(TO_CHAR(period_end, 'YYYY-MM-DD'), ''),
			   COALESCE(notes, ''), COALESCE(source_url, '')
		FROM aggregate_data
		ORDER BY total_victims DESC
	`)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}
	defer rows.Close()

	type Source struct {
		ID          int    `json:"id"`
		Name        string `json:"name"`
		Org         string `json:"org"`
		Total       int    `json:"total_victims"`
		PeriodStart string `json:"period_start"`
		PeriodEnd   string `json:"period_end"`
		Notes       string `json:"notes"`
		URL         string `json:"source_url"`
	}

	var sources []Source
	for rows.Next() {
		var s Source
		rows.Scan(&s.ID, &s.Name, &s.Org, &s.Total, &s.PeriodStart, &s.PeriodEnd, &s.Notes, &s.URL)
		sources = append(sources, s)
	}

	return c.JSON(sources)
}
