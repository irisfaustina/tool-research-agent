from typing import List, Optional, Dict, Any #to give exact format
from pydantic import BaseModel #typing for python allows us to validate data, to create structured data models

#take all of this type data and pipe into python object, so LLM gives data not in a markdown format
#llm output
class CompanyAnalysis(BaseModel): #schema/type defined inpydantic class that inherits from base model
    """Structured output for LLM company analysis focused on developer tools"""
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    description: str = ""
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []

#return for analysis
class CompanyInfo(BaseModel): #pydantic class
    name: str
    description: str
    website: str
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    competitors: List[str] = []
    # Developer-specific fields
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []
    developer_experience_rating: Optional[str] = None  # Poor, Good, Excellent


class ResearchState(BaseModel): #pydantic class
    query: str
    extracted_tools: List[str] = []  # Tools extracted from articles
    companies: List[CompanyInfo] = []
    search_results: List[Dict[str, Any]] = []
    analysis: Optional[str] = None