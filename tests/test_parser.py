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
    history = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True},
        {"DocumentType": "OIL AND GAS LEASE", "is_lease": True}
    ]
    assert analyzer.audit_lease_history(history) == True

    history_no_lease = [
        {"DocumentType": "WARRANTY DEED", "is_mineral_severed": True}
    ]
    assert analyzer.audit_lease_history(history_no_lease) == False
