# Use Case Assessment Questionnaire Agent

An agentic AI chat application built with Streamlit and LangChain to help classify business use cases into optimal technical solutions (RPA, ML, DL, NLP, GenAI).

## Project Structure
- `app.py`: Main entry point for the Streamlit application.
- `app/`:
    - `components/`: UI-specific modules (chat interface, buttons).
    - `prompts/`: System instructions and starter prompt templates.
    - `utils/`: State management and LLM orchestration logic.
- `tests/`: Automated test suite for logic verification.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- OpenAI API Key

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your OpenAI API key:
```text
OPENAI_API_KEY=your_api_key_here
```

### 4. Running the Application
```bash
streamlit run app.py
```

### 5. Running Tests
```bash
pytest
```

## Architecture
The application uses a state-machine approach to guide the user through five phases:
1. **Greeting**: Welcome message and starter prompts.
2. **Probing**: Dynamic questioning to gather data details.
3. **Summarization**: Classification of the use case with confidence scores.
4. **Feedback**: Gathering user input on the proposal.
5. **Deep Dive**: Detailed research on a specific selected solution.
