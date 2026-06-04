from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from src.state import AgentState
from src.agents import (
    dynamic_researcher_node,
    industry_analyst_node,
    solutions_architect_node,
    quality_critic_node,
    enterprise_sales_node
)

# ==========================================
# CONDITIONAL ROUTING CONTROLLERS
# ==========================================

def evaluate_research_depth(state: AgentState) -> Literal["Analyst", "Researcher"]:
    data = state.get("raw_research_data", "").strip()
    return "Researcher" if (len(data) < 300) and state.get("research_attempts", 0) < 3 else "Analyst"

def evaluate_quality_clearance(state: AgentState) -> Literal["Analyst", "Sales"]:
    return "Analyst" if state.get("critic_feedback") and state.get("qa_iterations", 0) < 3 else "Sales"


# ==========================================
# GRAPH COMPILATION CONTEXT
# ==========================================

def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("Researcher", dynamic_researcher_node)
    workflow.add_node("Analyst", industry_analyst_node)
    workflow.add_node("Architect", solutions_architect_node)
    workflow.add_node("Critic", quality_critic_node)
    workflow.add_node("Sales", enterprise_sales_node)
    
    workflow.set_entry_point("Researcher")
    workflow.add_conditional_edges("Researcher", evaluate_research_depth, {"Researcher": "Researcher", "Analyst": "Analyst"})
    workflow.add_edge("Analyst", "Architect")
    workflow.add_edge("Architect", "Critic")
    workflow.add_conditional_edges("Critic", evaluate_quality_clearance, {"Analyst": "Analyst", "Sales": "Sales"})
    workflow.add_edge("Sales", END)
    
    serde = JsonPlusSerializer(allowed_msgpack_modules=[
        ("src.schemas", "CompanyOverviewSchema"),
        ("src.schemas", "KeyBusinessInformationSchema"),
        ("src.schemas", "AnalystOutputSchema"),
        ("src.schemas", "ArchitectOutputSchema"),
        ("src.schemas", "CEOPitchSchema"),
    ])
    return workflow.compile(checkpointer=MemorySaver(serde=serde))

