import openai
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from dotenv import load_dotenv
import os
from utils.logger import setup_logger

def setup_openai():
    logger = setup_logger()
    logger.debug("Setting up OpenAI client and Semantic Kernel")
    
    # Load environment variables from .env file
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY is required but not set in .env file")
    
    logger.info("Successfully loaded OpenAI API key from environment")
    
    openai_client = openai.OpenAI(api_key=openai_key)
    
    kernel = Kernel()
    chat_service = OpenAIChatCompletion(
        service_id="openai-gpt4",
        ai_model_id="gpt-4",
        api_key=openai_key
    )
    kernel.add_service(chat_service)
    logger.debug("OpenAI client and Semantic Kernel initialized")
    
    return openai_client, kernel