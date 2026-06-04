import traceback
from src.state import AgentState
from src.schemas import ChallengeSchema, AnalystOutputSchema
from src.utils import get_llm, log_scraped_data

def industry_analyst_node(state: AgentState) -> dict:
    """Extracts structural corporate threats responding dynamically to feedback rules."""
    llm = get_llm(temperature=0.2)
    feedback = state.get("critic_feedback", "None")
    
    analyst_prompt = f"""
    You are an elite Industry Analyst. Study this background context for {state['company_name']}:
    {state['raw_research_data']}
    
    PREVIOUS CRITIC FEEDBACK ACTION ITEMS:
    {feedback}
    
    TASK:
    Isolate exactly 4 explicit business challenges, friction vectors, or commercial pain points. 
    You must identify EXACTLY ONE challenge for each of the following 4 categories:
    1. Operational Bottleneck (inefficiencies, supply chain, delivery delays, workflow gaps)
    2. Sales Challenge (customer acquisition, market competition, pricing pressure, revenue leakage)
    3. Customer Experience Challenge (service delivery, post-purchase support, communication friction)
    4. General Challenge (regulatory, strategic, environmental, or scaling challenge)
    
    Every single entry must contain a specific title, the matching category from the list above, a detailed description, and a clear reasoning chain grounded in the research data.
    """
    try:
        structured_analyst = llm.with_structured_output(AnalystOutputSchema)
        challenges = structured_analyst.invoke(analyst_prompt)
        error_payload = {}
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Industry Analyst Agent - Exception", state["company_name"], tb_str)
        # Fallback default challenges
        default_challenges = [
            ChallengeSchema(
                title="Operational Velocity Constraints",
                category="Operational Bottleneck",
                description="Project delivery cycles and resource allocation face alignment bottlenecks due to fragmented manual status tracking.",
                reasoning="Standard real estate and enterprise operations often experience friction in material supply chain updates."
            ),
            ChallengeSchema(
                title="Customer Acquisition Pipeline Efficiency",
                category="Sales Challenge",
                description="Lead tracking and customer sales agent conversion processes lack unified predictive qualification.",
                reasoning="High competition limits organic outreach efficacy without pre-qualified insights."
            ),
            ChallengeSchema(
                title="Post-Purchase Feedback Loop Latency",
                category="Customer Experience Challenge",
                description="Client queries regarding project/service delivery status encounter delayed response times.",
                reasoning="Siloed messaging channels delay prompt customer resolution loops."
            ),
            ChallengeSchema(
                title="Regulatory Compliance and Scaling Friction",
                category="General Challenge",
                description="Managing local norms, regulatory updates, and expansion overheads.",
                reasoning="Real estate and scaling enterprises face strict local zoning and compliance rules."
            )
        ]
        challenges = AnalystOutputSchema(challenges=default_challenges)
        error_payload = {"error_logs": [f"Analyst extraction error: {str(e)}"]}
        
    challenges_str = challenges.model_dump_json(indent=2) if hasattr(challenges, 'model_dump_json') else str(challenges)
    log_scraped_data("Industry Analyst Agent - Challenges", state["company_name"], challenges_str)

    return {"business_challenges": challenges, **error_payload}
