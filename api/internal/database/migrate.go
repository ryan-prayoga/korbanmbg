package database

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

func Migrate(db *pgxpool.Pool) error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS provinces (
			id SERIAL PRIMARY KEY,
			name VARCHAR(100) NOT NULL UNIQUE,
			code VARCHAR(10)
		)`,

		`CREATE TABLE IF NOT EXISTS districts (
			id SERIAL PRIMARY KEY,
			name VARCHAR(100) NOT NULL,
			province_id INTEGER REFERENCES provinces(id),
			UNIQUE(name, province_id)
		)`,

		`CREATE TABLE IF NOT EXISTS incidents (
			id SERIAL PRIMARY KEY,
			title TEXT NOT NULL,
			description TEXT,
			victim_count INTEGER DEFAULT 0,
			hospitalized INTEGER DEFAULT 0,
			deaths INTEGER DEFAULT 0,
			incident_date DATE,
			province_id INTEGER REFERENCES provinces(id),
			district_id INTEGER REFERENCES districts(id),
			location_detail TEXT,
			menu_items TEXT[],
			symptoms TEXT[],
			source_url TEXT,
			source_name VARCHAR(100),
			verified BOOLEAN DEFAULT false,
			created_at TIMESTAMP DEFAULT NOW(),
			updated_at TIMESTAMP DEFAULT NOW()
		)`,

		`CREATE TABLE IF NOT EXISTS aggregate_data (
			id SERIAL PRIMARY KEY,
			source_name VARCHAR(200) NOT NULL,
			source_org VARCHAR(200),
			total_victims INTEGER NOT NULL,
			period_start DATE,
			period_end DATE,
			notes TEXT,
			source_url TEXT,
			created_at TIMESTAMP DEFAULT NOW()
		)`,

		`CREATE INDEX IF NOT EXISTS idx_incidents_province ON incidents(province_id)`,
		`CREATE INDEX IF NOT EXISTS idx_incidents_district ON incidents(district_id)`,
		`CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents(incident_date)`,
		`CREATE INDEX IF NOT EXISTS idx_incidents_verified ON incidents(verified)`,
	}

	for _, q := range queries {
		if _, err := db.Exec(context.Background(), q); err != nil {
			return fmt.Errorf("migration failed: %w\nQuery: %s", err, q)
		}
	}

	return nil
}
