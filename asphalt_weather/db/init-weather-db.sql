CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE weather_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    reliability_weight NUMERIC(3,2) DEFAULT 1.0
);

CREATE TABLE raw_forecasts (
    id SERIAL PRIMARY KEY,
    section_id INT NOT NULL,
    provider_id INT REFERENCES weather_providers(id),
    forecast_for_time TIMESTAMP NOT NULL,
    temp_c NUMERIC(5,2) NOT NULL,
    rain_probability NUMERIC(5,2) NOT NULL,
    precipitation_mm NUMERIC(6,2) DEFAULT 0,
    wind_speed_ms NUMERIC(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE aggregated_forecasts (
    id SERIAL PRIMARY KEY,
    section_id INT NOT NULL,
    forecast_for_time TIMESTAMP NOT NULL,
    aggr_temp_c NUMERIC(5,2) NOT NULL,
    aggr_rain_probability NUMERIC(5,2) NOT NULL,
    is_green_window BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_section_time ON raw_forecasts(section_id, forecast_for_time);
CREATE INDEX idx_aggr_section_time ON aggregated_forecasts(section_id, forecast_for_time);
