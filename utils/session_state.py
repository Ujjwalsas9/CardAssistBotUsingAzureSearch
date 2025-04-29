import streamlit as st
from utils.logger import setup_logger
import json
import os

def initialize_session_state():
    logger = setup_logger()
    logger.debug("Initializing session state")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        logger.info("Initialized chat_history")
    if "card_states" not in st.session_state:
        st.session_state.card_states = load_card_states()
        logger.info("Initialized card_states from persistent storage")
    if "card_action_history" not in st.session_state:
        st.session_state.card_action_history = load_card_action_history()
        logger.info("Initialized card_action_history from persistent storage")
    if "end_conversation" not in st.session_state:
        st.session_state.end_conversation = False
        logger.info("Initialized end_conversation")
    if "last_intent" not in st.session_state:
        st.session_state.last_intent = None
        logger.info("Initialized last_intent")

def update_chat_history(user_input: str, response: str):
    logger = setup_logger()
    logger.debug(f"Updating chat history with input: {user_input}, response: {response}")
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("assistant", response))
    logger.info("Chat history updated")

def load_card_states():
    logger = setup_logger()
    file_path = "card_states.json"
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                return data.get("card_states", {})
        else:
            logger.info("No card_states.json found, initializing empty card states")
            return {}
    except Exception as e:
        logger.error(f"Error loading card states: {e}")
        return {}

def load_card_action_history():
    logger = setup_logger()
    file_path = "card_states.json"
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                return data.get("card_action_history", [])
        else:
            logger.info("No card_states.json found, initializing empty action history")
            return []
    except Exception as e:
        logger.error(f"Error loading card action history: {e}")
        return []

def save_card_states():
    logger = setup_logger()
    file_path = "card_states.json"
    try:
        data = {
            "card_states": st.session_state.card_states,
            "card_action_history": st.session_state.card_action_history
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        logger.debug("Saved card states and action history to card_states.json")
    except Exception as e:
        logger.error(f"Error saving card states: {e}")