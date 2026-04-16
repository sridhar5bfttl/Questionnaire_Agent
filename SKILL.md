# Streamlit Chatbot Architecture UI & Agent Logic

This document defines the skills and implementation patterns required to build the Use Case Assessment Chat Agent as per `project.md`.

## 1. Streamlit UI Architecture
- **Chat Interface**: Utilize Streamlit's native `st.chat_message` and `st.chat_input` for the chat interface.
- **Session State**: Utilize `st.session_state` extensively to persist chat history, current phase of conversation (Greeting -> Probing -> Summary -> Feedback -> Deep Dive), and collected user data.
- **Starter Prompts**: Use `st.button` or a set of clickable elements (e.g. `st.columns` with buttons) in the initial greeting to render the 5 starter prompts. When a user clicks a button, the text should be appended to the chat and sent to the LLM agent.

## 2. Conversational Flow & State Management
The agent operates in defined phases/states to guide the conversation effectively:
1. **State: Greeting**: 
   - Display a welcome message.
   - Show 5 starter prompts.
   - Wait for user input or starter prompt selection.
2. **State: Probing**: 
   - Analyze the initial user input.
   - Dynamically generate probing questions (data type, size, expected outputs) to determine the nature of the use case.
3. **State: Confirmation & Summarization**:
   - Rephrase the user’s use case to ensure understanding.
   - Classify into categories: RPA, ML, DL, NLP, GenAI (MCP, RAG, Agentic AI, etc.).
   - Calculate and display a confidence score for each possible solution.
4. **State: Feedback & Export**:
   - Ask for user feedback on the summary.
   - Ask if the user wants to receive this summary via email.
5. **State: Deep Dive / Research**:
   - Prompt the user to select one of the suggested solutions for further research.
   - Based on selection (e.g., GenAI), ask specialized, deep-dive questions.

## 3. Core Agent Skills
- **Rephrasing & Confirmation**: The ability to parse multi-turn context and extract the core intent, playing it back to the user to get a "yes/no" confirmation.
- **Zero-Shot/Few-Shot Classification**: Using a prompt with definitions for RPA, ML, DL, NLP, and GenAI sub-architectures to classify the gathered requirements.
- **Dynamic Question Generation**: The agent must identify missing pieces of information (e.g., "The user mentioned classifying text, but didn't mention where the text comes from or how much data exists") and synthesize natural-sounding questions.
- **Confidence Scoring**: Generating a rationale and a probabilistic score representing how well the use case aligns with a specific technology stack.

## 4. Directory Structure
For building this app, we organize the codebase as follows:
- `/app/`: Main application source code
  - `/app/components/`: Streamlit UI specific custom layouts (e.g., starter prompts UI).
  - `/app/utils/`: Helper functions (LLM integrations, email sending utilities).
  - `/app/prompts/`: Template prompts for system instructions (e.g., `system_prompt_classifier.txt`).
- `/pages/`: For multi-page configuration if we break out the deep-dive research into a separate view.
- `/assets/`: Static files like CSS for custom branding, images.
- `/data/`: Storing log chats or mock example data locally if database isn't attached yet.

## 5. Technology Stack Recommendations
- **Frontend/Framework**: `streamlit`
- **LLM Orchestration**: `langchain` or directly using `openai`/`anthropic` API wrappers depending on preference for lightweight vs robust frameworks.
- **Logging**: Maintain structured logs of interactions to improve classification accuracy over time.

## 6. Testing the Solution
- **Unit Testing**: Create modular tests for individual utility functions in `/app/utils/` (e.g., test LLM output parsing, test state transition logic). Use frameworks like `pytest`.
- **Integration Testing**: Test the complete flow of the agent from Greeting -> Probing -> Summarization using mocked LLM responses to ensure data is passed correctly between states.
- **UI/E2E Testing**: Use Streamlit's built-in testing framework (`AppTest`) or tools like Playwright to simulate user interactions ensuring that buttons execute the expected logic and chat inputs update the state properly.

## 7. Documentation Instructions
- **Inline Documentation**: Ensure all utility functions and classes have descriptive docstrings explaining parameters, return values, and expected behavior.
- **Code Comments**: Add structured comments for complex state transitions to make the flow easy to trace.
- **README Update**: Maintain an updated `README.md` detailing the setup instructions, architecture summary, and how to run tests. Include environment variables needed for LLM access.
- **Dependency Management**: Ensure all new packages and dependencies used during development are explicitly added to `requirements.txt` for reproducibility. 
    - **Verification**: Always cross-reference imported modules (e.g., `langchain_openai`) with their corresponding installable package names (e.g., `langchain-openai`) in `requirements.txt`.
    - **Minimalism**: Include only necessary packages, but ensure all sub-integrations (like `langchain-openai` or `langchain-anthropic`) are listed separately.

## 8. Mandatory Development Workflow
To maintain project integrity, every code change **MUST** follow this exact sequence:

1. **Dependency Sync**: If the change requires a new library, add it to `requirements.txt` **BEFORE** writing the implementation code. Always verify the package name vs. the import name.
2. **Implementation**: Modify or create the source code or **prompt templates** in the appropriate `/app/` subdirectory. Follow the state management rules defined in Section 2.
3. **Test Preparation**: Update or create corresponding test cases in `/tests/`. If a new utility is added or a prompt logic changes, a unit/integration test is mandatory.
4. **Verification**: Run `pytest tests/` and manually verify the Streamlit UI behavior. For prompt changes, verify the output quality and tone. Fix any regressions immediately.
5. **Documentation**: 
    - Add/update docstrings and comments in the code.
    - If the change affects setup or architecture, update `README.md`.
    - If new implementation patterns are established, update this `SKILL.md` file.
6. **Task Update**: Finalize the task in `task.md` only after all above steps are completed.

