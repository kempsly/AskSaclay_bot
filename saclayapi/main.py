# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import initialize_tools, initialize_bot, process_input

# Initialize FastAPI app
app = FastAPI()

# Initialize chatbot tools and agent
tools = initialize_tools()
agent_executor = initialize_bot(tools, os.getenv("GROQ_API_KEY"))

# Define request and response models
class ChatRequest(BaseModel):
    input_text: str

class ChatResponse(BaseModel):
    response: str

# Define the /chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = process_input(agent_executor, request.input_text)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)