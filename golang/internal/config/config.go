package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	Auth     AuthConfig
	Export   ExportConfig
}

type ServerConfig struct {
	Port int
	Mode string
}

type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	SSLMode  string
}

type AuthConfig struct {
	APIKey string
}

type ExportConfig struct {
	MaxConcurrent int
	ChunkSize     int
	OutputDir     string
}

func Load() *Config {
	return &Config{
		Server: ServerConfig{
			Port: getEnvAsInt("SERVER_PORT", 8081),
			Mode: getEnv("GIN_MODE", "release"),
		},
		Database: DatabaseConfig{
			Host:     getEnv("DB_HOST", "localhost"),
			Port:     getEnvAsInt("DB_PORT", 5432),
			User:     getEnv("DB_USER", "benchmark"),
			Password: getEnv("DB_PASSWORD", "benchmark123"),
			DBName:   getEnv("DB_NAME", "benchmark"),
			SSLMode:  getEnv("DB_SSLMODE", "disable"),
		},
		Auth: AuthConfig{
			APIKey: getEnv("API_KEY", "benchmark-api-key-2024"),
		},
		Export: ExportConfig{
			MaxConcurrent: getEnvAsInt("EXPORT_MAX_CONCURRENT", 10),
			ChunkSize:     getEnvAsInt("EXPORT_CHUNK_SIZE", 10000),
			OutputDir:     getEnv("EXPORT_OUTPUT_DIR", "/tmp/exports"),
		},
	}
}

func (c *DatabaseConfig) DSN() string {
	return fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		c.Host, c.Port, c.User, c.Password, c.DBName, c.SSLMode,
	)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
