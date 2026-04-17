import sys
import os
import json
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.auditor_agent import AuditorAgent

def verify_extraction():
    auditor = AuditorAgent()
    sample_summary = """
    Based on our conversation, I recommend implementing a Generative AI (GenAI) solution using RAG (Retrieval Augmented Generation).
    
    Technical Category: GenAI
    Confidence Score: 95%
    
    Rationale: The user needs to query high volumes of unstructured PDF invoices and retrieve specific semantic insights. Generative AI with a vector database is the most scalable approach for this natural language requirement.
    """
    
    print("Testing extraction logic...")
    classification, confidence, rationale = auditor.extract_recommendation(sample_summary)
    
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence}")
    print(f"Rationale: {rationale}")
    
    assert classification in ["GenAI", "RPA", "ML", "DL", "NLP"]
    assert isinstance(confidence, int)
    assert len(rationale) > 10
    print("SUCCESS: Extraction logic verified.")

if __name__ == "__main__":
    verify_extraction()
