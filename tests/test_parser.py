import pytest
from parser.document_analyzer import DocumentAnalyzer

def test_document_analyzer_init():
    # Will fail if API key is invalid, so we mock or don't make requests
    analyzer = DocumentAnalyzer(openai_api_key="test_key")
    assert analyzer.openai_client.api_key == "test_key"
