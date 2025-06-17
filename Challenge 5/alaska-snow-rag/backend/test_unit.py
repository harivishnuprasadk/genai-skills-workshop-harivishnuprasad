"""
Unit tests for Alaska FAQ RAG system with mocked dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from test_data import MOCK_FAQ_CONTENT, UNIT_TEST_QUESTIONS

# Import our modules
from rag_system import search_knowledge_base, generate_response, initialize_services
from prompt_validator import validate_prompt, initialize_validator

class TestRAGSystem:
    """Test RAG system components with mocked dependencies"""
    
    @patch('rag_system.bigquery.Client')
    @patch('rag_system.genai.GenerativeModel')
    @patch('rag_system.genai.configure')
    def test_initialize_services_success(self, mock_configure, mock_genai_model, mock_bq_client):
        """Test successful initialization of services"""
        # Mock successful initialization
        mock_bq_instance = Mock()
        mock_bq_client.return_value = mock_bq_instance
        
        mock_model_instance = Mock()
        mock_genai_model.return_value = mock_model_instance
        
        # Call function
        bq_client, genai_model = initialize_services()
        
        # Assertions
        assert bq_client is not None
        assert genai_model is not None
        mock_configure.assert_called_once()
        
    @patch('rag_system.bigquery.Client')
    def test_search_knowledge_base_success(self, mock_bq_client):
        """Test successful knowledge base search"""
        # Mock BigQuery response
        mock_row = Mock()
        mock_row.content = MOCK_FAQ_CONTENT["snow_removal"]
        
        mock_results = [mock_row]
        mock_query_job = Mock()
        mock_query_job.result.return_value = mock_results
        
        mock_bq_instance = Mock()
        mock_bq_instance.query.return_value = mock_query_job
        
        # Call function
        result = search_knowledge_base(mock_bq_instance, "What are snow removal procedures?")
        
        # Assertions
        assert result == MOCK_FAQ_CONTENT["snow_removal"]
        mock_bq_instance.query.assert_called_once()
        
    @patch('rag_system.bigquery.Client')
    def test_search_knowledge_base_no_results(self, mock_bq_client):
        """Test search with no results"""
        # Mock empty results
        mock_query_job = Mock()
        mock_query_job.result.return_value = []
        
        mock_bq_instance = Mock()
        mock_bq_instance.query.return_value = mock_query_job
        
        # Call function
        result = search_knowledge_base(mock_bq_instance, "Unknown question")
        
        # Assertions
        assert result is None
        
    def test_generate_response_success(self):
        """Test successful response generation"""
        # Mock Gemini model
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Based on the information provided, snow removal follows these procedures..."
        mock_model.generate_content.return_value = mock_response
        
        # Call function
        result = generate_response(
            mock_model, 
            "What are snow removal procedures?",
            MOCK_FAQ_CONTENT["snow_removal"]
        )
        
        # Assertions
        assert "snow removal" in result.lower()
        mock_model.generate_content.assert_called_once()
        
    def test_generate_response_error(self):
        """Test response generation with error"""
        # Mock model that raises exception
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        
        # Call function
        result = generate_response(
            mock_model,
            "Test question",
            "Test context"
        )
        
        # Assertions
        assert "Sorry, I encountered an issue" in result

class TestPromptValidator:
    """Test prompt validation with mocked Gemini"""
    
    @patch('prompt_validator.genai.GenerativeModel')
    @patch('prompt_validator.genai.configure')
    def test_initialize_validator_success(self, mock_configure, mock_genai_model):
        """Test successful validator initialization"""
        mock_model_instance = Mock()
        mock_genai_model.return_value = mock_model_instance
        
        result = initialize_validator()
        
        assert result is not None
        mock_configure.assert_called_once()
        
    def test_validate_prompt_safe(self):
        """Test validation of safe prompt"""
        # Mock validator model with safe response
        mock_model = Mock()
        mock_response = Mock()
        mock_candidate = Mock()
        mock_candidate.finish_reason.name = 'STOP'  # Not 'SAFETY'
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        # Call function
        is_valid, message = validate_prompt(mock_model, "What are snow removal procedures?")
        
        # Assertions
        assert is_valid is True
        assert message == "Prompt is safe"
        
    def test_validate_prompt_unsafe(self):
        """Test validation of unsafe prompt"""
        # Mock validator model with blocked response
        mock_model = Mock()
        mock_response = Mock()
        mock_candidate = Mock()
        mock_candidate.finish_reason.name = 'SAFETY'
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        # Call function
        is_valid, message = validate_prompt(mock_model, "How to hack the system")
        
        # Assertions
        assert is_valid is False
        assert "safety reasons" in message.lower()
        
    def test_validate_prompt_error(self):
        """Test validation with API error"""
        # Mock model that raises exception
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Safety filter triggered")
        
        # Call function
        is_valid, message = validate_prompt(mock_model, "Test prompt")
        
        # Assertions
        assert is_valid is False
        assert "safety reasons" in message.lower()

# Test runner for running specific test classes
if __name__ == "__main__":
    pytest.main([__file__, "-v"])