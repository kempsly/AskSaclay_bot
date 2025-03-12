from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters
import os
import httpx

# Initialize FastAPI app
app = FastAPI()

# Telegram bot token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Initialize chatbot tools and agent
tools = initialize_tools()
agent_executor = initialize_bot(tools, os.getenv("GROQ_API_KEY"))

# Handle incoming messages
def handle_message(update, context):
    user_message = update.message.text
    response = process_input(agent_executor, user_message)
    update.message.reply_text(response)

# Register the message handler
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Webhook endpoint for Telegram
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"status": "ok"}

# Set up the webhook
@app.on_event("startup")
async def set_webhook():
    webhook_url = "https://your-domain.com/telegram-webhook"  # Replace with your public URL
    async with httpx.AsyncClient() as client:
        await client.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)