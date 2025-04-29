from utils.logger import setup_logger

class IntentAgent:
    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.logger = setup_logger()

    async def classify_intent(self, user_input: str, chat_history: list) -> str:
        self.logger.debug(f"Classifying intent for input: {user_input}")
        context = ""
        for role, message in chat_history[-4:]:
            context += f"{role}: {message}\n"

        system_prompt = """
You are an intent classifier for a card management chatbot. Classify the user's intent into one of these:
- activate
- deactivate
- query_activated
- query_deactivated
- query_status
- query_all_status
- knowledge
- end
- reset_cards

Consider the conversation context to determine if the user is responding to a prompt (e.g., providing a card number after being asked). 
- Use 'query_status' for questions about a specific card's status (e.g., "What is the status of card 123456789?").
- Use 'query_all_status' for questions about all activated and deactivated cards.
- Use 'reset_cards' for requests to reset all card states (e.g., "Reset all cards").
Return only the intent word.
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\nCurrent input: {user_input}"}
                ]
            )
            intent = response.choices[0].message.content.strip().lower()
            self.logger.info(f"Classified intent: {intent}")
            return intent
        except Exception as e:
            self.logger.error(f"Error classifying intent: {e}")
            raise