-- Enable PostGIS extension for spatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table for USGS/State Geological Data (Subsurface High-Value Zones)
CREATE TABLE IF NOT EXISTS geological_zones (
    id SERIAL PRIMARY KEY,
    zone_name VARCHAR(255) NOT NULL,
    formation_type VARCHAR(100), -- e.g., 'Shale Play', 'Lithium Brine', 'Oil Field'
    probability_score FLOAT CHECK (probability_score >= 0.0 AND probability_score <= 1.0),
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial index for geological zones
CREATE INDEX IF NOT EXISTS idx_geological_zones_geom
ON geological_zones USING GIST(geom);


-- Table for County Parcel Data (Surface Records)
CREATE TABLE IF NOT EXISTS parcels (
    id SERIAL PRIMARY KEY,
    county_fips VARCHAR(5) NOT NULL,
    parcel_id VARCHAR(100) NOT NULL,
    owner_name VARCHAR(255),
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    acreage FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(county_fips, parcel_id)
);

-- Spatial index for parcels
CREATE INDEX IF NOT EXISTS idx_parcels_geom
ON parcels USING GIST(geom);


-- Table for OCR/LLM parsed Deeds and Legal Documents
CREATE TABLE IF NOT EXISTS deeds (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER REFERENCES parcels(id) ON DELETE CASCADE,
    document_id VARCHAR(255) NOT NULL, -- e.g., County Recorder Instrument Number
    recording_date DATE,
    grantor_name TEXT,
    grantee_name TEXT,
    is_mineral_severed BOOLEAN DEFAULT FALSE,
    reservation_percentage FLOAT,
    legal_description_metes_and_bounds TEXT,
    has_active_lease BOOLEAN DEFAULT FALSE,
    ocr_confidence FLOAT,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table for Lead Scoring & Anomalies (The Arbitrage Output)
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    parcel_id INTEGER REFERENCES parcels(id) ON DELETE CASCADE,
    zone_id INTEGER REFERENCES geological_zones(id) ON DELETE SET NULL,
    total_score FLOAT, -- Algorithmic score
    distance_to_active_infrastructure FLOAT, -- Meters/Miles to active well/mine
    fractionalization_risk_score INTEGER, -- Based on number of heirs
    competitive_density_score FLOAT, -- Corporate mailers/leases nearby
    is_high_value_anomaly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for querying high value leads quickly
CREATE INDEX IF NOT EXISTS idx_leads_anomaly
ON leads(is_high_value_anomaly);
