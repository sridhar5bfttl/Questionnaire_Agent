project : Use Case assessment with questionnaire
Description: The aim of this project is to classify use cases based on a sequence of questions to determine the best possible solution around RPA, ML, DL, NLP, GenAI (MCP, RAG, Agentic AI, etc.). 
---

Greetings:
1. Chat agent should greet the user and ask for the use case description.
2. The chat agent should provide 5 starter prompts so that user can select one of them or provide their own use case description.

Questions to user:
1. Chat agent should probe questions around input data and output expected
Example, If user shares "I have 5 numeric columns and one numeric target column, I want to predict the target column based on the input columns", Chat agent should ask questions around the data size, data type, data quality, etc. 
2. Agent should ask appropriate questions to determine the best possible solution around RPA, ML, DL, NLP, GenAI (MCP, RAG, Agentic AI, etc.). 
3. The agent should able to rephrase user question and ask for confirmation before summarizing the use case.
4. Chat agent should able summarize the use case and provide a list of possible solutions with confidence score.


Feedback:
1. Once the chat agent shares the summary and possible solutions, the agent should ask user for feedback on the summary and possible solutions.
2. Agent should check if user expects to send the conversation/summary over email or not.


Rerun/restart/start:
1. One user provides feedback or not, the next step is to check if they want to research on the possible solutions or not.
2. If user wants to research on the possible solutions, the agent should provide a list of possible solutions and ask user to select one of them.
3. The chat agent should able to ask user depth questions so that it can provide a list of possible solutions with more confidence.
Example, if user selects GenAI, agent should ask more detailed questions around the use case to determine the best possible solution around GenAI (MCP, RAG, Agentic AI, etc.). 
4. 


