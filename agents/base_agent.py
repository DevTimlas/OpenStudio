"""Base agent class for OpenStudio AI agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
import traceback
from config import settings


class BaseAgent(ABC):
    """Base class for all OpenStudio AI agents."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """Initialize the base agent with LLM configuration."""
        try:
            self.model_name = model_name
            self.llm = self._initialize_llm()
        except Exception as e:
            print(f"❌ Error initializing BaseAgent: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            self.llm = None
    
    def _initialize_llm(self):
        """Initialize the language model."""
        try:
            # Use OpenAI as primary LLM
            return ChatOpenAI(
                model=self.model_name,
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )
        except Exception as e:
            print(f"❌ Warning: Could not initialize LLM: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return None
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and return the response."""
        pass
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using the LLM."""
        if not self.llm:
            return "Error: LLM not initialized. Please check your API configuration."
        
        try:
            messages = []
            if system_prompt:
                messages.append(("system", system_prompt))
            messages.append(("human", prompt))
            
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return f"Error generating response: {str(e)}"
    
    def validate_request(self, request: Dict[str, Any], required_fields: list) -> bool:
        """Validate that required fields are present in the request."""
        try:
            return all(field in request for field in required_fields)
        except Exception as e:
            print(f"❌ Error validating request: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return False