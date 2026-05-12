package main

import (
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/joho/godotenv"
	"github.com/ryan-prayoga/korbanmbg-api/internal/database"
	"github.com/ryan-prayoga/korbanmbg-api/internal/handler"
)

func main() {
	godotenv.Load()

	// Connect to database
	db, err := database.Connect()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Run migrations
	if err := database.Migrate(db); err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	app := fiber.New(fiber.Config{
		AppName: "KorbanMBG API",
	})

	// Middleware
	app.Use(logger.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins: "*",
		AllowHeaders: "Origin, Content-Type, Accept, Authorization",
	}))

	// Health check
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "ok"})
	})

	// API routes
	api := app.Group("/api/v1")

	h := handler.New(db)

	// Public endpoints
	api.Get("/stats", h.GetStats)
	api.Get("/incidents", h.GetIncidents)
	api.Get("/incidents/:id", h.GetIncidentByID)
	api.Get("/provinces", h.GetProvinceStats)
	api.Get("/timeline", h.GetTimeline)
	api.Get("/sources", h.GetSources)

	// Get port
	port := os.Getenv("PORT")
	if port == "" {
		port = "8090"
	}

	log.Printf("Server starting on :%s", port)
	log.Fatal(app.Listen(":" + port))
}
