from fpdf import FPDF
import datetime
import os

class TechnicalAssessmentPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(0, 123, 255) # Visionary Blue
        self.cell(0, 10, 'Vantage Point AI: Strategic Session Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Strategic Assessment - Confidential', 0, 0, 'C')

def sanitize_text(text):
    """
    Remove or replace non-latin-1 characters to prevent FPDF crashes.
    """
    if not text:
        return ""
    # Map common problematic unicode characters to latin-1 equivalents
    replacements = {
        '\u2013': '-', # en-dash
        '\u2014': '--', # em-dash
        '\u2018': "'", # left single quote
        '\u2019': "'", # right single quote
        '\u201c': '"', # left double quote
        '\u201d': '"', # right double quote
        '\u2022': '*', # bullet point
        '\u2026': '...', # ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Final fallback: encode to latin-1 and replace unknown with '?'
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_assessment_pdf(session_title, assessment_data, audit_score, audit_feedback, messages, usage_data):
    """
    Generate a comprehensive professional PDF Session Report including resource usage.
    usage_data: dict with input_tokens, output_tokens, total_cost
    """
    pdf = TechnicalAssessmentPDF()
    pdf.add_page()
    
    # --- SECTION 1: REPORT SUMMARY ---
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(0)
    pdf.cell(0, 10, f"Project: {sanitize_text(session_title)}", 0, 1)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 8, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(5)
    
    # Executive Verdict Box
    pdf.set_fill_color(240, 248, 255)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f"Recommended Architecture: {sanitize_text(assessment_data.get('classification', 'N/A'))}", 1, 1, 'L', fill=True)
    pdf.cell(0, 10, f"Analysis Confidence: {assessment_data.get('confidence', 0)}%", 1, 1, 'L', fill=True)
    pdf.cell(0, 10, f"Quality Audit Score: {audit_score}/10", 1, 1, 'L', fill=True)
    pdf.ln(10)

    # --- SECTION 2: RESOURCE UTILIZATION (NEW) ---
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, "Resource & Cost Utilization (GPT-5.1):", 0, 1)
    pdf.set_font('helvetica', '', 11)
    pdf.cell(0, 7, f"Input Volume: {usage_data.get('input_tokens', 0):,} tokens", 0, 1)
    pdf.cell(0, 7, f"Output Volume: {usage_data.get('output_tokens', 0):,} tokens", 0, 1)
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 7, f"Estimated Session Cost: ${usage_data.get('total_cost', 0.0):.6f}", 0, 1)
    pdf.ln(10)

    # --- SECTION 3: AUDIT VERDICT ---
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, "Governance & Audit Feedback:", 0, 1)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 7, sanitize_text(audit_feedback) if audit_feedback else "No specific audit feedback recorded.")
    pdf.ln(10)

    # --- SECTION 4: TECHNICAL RATIONALE ---
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, "Technical Solution Blueprint:", 0, 1)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 7, sanitize_text(assessment_data.get('rationale', 'No rationale provided.')))
    pdf.ln(10)

    # --- SECTION 5: CONVERSATION TRANSCRIPT ---
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "Interaction History", 0, 1, 'C')
    pdf.ln(5)
    
    for msg in messages:
        role = "USER" if msg['role'] == 'user' else "VANTAGE POINT AI"
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(100)
        pdf.cell(0, 6, f"{role}:", 0, 1)
        
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(0)
        pdf.multi_cell(0, 6, sanitize_text(msg['content']))
        pdf.ln(3)

    return pdf.output()
