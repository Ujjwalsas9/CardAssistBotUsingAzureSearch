from utils.logger import setup_logger

class KnowledgeAgent:
    def __init__(self, embedding_model, chunks, search_client, openai_client):
        self.embedding_model = embedding_model
        self.chunks = chunks
        self.search_client = search_client
        self.openai_client = openai_client
        self.logger = setup_logger()

    def search_knowledge_base(self, query: str) -> str:
        self.logger.debug(f"Searching knowledge base for query: {query}")
        try:
            query_vector = self.embedding_model.encode([query]).tolist()[0]
            results = self.search_client.search(
                search_text="*",
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_vector,
                    "k": 3,
                    "fields": "embedding"
                }],
                top=3
            )
            retrieved_text = "\n\n".join([result["content"] for result in results])
            self.logger.debug(f"Retrieved knowledge base text: {retrieved_text[:100]}...")

            prompt = f"""
Answer the question using only the information below.

### Knowledge:
{retrieved_text}

### Question:
{query}

### Answer:
"""
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content.strip()
            self.logger.info(f"Knowledge base response: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error in knowledge base search: {e}")
            raise