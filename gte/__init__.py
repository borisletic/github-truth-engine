"""
GitHub Truth Engine - AI-powered roast bot for GitHub repositories
"""

__version__ = "0.1.0"
__author__ = "Boris Letic"

from .analyzer import RepoAnalyzer
from .roaster import AIRoaster

__all__ = ["RepoAnalyzer", "AIRoaster"]
