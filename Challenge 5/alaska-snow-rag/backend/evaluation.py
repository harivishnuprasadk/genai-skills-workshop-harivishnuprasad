"""
Google Evaluation Service for Alaska FAQ RAG system
Evaluates the quality of real RAG responses
"""

import os
import datetime
import pandas as pd
import vertexai
from vertexai.evaluation import EvalTask, MetricPromptTemplateExamples
from google.cloud import aiplatform

# Import our RAG system
from rag_system import initialize_services, search_knowledge_base, generate_response
from prompt_validator import initialize_validator, validate_prompt
from test_data import EVALUATION_QUESTIONS, ALASKA_SYSTEM_PROMPT, MOCK_FAQ_CONTENT
from config import PROJECT_ID

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location="us-central1")

def generate_rag_response(question):
    """Generate actual RAG response for evaluation"""
    try:
        # Initialize services
        bq_client, genai_model = initialize_services()
        validator_model = initialize_validator()
        
        if not all([bq_client, genai_model, validator_model]):
            return "Error: Failed to initialize services"
        
        # Validate prompt
        is_valid, validation_msg = validate_prompt(validator_model, question)
        if not is_valid:
            return f"Prompt validation failed: {validation_msg}"
        
        # Search knowledge base
        context = search_knowledge_base(bq_client, question)
        if not context:
            return "I couldn't find information about that topic in my Alaska FAQ database."
        
        # Generate response
        response = generate_response(genai_model, question, context)
        return response
        
    except Exception as e:
        return f"Error generating response: {str(e)}"

def create_evaluation_dataset():
    """Create evaluation dataset with real RAG responses"""
    print("📊 Creating evaluation dataset...")
    
    eval_data = []
    
    for item in EVALUATION_QUESTIONS:
        # Generate actual RAG response
        rag_response = generate_rag_response(item["question"])
        
        # For evaluation, we'll use mock context since we can't guarantee BigQuery results
        # In production, this would use actual retrieved context
        context = MOCK_FAQ_CONTENT.get(item["context_key"], "No context found")
        
        eval_data.append({
            "instruction": ALASKA_SYSTEM_PROMPT,
            "context": f"Question: {item['question']}\nRetrieved Information: {context}",
            "response": rag_response,
            "reference": item["reference_answer"]
        })
        
        print(f"✅ Generated response for: {item['question'][:50]}...")
    
    return pd.DataFrame(eval_data)

def run_evaluation():
    """Run Google Evaluation Service on RAG responses"""
    print("\n🚀 Starting Alaska FAQ RAG Evaluation\n")
    
    # Create evaluation dataset
    eval_dataset = create_evaluation_dataset()
    
    # Dataset shape
    print(f"📝 Dataset shape: {eval_dataset.shape}")
    
    # Create timestamp for this run
    run_timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Create evaluation task
    print("\n📐 Setting up evaluation metrics...")
    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=[
            MetricPromptTemplateExamples.Pointwise.GROUNDEDNESS,
            MetricPromptTemplateExamples.Pointwise.INSTRUCTION_FOLLOWING,
            MetricPromptTemplateExamples.Pointwise.SAFETY,
            MetricPromptTemplateExamples.Pointwise.SUMMARIZATION_QUALITY
        ],
        experiment=f"alaska-faq-rag-evaluation-{run_timestamp}"
    )
    
    # Run evaluation
    print("\n🔄 Running evaluation (this may take a few minutes)...")
    try:
        result = eval_task.evaluate(
            prompt_template="Instruction: {instruction}\nContext: {context}\nResponse: {response}",
            experiment_run_name=f"alaska-rag-eval-{run_timestamp}"
        )
        
        print("\n✅ Evaluation complete!")
        print("\n📊 Results Summary:")
        print(f"{'='*60}")
        
        # Display results
        if hasattr(result, 'summary_metrics'):
            for metric, value in result.summary_metrics.items():
                print(f"{metric}: {value:.3f}")

    except Exception as e:
        print(f"\n❌ Evaluation error: {str(e)}")
        print("\nNote: Make sure you have the necessary permissions and APIs enabled:")
        print("- Vertex AI API")
        print("- Cloud Storage (for results)")
        print("- Proper IAM permissions")

def run_quick_evaluation():
    """Run a quick evaluation without Google Evaluation Service"""
    print("\n🚀 Running Quick Local Evaluation\n")
    
    results = []
    for item in EVALUATION_QUESTIONS[:3]:  # Test first 3 questions
        print(f"\n{'='*60}")
        print(f"❓ Question: {item['question']}")
        
        response = generate_rag_response(item['question'])
        print(f"🤖 RAG Response: {response[:200]}...")
        print(f"📚 Reference: {item['reference_answer'][:200]}...")
        
        results.append({
            "question": item['question'],
            "rag_response": response,
            "reference": item['reference_answer']
        })

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Run quick evaluation without Google Evaluation Service
        run_quick_evaluation()
    else:
        # Run full evaluation with Google Evaluation Service
        run_evaluation()