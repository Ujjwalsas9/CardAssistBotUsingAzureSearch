import streamlit as st
import asyncio
import os
import argparse
from agents.intent_agent import IntentAgent
from agents.card_management_agent import CardManagementAgent
from agents.knowledge_agent import KnowledgeAgent
from utils.session_state import initialize_session_state, update_chat_history, save_card_states
from utils.openai_setup import setup_openai
from utils.knowledge_base import load_knowledge_base
from utils.logger import setup_logger
import re

# Parse command-line arguments
parser = argparse.ArgumentParser(description="CardAssist Chatbot")
parser.add_argument(
    "--log-level",
    type=str,
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Set the logging level (default: INFO)"
)
args = parser.parse_args()

# Set up logger with the specified level
logger = setup_logger(args.log_level)

# Set environment variable for Streamlit file watcher
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "stat"

# Streamlit App Setup
st.set_page_config(page_title="CardAssist Chatbot", layout="wide")
st.title("💳 CardAssist: Card Management & Knowledge Assistant")

# Welcome Message
st.markdown("""
**Welcome to CardAssist!**  
I'm here to help you manage your cards and answer your questions. You can:
- Activate or deactivate a card (e.g., "Activate card 123456789")
- Check card status (e.g., "What is the status of card 123456789?")
- Ask about card management (e.g., "How do I change my PIN?")
- Reset all cards (e.g., "Reset all cards")
- End the session by saying "thanks" or "end"

Start by typing your question below!
""")

# Initialize session state
initialize_session_state()

# Load knowledge base
embedding_model, chunks, search_client = load_knowledge_base()

# Setup OpenAI and Semantic Kernel
openai_client, kernel = setup_openai()

# Display chat history
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 CardAssist:** {message}")
        if message == "✅ Session ended. You can start a new conversation!" and st.session_state.end_conversation:
            st.markdown("👋 Session ended. Start a new conversation below.")

# Handle user input
async def handle_user_input(user_input: str):
    logger.info(f"Received user input: {user_input}")
    intent_agent = IntentAgent(openai_client)
    card_agent = CardManagementAgent()
    knowledge_agent = KnowledgeAgent(embedding_model, chunks, search_client, openai_client)

    # Check if input is a 9-digit number and last intent was activate/deactivate
    if re.match(r'^\d{9}$', user_input) and st.session_state.last_intent in ["activate", "deactivate"]:
        intent = st.session_state.last_intent
        logger.debug(f"Using previous intent: {intent} for card number input")
    else:
        intent = await intent_agent.classify_intent(user_input, st.session_state.chat_history)
        logger.debug(f"Classified intent: {intent}")

    st.session_state.last_intent = intent

    if intent == "end":
        st.session_state.end_conversation = True
        st.session_state.last_intent = None
        save_card_states()  # Save card states before ending session
        result = "✅ Session ended. You can start a new conversation!"
        logger.info("Conversation ended by user")
    elif intent == "query_activated":
        result = card_agent.query_card_status("activated")
        logger.info(f"Queried activated cards: {result}")
    elif intent == "query_deactivated":
        result = card_agent.query_card_status("deactivated")
        logger.info(f"Queried deactivated cards: {result}")
    elif intent == "query_status":
        match = re.search(r'\b\d{9}\b', user_input)
        if match:
            card_number = match.group(0)
            result = card_agent.query_specific_card_status(card_number)
            logger.info(f"Queried status for card {card_number}: {result}")
        else:
            result = "❓ Please provide a valid 9-digit card number to check its status."
            logger.warning("Invalid card number for status query")
    elif intent == "query_all_status":
        result = card_agent.query_all_status()
        logger.info(f"Queried all card statuses: {result}")
    elif intent in ["activate", "deactivate"]:
        match = re.search(r'\b\d{9}\b', user_input)
        if match:
            card_number = match.group(0)
            result = card_agent.activate_card(card_number) if intent == "activate" else card_agent.deactivate_card(card_number)
            logger.info(f"Performed {intent} on card {card_number}: {result}")
        else:
            action = "activate" if intent == "activate" else "deactivate"
            result = f"❓ Please provide a valid 9-digit card number to {action} the card."
            logger.warning(f"No valid card number provided for {action}")
    elif intent == "knowledge":
        result = knowledge_agent.search_knowledge_base(user_input)
        logger.info(f"Knowledge base query: {user_input}, Response: {result}")
    elif intent == "reset_cards":
        result = card_agent.reset_all_cards()
        logger.info(f"Reset all cards: {result}")
    else:
        result = "❓ Your question is unclear. Please provide a valid query."
        logger.warning(f"Unclear user query: {user_input}")

    return intent, result

# Input Section
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Ask your question:", placeholder="e.g., Activate card 123456789 or How do I change my PIN?")
    submit_btn = st.form_submit_button("Submit")

if submit_btn and user_input:
    try:
        intent, response = asyncio.run(handle_user_input(user_input))
        update_chat_history(user_input, response)
        logger.debug(f"Updated chat history with user input and response: {response}")
        st.rerun()
    except RuntimeError as e:
        st.error(f"Async error: {e}. Please try again.")
        logger.error(f"Async error occurred: {e}")