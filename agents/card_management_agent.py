import streamlit as st
from utils.logger import setup_logger
from utils.session_state import save_card_states

class CardManagementAgent:
    def __init__(self):
        self.logger = setup_logger()

    def activate_card(self, card_number: str) -> str:
        self.logger.debug(f"Attempting to activate card: {card_number}")
        if not card_number.isdigit() or len(card_number) != 9:
            self.logger.warning(f"Invalid card number for activation: {card_number}")
            return "❌ Invalid card number. Must be 9 digits."
        if card_number in st.session_state.card_states and st.session_state.card_states[card_number] == "active":
            self.logger.info(f"Card {card_number} already activated")
            return f"⚠️ Card {card_number} is already activated."
        st.session_state.card_states[card_number] = "active"
        st.session_state.card_action_history.append((card_number, "activated"))
        save_card_states()
        self.logger.info(f"Card {card_number} activated successfully")
        return f"✅ Card {card_number} has been activated."

    def deactivate_card(self, card_number: str) -> str:
        self.logger.debug(f"Attempting to deactivate card: {card_number}")
        if not card_number.isdigit() or len(card_number) != 9:
            self.logger.warning(f"Invalid card number for deactivation: {card_number}")
            return "❌ Invalid card number. Must be 9 digits."
        if card_number in st.session_state.card_states and st.session_state.card_states[card_number] == "inactive":
            self.logger.info(f"Card {card_number} already deactivated")
            return f"⚠️ Card {card_number} is already deactivated."
        st.session_state.card_states[card_number] = "inactive"
        st.session_state.card_action_history.append((card_number, "deactivated"))
        save_card_states()
        self.logger.info(f"Card {card_number} deactivated successfully")
        return f"🔒 Card {card_number} has been deactivated."

    def query_card_status(self, action: str) -> str:
        self.logger.debug(f"Querying card status for action: {action}")
        if not st.session_state.card_action_history:
            self.logger.info(f"No cards have been {action} in this session")
            return f"ℹ️ No cards have been {action} in this session."
        filtered_actions = [(card_number, act) for card_number, act in st.session_state.card_action_history if act == action]
        if not filtered_actions:
            self.logger.info(f"No cards found for action: {action}")
            return f"ℹ️ No cards have been {action} in this session."
        response = f"ℹ️ Cards {action}:\n"
        for card_number, _ in filtered_actions:
            response += f"- Card {card_number} was {action}.\n"
        self.logger.info(f"Queried {action} cards: {response.strip()}")
        return response.strip()

    def query_specific_card_status(self, card_number: str) -> str:
        self.logger.debug(f"Querying status for card: {card_number}")
        if not card_number.isdigit() or len(card_number) != 9:
            self.logger.warning(f"Invalid card number for status query: {card_number}")
            return "❌ Invalid card number. Must be 9 digits."
        if card_number not in st.session_state.card_states:
            self.logger.info(f"No recorded actions for card {card_number}")
            return f"ℹ️ Card {card_number} has no recorded actions."
        status = st.session_state.card_states[card_number]
        self.logger.info(f"Card {card_number} status: {status}")
        return f"ℹ️ Card {card_number} is currently {status}."

    def query_all_status(self) -> str:
        self.logger.debug("Querying all card statuses")
        if not st.session_state.card_action_history:
            self.logger.info("No cards have been activated or deactivated")
            return "ℹ️ No cards have been activated or deactivated."
        
        activated = [(card_number, act) for card_number, act in st.session_state.card_action_history if act == "activated"]
        deactivated = [(card_number, act) for card_number, act in st.session_state.card_action_history if act == "deactivated"]
        
        response = ""
        if activated:
            response += "ℹ️ Cards activated:\n" + "\n".join(f"- Card {card_number} was activated." for card_number, _ in activated) + "\n\n"
        else:
            response += "ℹ️ No cards have been activated.\n\n"
        
        if deactivated:
            response += "ℹ️ Cards deactivated:\n" + "\n".join(f"- Card {card_number} was deactivated." for card_number, _ in deactivated)
        else:
            response += "ℹ️ No cards have been deactivated."
        
        self.logger.info(f"All card statuses: {response.strip()}")
        return response.strip()

    def reset_all_cards(self) -> str:
        self.logger.debug("Attempting to reset all card states")
        if not st.session_state.card_states:
            self.logger.info("No card states to reset")
            return "ℹ️ No cards to reset."
        st.session_state.card_states.clear()
        st.session_state.card_action_history.clear()
        save_card_states()
        self.logger.info("All card states and action history reset successfully")
        return "✅ All card states have been reset."