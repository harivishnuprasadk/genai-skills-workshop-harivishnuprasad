import os
from google.cloud import bigquery
import google.generativeai as genai
from config import PROJECT_ID, GEMINI_API_KEY, DATASET_NAME, TABLE_NAME, EMBEDDING_MODEL

def initialize_services():
    """Initialize BigQuery and Gemini services"""
    # Initialize BigQuery
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)
        print(f"✅ BigQuery connected to project: {PROJECT_ID}")
    except Exception as e:
        print(f"❌ BigQuery connection failed: {e}")
        return None, None

    # Configure Gemini API
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        print("✅ Gemini model ready")
        
        return bq_client, model
        
    except Exception as e:
        print(f"❌ Gemini setup failed: {e}")
        return bq_client, None

def search_knowledge_base(bq_client, user_question):
    """Search Alaska FAQ knowledge base using vector similarity"""
    search_query = f"""
    SELECT
        query.query,
        base.content
    FROM
        VECTOR_SEARCH(
            TABLE `{DATASET_NAME}.{TABLE_NAME}`,
            'ml_generate_embedding_result',
            (
                SELECT
                    ml_generate_embedding_result,
                    content AS query
                FROM
                    ML.GENERATE_EMBEDDING(
                        MODEL `{EMBEDDING_MODEL}`,
                        (SELECT '{user_question}' AS content)
                    )
            ),
            top_k => 1,
            options => '{{"fraction_lists_to_search": 0.01}}'
        );
    """
    
    try:
        query_job = bq_client.query(search_query)
        results = query_job.result()
        
        for row in results:
            return row.content
            
        return None
        
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return None

def generate_response(model, user_question, context):
    """Generate AI response using retrieved context"""
    system_prompt = f"""
You are an Alaska Department information assistant. Provide helpful answers using only the information below.
If the answer isn't available in the provided content, politely say you don't have that information.

Available Information:
{context}

User Question:
{user_question}

Response:"""
    
    try:
        response = model.generate_content(system_prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"⚠️ Response generation error: {e}")
        return "Sorry, I encountered an issue generating a response."