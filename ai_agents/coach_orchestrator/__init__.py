"""
Coach Orchestrator Agent

Unified AI coach that combines:
- Personal coaching (user data analysis)
- Evidence-based knowledge (RAG)
- Specialist integration (Nutrition, Training agents)
"""

from .agent import CoachAgent
from .prompts import get_system_prompt
from .tools import get_available_tools, execute_tool

__all__ = [
    "CoachAgent",
    "get_system_prompt",
    "get_available_tools",
    "execute_tool",
]
