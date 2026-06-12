import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

# Load local environment variables if testing locally
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve environment variables
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

# Initialize the AI Client (Assumes OpenAI or any OpenAI-compatible provider)
ai_client = OpenAI(api_key=AI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Hello! I am Grammarly0_Bot, your AI writing assistant.\n\n"
        "Just send me any text, sentence, or paragraph, and I will fix the grammar, spelling, "
        "punctuation, and structure while making it clear and readable!"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process user text and return AI-corrected text."""
    user_text = update.message.text
    
    # Send a typing indicator so the user knows the AI is working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Define the instruction for the AI
    system_prompt = (
        "You are an expert copyeditor and writing assistant. "
        "Correct all grammar, spelling, punctuation, and structural issues in the provided text. "
        "Improve clarity and readability while maintaining the original tone. "
        "Provide ONLY the corrected version of the text. Do not add conversational intro/outro text."
    )

    try:
        # Call the AI API
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini", # You can adjust this based on your preferred provider/model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.3
        )
        
        corrected_text = response.choices[0].message.content.strip()
        
        # If the text didn't require any changes, let the user know gently
        if corrected_text.lower() == user_text.lower():
            await update.message.reply_text("✨ Looks perfect! No corrections needed.")
        else:
            await update.message.reply_text(f"📝 **Corrected Version:**\n\n{corrected_text}", parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error calling AI API: {e}")
        await update.message.reply_text("⚠️ Sorry, I ran into an error processing your request. Please try again later.")

def main():
    """Start the bot."""
    if not TELEGRAM_TOKEN or not AI_API_KEY:
        logger.error("Missing Environment Variables! Please set BOT_TOKEN and AI_API_KEY.")
        return

    # Build the application using the Telegram token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Run the bot using Long Polling (perfect for simple Railway deployments)
    application.run_polling()

if __name__ == '__main__':
    main()
