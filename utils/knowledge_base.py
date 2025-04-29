import streamlit as st
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    VectorSearch,  # Correct import from indexes.models
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
import numpy as np
from utils.logger import setup_logger

@st.cache_resource
def load_knowledge_base():
    logger = setup_logger()
    logger.debug("Loading knowledge base with Azure Search")
    try:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Loaded SentenceTransformer model")
        reader = PdfReader("global_card_access_user_guide.pdf")
        chunks = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                chunks.extend([chunk.strip() for chunk in text.split("\n\n") if chunk.strip()])
        logger.info(f"Extracted {len(chunks)} text chunks from PDF")

        # Load Azure Search configuration
        load_dotenv()
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        api_key = os.getenv("AZURE_SEARCH_API_KEY")
        if not endpoint or not api_key:
            logger.error("AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY not set in .env")
            raise ValueError("Azure Search configuration is missing in .env")

        # Initialize Azure Search index client
        credential = AzureKeyCredential(api_key)
        index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
        logger.debug("Initialized Azure Search index client")

        # Define index schema
        index_name = "cardassist-index"
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True, searchable=False),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                dimensions=384,
                vector_search_profile_name="my-vector-profile"
            )
        ]
        vector_search = VectorSearch(
            algorithms=[VectorSearchAlgorithmConfiguration(name="my-hnsw", kind="hnsw")],
            profiles=[VectorSearchProfile(name="my-vector-profile", algorithm_configuration_name="my-hnsw")]
        )
        index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

        # Create index if it doesn't exist
        try:
            index_client.get_index(index_name)
            logger.info(f"Index {index_name} already exists")
        except:
            logger.info(f"Creating index {index_name}")
            index_client.create_index(index)
            logger.info(f"Index {index_name} created successfully")

        # Initialize Azure Search client
        search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
        logger.debug("Initialized Azure Search client")

        # Upload documents with embeddings
        documents = [
            {
                "id": str(i),
                "content": chunk,
                "embedding": embedding_model.encode(chunk).tolist()
            }
            for i, chunk in enumerate(chunks)
        ]
        try:
            result = search_client.upload_documents(documents)
            logger.info(f"Uploaded {len(documents)} documents to Azure Search index")
            for res in result:
                if not res.succeeded:
                    logger.error(f"Failed to upload document {res.key}: {res.error_message}")
        except Exception as e:
            logger.error(f"Error uploading documents: {e}")
            raise

        return embedding_model, chunks, search_client
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        raise