CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE truck_status_enum AS ENUM (
    'IDLE',
    'LOADING',
    'IN_TRANSIT',
    'UNLOADING',
    'RETURNING',
    'MAINTENANCE'
);

CREATE TYPE order_status_enum AS ENUM (
    'PENDING',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED',
    'REDIRECTED'
);

CREATE TYPE order_type_enum AS ENUM (
    'ASPHALT', 
    'TECHNICAL_FLUIDS'
);

CREATE TABLE plants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity_per_hour NUMERIC(6,2) NOT NULL,
    bunker_capacity NUMERIC(6,2) NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    start_location GEOMETRY(Point, 4326) NOT NULL,
    end_location GEOMETRY(Point, 4326) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sections_start_loc ON sections USING GIST (start_location);
CREATE INDEX idx_sections_end_loc ON sections USING GIST (end_location);

CREATE TABLE trucks (
    id SERIAL PRIMARY KEY,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    capacity_tons NUMERIC(5,2) NOT NULL DEFAULT 20.0,
    status truck_status_enum DEFAULT 'IDLE',
    home_plant_id INT REFERENCES plants(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    type order_type_enum DEFAULT 'ASPHALT',
    plant_id INT REFERENCES plants(id),
    section_id INT REFERENCES sections(id),
    ordered_tons NUMERIC(8,2) NOT NULL,
    delivered_tons NUMERIC(8,2) DEFAULT 0,
    status order_status_enum DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    truck_id INT REFERENCES trucks(id),
    dispatched_at TIMESTAMP,
    initial_temp_c NUMERIC(5,2),
    redirected_to_section_id INT REFERENCES sections(id),
    completed_at TIMESTAMP
);

CREATE TABLE maintenance_tasks (
    id SERIAL PRIMARY KEY,
    truck_id INT REFERENCES trucks(id),
    reason VARCHAR(255) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_plants_location ON plants USING GIST (location);
CREATE INDEX idx_sections_location ON sections USING GIST (center_location);
CREATE INDEX idx_trips_order_id ON trips(order_id);
CREATE INDEX idx_trucks_status ON trucks(status);
