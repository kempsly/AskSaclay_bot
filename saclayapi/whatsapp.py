from fastapi import FastAPI, Request, Form
from twilio.rest import Client
import os

# Initialize FastAPI app
app = FastAPI()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize chatbot tools and agent
tools = initialize_tools()
agent_executor = initialize_bot(tools, os.getenv("GROQ_API_KEY"))

# Webhook endpoint for WhatsApp
@app.post("/whatsapp-webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    user_message = Body
    response = process_input(agent_executor, user_message)

    # Send the response back to WhatsApp
    client.messages.create(
        body=response,
        from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
        to=f"whatsapp:{From}"
    )
    return {"status": "ok"}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)