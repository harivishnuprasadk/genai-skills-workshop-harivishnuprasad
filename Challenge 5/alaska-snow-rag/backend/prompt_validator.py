import google.generativeai as genai
from config import GEMINI_API_KEY, SAFETY_SETTINGS

def initialize_validator():
    """Initialize Gemini model for prompt validation"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Using gemini-1.5-flash for fast validation
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            safety_settings=SAFETY_SETTINGS
        )
        
        print("✅ Prompt validator initialized")
        return model
        
    except Exception as e:
        print(f"❌ Validator initialization failed: {e}")
        return None

def validate_prompt(validator_model, prompt):
    """
    Validates if a prompt is safe to process
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        # Test the prompt with the validator model
        response = validator_model.generate_content(prompt)
        
        # Check if response was blocked
        if response.candidates and response.candidates[0].finish_reason.name == 'SAFETY':
            return False, "This prompt was blocked for safety reasons. Please rephrase your question."
        
        # If we got here, prompt is safe
        return True, "Prompt is safe"
        
    except Exception as e:
        # If any error occurs (including safety blocks), consider it unsafe
        error_msg = str(e).lower()
        if 'safety' in error_msg or 'block' in error_msg:
            return False, "This prompt was blocked for safety reasons. Please rephrase your question."
        else:
            return False, f"Error validating prompt: {e}"