from typing import List, Literal
from pydantic import BaseModel, Field

class QueryGenerationSchema(BaseModel):
    queries: List[str] = Field(..., description="Exactly 3 highly targeted search query strings targeting company profile, recent developments, expansion plans, and industry bottlenecks.")

class CompanyWebsiteExtractionSchema(BaseModel):
    official_website_url: str = Field(..., description="The official website homepage URL of the company. Must be a valid absolute URL (e.g., 'https://www.brigadegroup.com'). If no official website is found in the search results, return an empty string.")


class CompanyOverviewSchema(BaseModel):
    description: str = Field(..., description="A concise summary of what the company does, its core mission, and business model.")
    industry: str = Field(..., description="The primary market sector or industry classification (e.g., Real Estate, Technology, HealthCare).")
    scale: str = Field(..., description="Operational scale, size, employee count, or revenue tier indicators.")
    geographic_presence: str = Field(..., description="Geographic distribution, core operational regions, or headquarters location.")

class KeyBusinessInformationSchema(BaseModel):
    major_offerings: List[str] = Field(..., description="Key products, platforms, projects, or core services provided.")
    recent_developments: List[str] = Field(..., description="Recent corporate news, announcements, mergers, acquisitions, or key launches.")
    expansion_plans: List[str] = Field(..., description="Future expansion plans, geographical scaling, new market entries, or product pipeline launches.")
    important_public_information: List[str] = Field(..., description="Key financial highlights, public stock details, funding rounds, or major partnerships.")

class ChallengeSchema(BaseModel):
    title: str = Field(..., description="Concise, technical title for the corporate friction point.")
    category: Literal["Operational Bottleneck", "Sales Challenge", "Customer Experience Challenge", "General Challenge"] = Field(..., description="The category of this specific business challenge.")
    description: str = Field(..., description="Deep explanation of the bottleneck or threat within this category.")
    reasoning: str = Field(..., description="Explicit logical rationale grounded cleanly in the context gathered.")

class AnalystOutputSchema(BaseModel):
    challenges: List[ChallengeSchema] = Field(..., description="A list of exactly 4 granular business challenges, with exactly one challenge mapping to each category: Operational Bottleneck, Sales Challenge, Customer Experience Challenge, General Challenge.")

class AISolutionSchema(BaseModel):
    title: str = Field(..., description="Title of the technical AI integration workflow.")
    domain: Literal["Automation", "Customer Engagement", "Sales", "Operations", "Analytics", "Document Processing"] = Field(..., description="The operational domain category of this AI opportunity.")
    mapped_challenge_title: str = Field(..., description="The exact title of the corporate challenge this AI solution addresses.")
    technical_mechanism: str = Field(..., description="The explicit core ML model architecture or technique (e.g., Fine-tuning LayoutLMv3 models via PyTorch, implementing a RAG pipeline with LlamaIndex and LangChain). No vague buzzwords.")
    operational_flow: str = Field(..., description="Step-by-step description of how this technical infrastructure integrates with daily corporate data streams.")

class ArchitectOutputSchema(BaseModel):
    solutions: List[AISolutionSchema] = Field(..., description="Exactly 4 advanced technical AI architectures mapped 1:1 against the 4 challenges.")

class CriticOutputSchema(BaseModel):
    is_approved: bool = Field(..., description="True if payload completely passes the compliance and quality rubric, False otherwise.")
    feedback: str = Field(..., description="Constructive remediation instructions outlining formatting or depth improvements. Empty string if approved.")

class CEOPitchSchema(BaseModel):
    subject_line: str = Field(..., description="A high-impact enterprise cold-outreach subject line.")
    executive_summary: str = Field(..., description="A brief, high-impact summary of the pitch.")
    pitch_letter: str = Field(..., description="A complete, professional, one-page business pitch letter in markdown format. It should address the CEO, explain why you reached out, present the specific opportunities identified, detail the proposed AI solutions, and include a clear, professional call to action.")
