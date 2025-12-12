"""
Coach Orchestrator Agent - OpenAI SDK Implementation

This agent provides conversational AI coaching by:
1. Understanding natural language questions
2. Dynamically calling function tools to fetch data
3. Synthesizing personalized responses

Uses OpenAI SDK with function calling for intelligent tool selection.
"""

import json
import os
from typing import Dict, List, Any, Optional
from openai import OpenAI

from .tools import get_available_tools, execute_tool
from .prompts import get_system_prompt


class CoachAgent:
    """
    Conversational AI coach using OpenAI SDK.

    Handles:
    - Personal data analysis (workouts, nutrition, body composition)
    - Evidence-based knowledge (RAG)
    - Specialist agent integration (Nutrition, Training)
    """

    def __init__(
        self,
        openai_api_key: str,
        user_id: str,
        model: str = "gpt-4-turbo-preview"
    ):
        """
        Initialize Coach Agent.

        Args:
            openai_api_key: OpenAI API key
            user_id: Current user ID
            model: OpenAI model to use (default: gpt-4-turbo-preview)
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.user_id = user_id
        self.model = model

    def handle_question(
        self,
        question: str,
        thread_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Handle user question with function calling.

        Args:
            question: User's question
            thread_id: Optional thread ID for multi-turn conversations
            conversation_history: Optional conversation history

        Returns:
            {
                "message": str,  # AI response
                "thread_id": str,  # Thread ID for continuation
                "tool_calls": List[Dict],  # Tools that were called
                "sources": List[Dict]  # Sources if RAG was used
            }
        """
        # Build conversation messages
        messages = self._build_messages(question, conversation_history)

        # Get available tools
        tools = get_available_tools()

        # Track tool calls for debugging/logging
        tool_calls_made = []
        sources_used = []

        # Initial API call
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,  # Only include if we have tools
                tool_choice="auto" if tools else None
            )
        except Exception as e:
            return {
                "message": f"I encountered an error: {str(e)}. Please try again.",
                "thread_id": thread_id,
                "tool_calls": [],
                "sources": [],
                "error": str(e)
            }

        # Handle function calls iteratively
        while response.choices[0].finish_reason == "tool_calls":
            # Extract tool calls
            tool_calls = response.choices[0].message.tool_calls

            # Add assistant message with tool calls to history
            messages.append(response.choices[0].message)

            # Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute tool
                try:
                    result = execute_tool(function_name, function_args, self.user_id)

                    # Track tool usage
                    tool_calls_made.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "success": True
                    })

                    # Extract sources if this was a RAG call
                    if function_name == "search_knowledge_base" and "sources" in result:
                        sources_used.extend(result["sources"])

                except Exception as e:
                    result = {
                        "error": str(e),
                        "message": f"Tool execution failed: {str(e)}"
                    }
                    tool_calls_made.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "success": False,
                        "error": str(e)
                    })

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Continue conversation with tool results
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None
                )
            except Exception as e:
                return {
                    "message": f"I encountered an error processing the results: {str(e)}",
                    "thread_id": thread_id,
                    "tool_calls": tool_calls_made,
                    "sources": sources_used,
                    "error": str(e)
                }

        # Extract final response
        final_message = response.choices[0].message.content

        return {
            "message": final_message,
            "thread_id": thread_id or f"thread_{hash(question)}",  # Simple thread ID
            "tool_calls": tool_calls_made,
            "sources": sources_used
        }

    def _build_messages(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Build message list for OpenAI API.

        Args:
            question: Current user question
            conversation_history: Optional previous messages

        Returns:
            List of messages with system prompt
        """
        messages = [
            {"role": "system", "content": get_system_prompt()}
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question
        messages.append({"role": "user", "content": question})

        return messages
