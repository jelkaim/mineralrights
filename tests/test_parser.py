import pytest
from parser.document_analyzer import DocumentAnalyzer

def test_document_analyzer_init():
    # Will fail if API key is invalid, so we mock or don't make requests
    analyzer = DocumentAnalyzer(openai_api_key="test_key")
    assert analyzer.openai_client.api_key == "test_key"

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
