# Importing every model here registers all tables on Base, so
# `from app import models` is enough for create_all() to see them.
from app.models.analysis import Analysis, AnalysisIssue, AnalysisSuggestion
from app.models.person import Person
from app.models.plant import Plant
from app.models.user import User

__all__ = [
    "Analysis",
    "AnalysisIssue",
    "AnalysisSuggestion",
    "Person",
    "Plant",
    "User",
]
