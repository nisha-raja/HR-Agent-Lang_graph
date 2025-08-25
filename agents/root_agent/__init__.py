"""
Root Agent Package
"""

from .coordinator import RootAgentCoordinator

# Export main class
__all__ = ['RootAgentCoordinator']

# For backward compatibility
HRRootAgent = RootAgentCoordinator
