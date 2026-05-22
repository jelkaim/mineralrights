# Subsurface Arbitrage Engine (SAE)

The **Subsurface Arbitrage Engine (SAE)** is an automated application designed to discover severed mineral rights sitting above high-value geological formations. It achieves this by cross-referencing public county land records with federal geological databases.

## System Architecture

The application is composed of several modular Python backend services:

1. **`/ingestion`**: Data ingestion pipeline to fetch USGS Shapefiles and web scrape county land records portals.
2. **`/spatial`**: GIS mapping engine utilizing GeoPandas and PostGIS to find intersections between surface parcels and subsurface mineral zones.
3. **`/parser`**: Intelligent document parser utilizing Tesseract OCR and OpenAI's LLMs to extract entities from legal property deeds.
4. **`/scoring`**: Algorithmic scoring engine that ranks leads based on distance to infrastructure, heir fractionalization, and competitive density.
5. **`/database`**: Database schema designed for PostgreSQL with PostGIS for advanced spatial queries.

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 14+** with **PostGIS 3+** enabled
- **Docker** (optional, for containerized deployments)

## Setup Instructions

### 1. Database Configuration (PostGIS)

Ensure you have a PostgreSQL instance running. Create a new database and apply the schema:

```bash
createdb sae_db
psql -d sae_db -f database/schema.sql
```

This script automatically creates the `postgis` extension and initializes tables with proper geometry columns.

### 2. Environment Variables

Create a `.env` file in the root directory and configure the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sae_db
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
playwright install chromium
```

> **Note**: For OCR capabilities, you must also install Tesseract on your system (e.g., `apt-get install tesseract-ocr` on Ubuntu, or `brew install tesseract` on macOS).

## Running the Pipeline

Currently, the modules are designed as a framework. You can run them independently or integrate them into an overarching pipeline script.

Example running the spatial intersection engine (requires sample data):
```bash
python spatial/intersection_engine.py
```

## Frontend Integration

The backend is designed to serve a simple Next.js (React) dashboard. The dashboard should use Mapbox GL JS or Leaflet to visualize the `geom` data of high-value anomalies outputted into the `leads` table.
