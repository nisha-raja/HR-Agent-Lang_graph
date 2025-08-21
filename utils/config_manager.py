"""
Configuration Manager
Handles all system configurations and settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """Manages configuration settings for the HR Agent Suite"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
        self.config_file = self.config_dir / "config.json"
        
        # Load environment variables
        load_dotenv()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create default configuration
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default configuration
                default_config = self.get_default_config()
                self.save_config(default_config)
                return default_config
        except Exception as e:
            return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save configuration: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "system": {
                "name": "HR Agent Suite",
                "version": "1.0.0",
                "description": "AI-Powered HR Automation Suite"
            },
            "agents": {
                "jd_generator": {
                    "enabled": True,
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "resume_analyzer": {
                    "enabled": True,
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 3000
                },
                "root_agent": {
                    "enabled": True,
                    "coordination_enabled": True
                }
            },
            "ui": {
                "theme": "light",
                "port": 8501,
                "host": "localhost",
                "debug": False
            },
            "file_management": {
                "auto_cleanup": True,
                "cleanup_days": 30,
                "max_file_size_mb": 10,
                "allowed_extensions": [".txt", ".pdf", ".docx", ".jpg", ".jpeg"]
            },
            "analysis": {
                "min_content_length": 50,
                "max_content_length": 10000,
                "score_weights": {
                    "skills": 0.4,
                    "experience": 0.35,
                    "formatting": 0.25
                }
            },
            "security": {
                "api_key_required": True,
                "log_operations": True,
                "data_retention_days": 90
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        try:
            # Recursively update nested dictionaries
            self._update_nested_dict(self.config, updates)
            self.save_config(self.config)
        except Exception as e:
            print(f"Failed to update configuration: {e}")
    
    def _update_nested_dict(self, base_dict: Dict[str, Any], updates: Dict[str, Any]):
        """Recursively update nested dictionary"""
        for key, value in updates.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._update_nested_dict(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        return self.config.get("agents", {}).get(agent_name, {})
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if specific agent is enabled"""
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get("enabled", True)
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return self.config.get("ui", {})
    
    def get_file_management_config(self) -> Dict[str, Any]:
        """Get file management configuration"""
        return self.config.get("file_management", {})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration"""
        return self.config.get("analysis", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.config.get("security", {})
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI API configuration"""
        return {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
            "temperature": 0.5,
            "max_tokens": 2000
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = [
            "system.name",
            "system.version",
            "agents.jd_generator.enabled",
            "agents.resume_analyzer.enabled",
            "agents.root_agent.enabled"
        ]
        
        for field in required_fields:
            if not self._get_nested_value(self.config, field):
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            validation_result["warnings"].append("OpenAI API key not found in environment variables")
        
        # Check file management settings
        file_config = self.get_file_management_config()
        if file_config.get("cleanup_days", 0) < 1:
            validation_result["warnings"].append("File cleanup days should be at least 1")
        
        return validation_result
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def reset_to_default(self):
        """Reset configuration to default values"""
        self.config = self.get_default_config()
        self.save_config(self.config)
    
    def export_config(self, filepath: str):
        """Export configuration to external file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to export configuration: {e}")
    
    def import_config(self, filepath: str):
        """Import configuration from external file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            validation = self._validate_imported_config(imported_config)
            if validation["valid"]:
                self.config = imported_config
                self.save_config(self.config)
                return {"success": True, "message": "Configuration imported successfully"}
            else:
                return {"success": False, "errors": validation["errors"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_imported_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate imported configuration"""
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        # Check if it's a valid configuration structure
        required_sections = ["system", "agents", "ui", "file_management", "analysis", "security"]
        
        for section in required_sections:
            if section not in config:
                validation_result["errors"].append(f"Missing required section: {section}")
                validation_result["valid"] = False
        
        return validation_result
