import os
from typing import TypedDict, List, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from ...core.config import settings

class AgentState(TypedDict):
    repo_context: str
    graph_context: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    analysis_depth: int

class ReasoningWorkflow:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1
        )

    def _get_system_prompt(self) -> str:
        return """
        You are a Senior Staff Security Architect at Aegis. 
        Your task is to perform architectural security reasoning over a codebase's semantic graph.
        
        Focus on:
        1. Insecure trust boundaries (e.g., internal services trusting unvalidated tokens).
        2. Privilege propagation (e.g., a low-privilege service having an exploit path to a high-privilege resource).
        3. Dangerous architectural assumptions.
        4. Attack paths and blast radius.
        
        DO NOT report simple vulnerabilities like XSS or SQLi unless they enable a major architectural exploit.
        Output your findings in a structured JSON format.
        """

    async def analyze_architecture(self, state: AgentState) -> Dict[str, Any]:
        """First stage: Identify core architectural components and trust boundaries."""
        prompt = f"""
        Analyze the following security entities and relationships in the context of {state['repo_context']}:
        {state['graph_context'][:50]} # Truncate for prompt length
        
        Identify specific architectural vulnerabilities and trust boundary violations.
        
        Return ONLY a JSON array of findings. Each finding must have:
        {{ "title": "...", "description": "...", "severity": "high/medium/low", "type": "architectural" }}
        """
        response = await self.llm.ainvoke([
            SystemMessage(content=self._get_system_prompt()),
            HumanMessage(content=prompt)
        ])
        
        import json
        text = response.content
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        try:
            findings = json.loads(text)
            return {"findings": findings}
        except Exception as e:
            return {"findings": [{"title": "Analysis Summary", "description": response.content}]}

    def create_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("architect", self.analyze_architecture)
        
        workflow.set_entry_point("architect")
        workflow.add_edge("architect", END)
        
        return workflow.compile()
