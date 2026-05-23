import os
import json
import pytesseract
from pdf2image import convert_from_path
import openai
from typing import Dict, Any, Optional, List

class DocumentAnalyzer:
    """
    Intelligent Document Parser using OCR and LLM for legal analytics.
    """
    def __init__(self, openai_api_key: Optional[str] = None):
        # We wrap client initialization to not fail if OPENAI_API_KEY is not set
        # This allows offline MVP and heuristics to run without keys.
        self.api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.openai_client = None
        if self.api_key:
            self.openai_client = openai.OpenAI(api_key=self.api_key)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Uses Tesseract OCR to read text from scanned PDF deeds.
        """
        print(f"Running OCR on {pdf_path}...")
        try:
            # Convert PDF to list of images
            images = convert_from_path(pdf_path)

            full_text = ""
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                full_text += f"\n--- Page {i+1} ---\n{text}"

            return full_text
        except Exception as e:
            print(f"OCR failed for {pdf_path}: {e}")
            return ""

    def parse_legal_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Uses deterministic heuristics first, falling back to an LLM if needed,
        to parse OCR text. Extracts grantor/grantee, severance boolean, etc.
        """
        if not raw_text.strip():
            return {}

        # 1. Deterministic Heuristics First
        import re
        text_lower = raw_text.lower()

        # Look for severance indicators
        severance_keywords = ["reserves all oil, gas, and mineral rights", "excepting and reserving", "mineral deed", "severed"]
        is_severed = any(keyword in text_lower for keyword in severance_keywords)

        # Look for lease indicators
        lease_keywords = ["memorandum of lease", "oil and gas lease", "lessee"]
        is_lease = any(keyword in text_lower for keyword in lease_keywords)

        # Look for release indicators
        release_keywords = ["release of lease", "release of oil and gas lease", "surrender of lease"]
        is_release = any(keyword in text_lower for keyword in release_keywords)

        # Basic Grantor/Grantee extraction (very naive fallback)
        grantor_match = re.search(r'(between|from)\s+([A-Z\s,]+)\s+(as grantor|party of the first part)', raw_text, re.IGNORECASE)
        grantee_match = re.search(r'(to)\s+([A-Z\s,]+)\s+(as grantee|party of the second part)', raw_text, re.IGNORECASE)

        parsed_data = {
            "grantor_name": grantor_match.group(2).strip() if grantor_match else "Unknown",
            "grantee_name": grantee_match.group(2).strip() if grantee_match else "Unknown",
            "is_mineral_severed": is_severed,
            "is_lease": is_lease,
            "is_release": is_release,
            "reservation_percentage": 0.0, # Hard to get deterministically without complex NLP
            "legal_description_metes_and_bounds": "See Document"
        }

        # 2. LLM Fallback (Only if key fields are missing or if we want deeper analysis)
        # For MVP, we will stick to the heuristics to save tokens/time if it found a severance,
        # but here is the LLM logic using the modern SDK if we wanted to enforce it.

        if not is_severed and not is_lease and self.openai_client:
            # print("Falling back to LLM extraction...")
            schema = {
                "type": "object",
                "properties": {
                    "grantor_name": {"type": "string"},
                    "grantee_name": {"type": "string"},
                    "is_mineral_severed": {"type": "boolean"},
                    "reservation_percentage": {"type": "number"},
                    "legal_description_metes_and_bounds": {"type": "string"},
                    "is_lease": {"type": "boolean"}
                },
                "required": [
                    "grantor_name", "grantee_name", "is_mineral_severed",
                    "reservation_percentage", "legal_description_metes_and_bounds",
                    "is_lease"
                ]
            }

            prompt = (
                "Analyze the following legal property deed and extract the requested entities.\n"
                "If a field is not found or ambiguous, provide null or a sensible default "
                "(e.g. 0.0 for percentage, false for booleans).\n\n"
                f"TEXT:\n{raw_text[:4000]}"
            )

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {"role": "system", "content": "You are a legal document parsing assistant. Respond only in JSON matching the schema."},
                        {"role": "user", "content": prompt}
                    ],
                    tools=[{
                        "type": "function",
                        "function": {
                            "name": "extract_deed_data",
                            "parameters": schema
                        }
                    }],
                    tool_choice={"type": "function", "function": {"name": "extract_deed_data"}}
                )

                function_args = response.choices[0].message.tool_calls[0].function.arguments
                parsed_data = json.loads(function_args)
            except Exception as e:
                print(f"LLM Parsing failed: {e}")

        return parsed_data

    def audit_lease_history(self, deed_history: List[Dict[str, Any]]) -> bool:
        """
        Audits later records for lease indicators.
        Returns True if an active lease is found AFTER the original severance,
        and has not been subsequently released/terminated.
        """
        from datetime import datetime

        # Helper to parse dates robustly
        def parse_date(date_str):
            if not date_str:
                return datetime.max
            try:
                # Basic ISO format YYYY-MM-DD
                return datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                # If date is unparsable, treat it as datetime.max so it gets sorted
                # to the END of the chain and doesn't falsely act as an early trigger.
                return datetime.max

        # Sort deed history chronologically
        sorted_history = sorted(deed_history, key=lambda x: parse_date(x.get("Date")))

        # Find the earliest severance date
        severance_date = datetime.max
        for doc in sorted_history:
            if doc.get("is_mineral_severed"):
                doc_date = parse_date(doc.get("Date"))
                # If we have a severance with no date, we still need to track that it happened.
                if doc_date < severance_date:
                    severance_date = doc_date

        # If no severance, it doesn't matter (we aren't tracking a severed lead)
        # Note: A severance with NO date will still have a severance_date of datetime.max
        # To ensure we still audit the remainder of the chain if a severance occurred with no date,
        # we check the boolean flag, not just the date variable.
        has_severance = any(doc.get("is_mineral_severed") for doc in sorted_history)
        if not has_severance:
            return False

        has_active_lease = False

        # Audit forward from the severance
        for doc in sorted_history:
            doc_date = parse_date(doc.get("Date"))

            # Only care about documents executed after or on the day of severance.
            # If the severance date was unparsable (datetime.max), we still evaluate the lease docs
            # that come after it in the sorted list (which will also be datetime.max).
            if doc_date >= severance_date:
                doc_type = str(doc.get("DocumentType", "")).upper()

                # Check for a release first to clear the active lease flag
                if doc.get("is_release") or "RELEASE" in doc_type:
                    has_active_lease = False
                # If it's a lease, mark it active
                elif "LEASE" in doc_type or doc.get("is_lease"):
                    has_active_lease = True

        return has_active_lease

if __name__ == "__main__":
    # Example usage:
    # analyzer = DocumentAnalyzer()
    # text = analyzer.extract_text_from_pdf("sample_deed.pdf")
    # result = analyzer.parse_legal_text(text)
    # print(result)
    pass
