import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.pdf_generator import generate_assessment_pdf

def verify_unicode_fix():
    print("Testing PDF Generation with Unicode characters (e.g., en-dash: –)...")
    
    # Problematic input containing an en-dash
    unicode_assessment = {
        "classification": "Generative AI – Advanced",
        "confidence": 92,
        "rationale": "Testing en-dash – and smart quotes 'test' and em-dash —."
    }
    dummy_messages = [{"role": "user", "content": "Text with \u2013 en-dash."}]
    dummy_feedback = "Good results \u2013 verified."
    dummy_usage = {"input_tokens": 100, "output_tokens": 50, "total_cost": 0.01}
    
    try:
        pdf_bytes = generate_assessment_pdf(
            "Unicode Test – Session", 
            unicode_assessment, 
            9, 
            dummy_feedback, 
            dummy_messages,
            dummy_usage
        )
        print(f"SUCCESS: PDF generated successfully ({len(pdf_bytes)} bytes). Local sanitization worked.")
    except Exception as e:
        print(f"FAILURE: PDF Generation crashed: {e}")

if __name__ == "__main__":
    verify_unicode_fix()
