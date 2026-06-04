import traceback
from src.state import AgentState
from src.schemas import CEOPitchSchema
from src.utils import get_llm, log_scraped_data

def enterprise_sales_node(state: AgentState) -> dict:
    """Compiles the analytical parts into an integrated executive pitch model."""
    llm = get_llm(temperature=0.6)
    
    overview = state.get("company_overview")
    overview_str = f"Sector: {overview.industry} | Scale: {overview.scale} | Location: {overview.geographic_presence}\nOverview: {overview.description}" if overview else ""
    
    challenges_str = ""
    if state["business_challenges"] and state["business_challenges"].challenges:
        for c in state["business_challenges"].challenges:
            challenges_str += f"- Challenge: {c.title} (Category: {c.category})\n  Detail: {c.description}\n"
            
    solutions_str = ""
    if state["ai_opportunities"] and state["ai_opportunities"].solutions:
        for s in state["ai_opportunities"].solutions:
            solutions_str += f"- AI Solution: {s.title} (Domain: {s.domain}) mapped to challenge '{s.mapped_challenge_title}'\n  Technical Mechanism: {s.technical_mechanism}\n  Flow: {s.operational_flow}\n"

    sales_prompt = f"""
    Draft an executive-grade cold outreach pitch to the CEO of {state['company_name']}.
    
    COMPANY CONTEXT:
    {overview_str}
    
    IDENTIFIED BUSINESS CHALLENGES:
    {challenges_str}
    
    PROPOSED AI SOLUTIONS & SYSTEM ARCHITECTURES:
    {solutions_str}
    
    YOUR TASK:
    1. Create a high-impact Subject Line that will grab the CEO's attention.
    2. Write an Executive Summary summarizing the business case.
    3. Generate the full Pitch Letter:
       - Format the letter in beautiful markdown.
       - Address it formally to the CEO of {state['company_name']}.
       - Explain clearly why you reached out (e.g., studying industry bottlenecks and scaling challenges).
       - Present the specific challenges you identified and how they impact business metrics.
       - Detail the proposed AI solutions and the technical mechanisms (libraries, models) that resolve them.
       - Provide a clear call to action proposing a brief discovery call.
       - Ensure the pitch reads like a bespoke, tailored document, completely devoid of generic hype.
    """
    try:
        structured_sales = llm.with_structured_output(CEOPitchSchema)
        pitch = structured_sales.invoke(sales_prompt)
        error_payload = {}
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Enterprise Sales Agent - Exception", state["company_name"], tb_str)
        # Fallback default pitch
        pitch = CEOPitchSchema(
            subject_line=f"Unlocking AI-Driven Margin Expansion for {state['company_name']}",
            executive_summary=f"A consultative proposal highlighting 4 strategic corporate challenges at {state['company_name']} and matching AI architectures to accelerate operational efficiency and customer retention.",
            pitch_letter=f"""# Executive Consultation Memo

**To:** Chief Executive Officer, {state['company_name']}  
**From:** Principal Enterprise AI Architect  
**Subject:** Operational Velocity & Margin Expansion Opportunities  

Dear Chief Executive Officer,

I am reaching out to share a structured analysis of {state['company_name']}'s current market position and operational footprint. As scaling demands increase in your sector, manual oversight of operational workflows, customer inquiry routing, and predictive analytics often create margin leaks and resource bottlenecks.

Based on our recent research, we have identified several potential opportunities where advanced machine learning frameworks could significantly accelerate your business velocity:

1. **Operations Bottleneck:** Manual project tracking and delivery scheduling constraints. We propose an **Agentic Worksite Progress Automation** framework running OpenCV and fine-tuned YOLOv8 models to auto-log worksite milestones.
2. **Sales Conversions:** Optimizing customer lead qualification. We propose a **Predictive Lead Quality Engine** built using XGBoost on historical CRM metrics to route leads to top-performing teams.
3. **Customer Experience:** Post-sales inquiry response latency. We propose a **Context-Aware Support RAG system** leveraging LlamaIndex and a Qdrant vector database for instant customer queries resolutions.
4. **Compliance & Document Processing:** Managing regulatory zoning filings. We propose a fine-tuned **LayoutLMv3 document parser** to auto-extract zoning parameters.

Integrating these custom-tailored systems directly into your daily data streams could unlock new efficiencies, reduce customer turnover, and accelerate project cycles.

I would welcome a brief, 10-minute exploratory conversation next week to share our detailed technical blueprints and discuss how we can partner to pilot these capabilities.

Sincerely,  
*Lead Solutions Architect*  
*Enterprise AI Practice*"""
        )
        error_payload = {"error_logs": [f"Sales extraction error: {str(e)}"]}
        
    pitch_str = pitch.model_dump_json(indent=2) if hasattr(pitch, 'model_dump_json') else str(pitch)
    log_scraped_data("Enterprise Sales Agent - Pitch Memo", state["company_name"], pitch_str)

    return {"ceo_pitch": pitch, **error_payload}
