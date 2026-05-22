import pytest
from ingestion.usgs_fetcher import USGSDataFetcher
from ingestion.county_scraper import CountyRecorderScraper

def test_usgs_fetcher_init():
    fetcher = USGSDataFetcher(db_connection_string="test_db")
    assert fetcher.db_connection_string == "test_db"

def test_county_scraper_init():
    scraper = CountyRecorderScraper(headless=True)
    assert scraper.headless == True
    assert "mineral deed" in scraper.target_keywords
