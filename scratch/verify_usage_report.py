import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.pdf_generator import generate_assessment_pdf

def verify_full_usage_pdf():
    print("Testing Full Consolidated PDF with Resource Usage...")
    dummy_assessment = {
        "classification": "Machine Learning",
        "confidence": 88,
        "rationale": "Testing the inclusion of resource metrics in the formal report."
    }
    dummy_messages = [{"role": "user", "content": "Test case for resources."}]
    dummy_feedback = "Looks good."
    dummy_usage = {
        "input_tokens": 1250,
        "output_tokens": 850,
        "total_cost": 0.000155
    }
    
    try:
        pdf_bytes = generate_assessment_pdf(
            "Resource Tracking Session", 
            dummy_assessment, 
            10, 
            dummy_feedback, 
            dummy_messages,
            dummy_usage
        )
        print(f"SUCCESS: PDF with Resource Usage generated ({len(pdf_bytes)} bytes).")
    except Exception as e:
        print(f"FAILURE: Generation failed: {e}")

if __name__ == "__main__":
    verify_full_usage_pdf()
