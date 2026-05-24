import pytest
from parser.document_analyzer import DocumentAnalyzer

def test_document_analyzer_init():
    # Will fail if API key is invalid, so we mock or don't make requests
    analyzer = DocumentAnalyzer(openai_api_key="test_key")
    assert analyzer.openai_client.api_key == "test_key"

def test_extract_text_from_pdf():
    analyzer = DocumentAnalyzer()
    text = analyzer.extract_text_from_pdf("data/sample_deed.pdf")
    # Tesseract might output some weird spacing, but it should contain our key words
    assert "WARRANTY DEED" in text
    assert "reserves all oil" in text

def test_heuristic_parsing_severance():
    analyzer = DocumentAnalyzer()
    text = "This is a WARRANTY DEED. Grantor hereby reserves all oil, gas, and mineral rights."
    result = analyzer.parse_legal_text(text)
    assert result["is_mineral_severed"] == True
    assert result["is_lease"] == False

def test_heuristic_parsing_lease():
    analyzer = DocumentAnalyzer()
    text = "MEMORANDUM OF LEASE between party A and party B."
    result = analyzer.parse_legal_text(text)
    assert result["is_mineral_severed"] == False
    assert result["is_lease"] == True

def test_audit_lease_history():
    analyzer = DocumentAnalyzer()

    # 1. Lease occurs after severance -> active lease
    history_active = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": "1954-11-12"},
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True, "Date": "2010-05-01"}
    ]
    assert analyzer.audit_lease_history(history_active) == True

    # 2. No lease -> no active lease
    history_no_lease = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": "1954-11-12"}
    ]
    assert analyzer.audit_lease_history(history_no_lease) == False

    # 3. Lease is terminated/released later -> no active lease
    history_released = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": "1954-11-12"},
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True, "Date": "2010-05-01"},
        {"DocumentType": "RELEASE OF LEASE", "is_release": True, "Date": "2015-05-01"}
    ]
    assert analyzer.audit_lease_history(history_released) == False

    # 4. Lease occurs BEFORE severance -> should not trigger
    history_prior_lease = [
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True, "Date": "1920-05-01"},
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": "1954-11-12"}
    ]
    assert analyzer.audit_lease_history(history_prior_lease) == False

    # 5. Missing or unparsable dates should be sorted to the end (treated as datetime.max)
    # This prevents them from falsely acting as an early trigger.
    history_missing_date = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": "1954-11-12"},
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True, "Date": "Bad-Date-Format"}
    ]
    # Because it is treated as datetime.max, it occurs "after" 1954, so it flags active
    assert analyzer.audit_lease_history(history_missing_date) == True

    # 6. Severance with missing date but release with missing date
    # (Both evaluate at datetime.max, release should clear it based on order of occurrence)
    history_missing_dates_release = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": ""},
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True, "Date": "Bad-Date"},
        {"DocumentType": "RELEASE OF LEASE", "is_release": True, "Date": None}
    ]
    assert analyzer.audit_lease_history(history_missing_dates_release) == False

    # 7. Undated severance followed by a properly dated lease
    # Even though severance_date is datetime.max, the dated lease should trigger as active.
    history_undated_severance_dated_lease = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True, "Date": ""},
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True, "Date": "2010-05-01"}
    ]
    assert analyzer.audit_lease_history(history_undated_severance_dated_lease) == True
