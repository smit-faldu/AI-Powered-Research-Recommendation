import operator
from typing import TypedDict, Annotated, List
from src.schemas import (
    CompanyOverviewSchema,
    KeyBusinessInformationSchema,
    AnalystOutputSchema,
    ArchitectOutputSchema,
    CEOPitchSchema
)

class AgentState(TypedDict):
    company_name: str
    company_overview: CompanyOverviewSchema
    key_business_info: KeyBusinessInformationSchema
    raw_research_data: str
    business_challenges: AnalystOutputSchema
    ai_opportunities: ArchitectOutputSchema
    ceo_pitch: CEOPitchSchema
    research_attempts: int
    critic_feedback: str
    qa_iterations: int
    error_logs: Annotated[List[str], operator.add]
