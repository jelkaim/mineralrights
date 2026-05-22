import os
import json
import pytesseract
from pdf2image import convert_from_path
import openai
from typing import Dict, Any, Optional

class DocumentAnalyzer:
    """
    Intelligent Document Parser using OCR and LLM for legal analytics.
    """
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key or os.environ.get("OPENAI_API_KEY"))

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
        Uses an LLM with strict JSON schema outputs to parse the OCR text.
        Extracts grantor/grantee, mineral severance boolean, reservation percentage,
        legal description, and active lease boolean.
        """
        if not raw_text.strip():
            return {}

        schema = {
            "type": "object",
            "properties": {
                "grantor_name": {"type": "string"},
                "grantee_name": {"type": "string"},
                "is_mineral_severed": {"type": "boolean"},
                "reservation_percentage": {"type": "number"},
                "legal_description_metes_and_bounds": {"type": "string"},
                "has_active_lease": {"type": "boolean"}
            },
            "required": [
                "grantor_name", "grantee_name", "is_mineral_severed",
                "reservation_percentage", "legal_description_metes_and_bounds",
                "has_active_lease"
            ]
        }

        prompt = (
            "Analyze the following legal property deed and extract the requested entities.\n"
            "If a field is not found or ambiguous, provide null or a sensible default "
            "(e.g. 0.0 for percentage, false for booleans).\n\n"
            f"TEXT:\n{raw_text[:4000]}" # Truncating for context limits in this example
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-1106-preview", # or similar model supporting JSON mode
                messages=[
                    {"role": "system", "content": "You are a legal document parsing assistant. Respond only in JSON matching the schema."},
                    {"role": "user", "content": prompt}
                ],
                functions=[{"name": "extract_deed_data", "parameters": schema}],
                function_call={"name": "extract_deed_data"}
            )

            # Parse the function arguments as JSON
            function_args = response.choices[0].message.function_call.arguments
            parsed_data = json.loads(function_args)
            return parsed_data

        except Exception as e:
            print(f"LLM Parsing failed: {e}")
            return {}

if __name__ == "__main__":
    # Example usage:
    # analyzer = DocumentAnalyzer()
    # text = analyzer.extract_text_from_pdf("sample_deed.pdf")
    # result = analyzer.parse_legal_text(text)
    # print(result)
    pass
