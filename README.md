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

## Running the MVP Pipeline

You can run the end-to-end MVP pipeline from the command line. This workflow accepts local files to process geology shapes, spatial parcels, and deed exports.

```bash
python pipeline.py \
  --geology data/sample_geology.geojson \
  --parcels data/sample_parcels.geojson \
  --deeds data/sample_deeds.csv
```

### Implementation Notes
This MVP narrows the scope to a working end-to-end data funnel.
* **Fully Working:** The pipeline successfully parses local GeoJSON files for geology and parcels, runs a spatial intersection to isolate target parcels, loads county recorder deed exports (CSV), heuristically classifies severance and lease signals from the text, and calculates a ranked lead score.
* **County Specific:** The current structure uses an offline CSV import path (`ingestion/offline_recorder.py`) for deed documents. Because many county portals actively block automated scraping (e.g., Tyler/Granicus captchas), offline export ingestion is the most reliable MVP data path. The `county_scraper.py` remains in the framework but is mostly a stub for when a county provides an API without firewalls.
* **Future Work:** Integrating SQLAlchemy/GeoAlchemy2 directly to execute `find_intersections_postgis()` instead of using the in-memory GeoPandas fallback. Further LLM fine-tuning can be added if the strict deterministic heuristics fail on older, complex cursive deeds.

## Frontend Integration

The backend is designed to serve a simple Next.js (React) dashboard. The dashboard should use Mapbox GL JS or Leaflet to visualize the `geom` data of high-value anomalies outputted into the `leads` table.
