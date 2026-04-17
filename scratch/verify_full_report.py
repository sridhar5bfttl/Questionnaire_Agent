import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.pdf_generator import generate_assessment_pdf

def verify_full_pdf():
    print("Testing Full Consolidated PDF Generation...")
    dummy_assessment = {
        "classification": "Generative AI",
        "confidence": 95,
        "rationale": "Deep learning rationale for a complex enterprise use case involving RAG and Agentic workflows."
    }
    dummy_messages = [
        {"role": "user", "content": "I want to automate my invoicing process."},
        {"role": "assistant", "content": "Tell me more about the data format."},
        {"role": "user", "content": "They are mostly unstructured PDFs."},
        {"role": "assistant", "content": "Based on that, I recommend a GenAI solution."}
    ]
    dummy_feedback = "The conversation was very helpful and the technical advice was spot on."
    
    try:
        pdf_bytes = generate_assessment_pdf(
            "Test Strategy Session", 
            dummy_assessment, 
            9, 
            dummy_feedback, 
            dummy_messages
        )
        print(f"SUCCESS: Consolidated PDF generated ({len(pdf_bytes)} bytes).")
    except Exception as e:
        print(f"FAILURE: Consolidated PDF Generation failed: {e}")

if __name__ == "__main__":
    verify_full_pdf()
