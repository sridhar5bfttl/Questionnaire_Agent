import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.pdf_generator import generate_assessment_pdf

def verify_premium_features():
    print("Testing PDF Generation...")
    dummy_data = {
        "classification": "GenAI",
        "confidence": 99,
        "rationale": "This is a dummy rationale for verification."
    }
    try:
        pdf_bytes = generate_assessment_pdf("Test Session", dummy_data, audit_score=9)
        print(f"SUCCESS: PDF generated ({len(pdf_bytes)} bytes).")
    except Exception as e:
        print(f"FAILURE: PDF Generation failed: {e}")

    print("Testing Plotly Import...")
    try:
        import plotly.express as px
        print("SUCCESS: Plotly imported correctly.")
    except Exception as e:
        print(f"FAILURE: Plotly import failed: {e}")

if __name__ == "__main__":
    verify_premium_features()
