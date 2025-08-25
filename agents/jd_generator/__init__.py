"""
JD Generator Agent Package
"""

from .agent import JDGeneratorAgent
from .models import JobDetails, JobDescriptionResponse, ValidationResult, RAGStats
from .config import JDGeneratorConfig
from .utils import JDFileManager, JDValidator, RAGUtils

# Export main classes
__all__ = [
    'JDGeneratorAgent',
    'JobDetails', 
    'JobDescriptionResponse',
    'ValidationResult',
    'RAGStats',
    'JDGeneratorConfig',
    'JDFileManager',
    'JDValidator',
    'RAGUtils'
]

# For backward compatibility
LangGraphJDGenerator = JDGeneratorAgent
SimpleRAGJDGenerator = JDGeneratorAgent
RAGEnhancedJDGenerator = JDGeneratorAgent
