import traceback
from src.state import AgentState
from src.schemas import AISolutionSchema, ArchitectOutputSchema
from src.utils import get_llm, log_scraped_data

def solutions_architect_node(state: AgentState) -> dict:
    """Engineers explicit machine learning pipelines mapped 1:1 against threats."""
    llm = get_llm(temperature=0.3)
    
    challenges_str = ""
    if state["business_challenges"] and state["business_challenges"].challenges:
        for c in state["business_challenges"].challenges:
            challenges_str += f"- Challenge: {c.title} (Category: {c.category})\n  Detail: {c.description}\n"

    architect_prompt = f"""
    You are an AI Solutions Architect. Build exactly 4 concrete, deep infrastructure architectures for {state['company_name']}.
    Target these challenges 1:1:
    {challenges_str}
    
    CRITERIA:
    - Map each solution 1:1 to the 4 challenges listed above. Use the exact challenge title.
    - Assign each solution to one of the following domains: 'Automation', 'Customer Engagement', 'Sales', 'Operations', 'Analytics', 'Document Processing'.
    - Provide company-specific suggestions. Avoid generic boilerplate statements.
    - Explicitly state the technical mechanism (e.g. libraries, frameworks, open-source models, training schemas like 'PyTorch LayoutLMv3', 'Hugging Face transformers', 'LlamaIndex RAG pipelines with Qdrant vector database', etc.). No hand-waving or buzzwords.
    """
    try:
        structured_architect = llm.with_structured_output(ArchitectOutputSchema)
        opportunities = structured_architect.invoke(architect_prompt)
        error_payload = {}
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Solutions Architect Agent - Exception", state["company_name"], tb_str)
        # Fallback default solutions
        default_solutions = [
            AISolutionSchema(
                title="Agentic Worksite Progress Automation",
                domain="Operations",
                mapped_challenge_title="Operational Velocity Constraints",
                technical_mechanism="LangGraph agentic state machines with OpenCV and YOLOv8 running on PyTorch for site photo parsing.",
                operational_flow="Daily worksite status updates are analyzed via site camera feeds, with progress auto-logged to corporate dashboards."
            ),
            AISolutionSchema(
                title="Predictive Lead Quality Analytics Engine",
                domain="Sales",
                mapped_challenge_title="Customer Acquisition Pipeline Efficiency",
                technical_mechanism="XGBoost model training via Scikit-Learn utilizing historical customer CRM feature matrices.",
                operational_flow="Incoming sales leads are auto-scored and routed to high-performing reps based on predicted conversion metrics."
            ),
            AISolutionSchema(
                title="Context-Aware Customer Support RAG System",
                domain="Customer Engagement",
                mapped_challenge_title="Post-Purchase Feedback Loop Latency",
                technical_mechanism="LlamaIndex RAG pipeline using Hugging Face SentenceTransformers and Qdrant vector database.",
                operational_flow="Client queries are intercepted by an AI customer agent with access to project timelines and FAQs to resolve issues instantly."
            ),
            AISolutionSchema(
                title="Unified Compliance & Document Extraction Parser",
                domain="Document Processing",
                mapped_challenge_title="Regulatory Compliance and Scaling Friction",
                technical_mechanism="LayoutLMv3 fine-tuning via PyTorch for structural key-value extraction of zoning and municipal approvals.",
                operational_flow="Scanned local regulatory filings are uploaded to a processing bucket, where LayoutLMv3 auto-extracts compliance terms."
            )
        ]
        opportunities = ArchitectOutputSchema(solutions=default_solutions)
        error_payload = {"error_logs": [f"Architect extraction error: {str(e)}"]}
        
    opportunities_str = opportunities.model_dump_json(indent=2) if hasattr(opportunities, 'model_dump_json') else str(opportunities)
    log_scraped_data("Solutions Architect Agent - AI Opportunities", state["company_name"], opportunities_str)

    return {"ai_opportunities": opportunities, **error_payload}
