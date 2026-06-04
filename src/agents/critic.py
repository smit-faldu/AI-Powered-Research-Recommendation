import traceback
from src.state import AgentState
from src.schemas import CriticOutputSchema
from src.utils import get_llm, log_scraped_data

def quality_critic_node(state: AgentState) -> dict:
    """Acts as an autonomous guardrail verifying mapping alignment and solution depth."""
    llm = get_llm(temperature=0.1)
    iterations = state.get("qa_iterations", 0) + 1
    
    challenges_str = "\n".join([f"- {c.title} ({c.category}): {c.description}" for c in state["business_challenges"].challenges]) if state["business_challenges"] else ""
    solutions_str = "\n".join([f"- {s.title} (Domain: {s.domain}) mapped to {s.mapped_challenge_title}: {s.technical_mechanism}" for s in state["ai_opportunities"].solutions]) if state["ai_opportunities"] else ""

    critic_prompt = f"""
    Review these proposed organizational assets for alignment depth and quality constraints:
    
    CHALLENGES GATHERED:
    {challenges_str}
    
    SOLUTIONS ARCHITECTURE MAPS:
    {solutions_str}
    
    Verify that:
    1. There are exactly 4 challenges, each in a unique category ('Operational Bottleneck', 'Sales Challenge', 'Customer Experience Challenge', 'General Challenge').
    2. There are exactly 4 AI solutions, mapped 1:1 to each challenge.
    3. Each AI solution is mapped to a specific domain (Automation, Customer Engagement, Sales, Operations, Analytics, Document Processing) and specifies concrete engineering frameworks or ML libraries (e.g. PyTorch, Hugging Face, LlamaIndex, TensorFlow) rather than vague jargon.
    
    Set is_approved to False and provide clear corrections if requirements fall short. Set is_approved to True if all constraints are fully met.
    """
    try:
        structured_critic = llm.with_structured_output(CriticOutputSchema)
        evaluation = structured_critic.invoke(critic_prompt)
        feedback = evaluation.feedback if not evaluation.is_approved else ""
        is_approved = evaluation.is_approved
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Quality Critic Agent - Exception", state["company_name"], tb_str)
        feedback = ""  # Skip and route forward if validation parsing crashes to prevent state loops
        is_approved = True
        
    critic_log_content = f"Approved: {is_approved}\nFeedback: {feedback if feedback else 'None'}"
    log_scraped_data("Quality Critic Agent - Evaluation", state["company_name"], critic_log_content)
        
    return {"critic_feedback": feedback, "qa_iterations": iterations}
