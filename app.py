import os
import streamlit as st
import dotenv

from src.workflow import build_workflow
from src.schemas import (
    CompanyOverviewSchema,
    KeyBusinessInformationSchema,
    AnalystOutputSchema,
    ArchitectOutputSchema,
    CEOPitchSchema
)

dotenv.load_dotenv()

# ==========================================
# HIGHLY ORGANIZED STREAMLIT INTERFACE
# ==========================================

def render_stepper(current_node: str):
    nodes = ["Researcher", "Analyst", "Architect", "Critic", "Sales"]
    node_idx = {node: i for i, node in enumerate(nodes)}
    curr_idx = node_idx.get(current_node, -1) if current_node else -1
    
    html = '<div class="stepper-container"><div class="stepper-line"></div>'
    for i, node in enumerate(nodes):
        circle_cls = ""
        label_cls = ""
        symbol = str(i+1)
        
        if i < curr_idx:
            circle_cls = "completed"
            label_cls = "completed"
            symbol = "✓"
        elif i == curr_idx:
            circle_cls = "active"
            label_cls = "active"
        else:
            circle_cls = ""
            label_cls = ""
            
        html += f"""
        <div class="stepper-step">
            <div class="stepper-circle {circle_cls}">{symbol}</div>
            <div class="stepper-label {label_cls}">{node}</div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="AI-Powered Research & Recommendation Engine", page_icon="🧠", layout="wide")
    
    # Custom CSS for Premium Design & Glassmorphism
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Outfit', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #f8fafc;
    }
    
    /* Glassmorphic cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.35);
        border-radius: 8px;
        padding: 18px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Category badges */
    .badge-op {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-sales {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-cx {
        background-color: rgba(6, 182, 212, 0.15);
        color: #06b6d4;
        border: 1px solid rgba(6, 182, 212, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-gen {
        background-color: rgba(139, 92, 246, 0.15);
        color: #8b5cf6;
        border: 1px solid rgba(139, 92, 246, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Pitch letter container */
    .letter-box {
        background-color: #0b0f19;
        color: #f1f5f9;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 40px;
        font-family: 'Outfit', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 1.05rem;
        line-height: 1.7;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 8px 0 rgba(0, 0, 0, 0.5);
        margin-top: 15px;
    }
    
    /* Stepper styles */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        margin: 25px 0;
        position: relative;
        padding: 0 10px;
    }
    .stepper-line {
        position: absolute;
        top: 16px;
        left: 30px;
        right: 30px;
        height: 2px;
        background-color: rgba(255, 255, 255, 0.08);
        z-index: 1;
    }
    .stepper-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        z-index: 2;
        width: 18%;
    }
    .stepper-circle {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background-color: #0f172a;
        border: 2px solid rgba(255, 255, 255, 0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.4);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stepper-circle.active {
        background-color: #2563eb;
        border-color: #3b82f6;
        color: white;
        box-shadow: 0 0 16px rgba(37, 99, 235, 0.6);
        transform: scale(1.1);
    }
    .stepper-circle.completed {
        background-color: #059669;
        border-color: #10b981;
        color: white;
    }
    .stepper-label {
        font-size: 0.78rem;
        margin-top: 8px;
        color: rgba(255, 255, 255, 0.4);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stepper-label.active {
        color: #60a5fa;
        font-weight: 600;
    }
    .stepper-label.completed {
        color: #34d399;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); padding: 30px; border-radius: 12px; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.05);">
        <h1 style="margin:0; font-size: 2.25rem; font-weight:700; background: linear-gradient(to right, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🧠 Enterprise Intelligence & AI Recommendation Engine
        </h1>
        <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 1.1rem;">
            Deep-dive multi-agent corporate research and technical AI architecture mapping.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Engine Parameters")
        
        st.session_state["selected_model"] = "gemini-flash-latest"
        
        selected_temp = st.slider(
            "Generation Temperature",
            min_value=0.1,
            max_value=1.0,
            value=0.2,
            step=0.05,
            help="Lower values yield deterministic, framework-grade specifications. Higher values offer creative outreach copywriting."
        )
        st.session_state["selected_temp"] = selected_temp
        
        st.divider()
        st.markdown("**System State Layer:** Active Structured Processing")
        st.markdown("**Pipeline Mode:** Fully Autonomous Agentic Loop")
        
    company_input = st.text_input("Target Enterprise Name", placeholder="e.g., Sobha, Prestige Group, Adani Realty, Brigade Group")
    
    if st.button("Initiate Agentic Pipeline", type="primary", use_container_width=True):
        if not company_input:
            st.error("Provide a target company name to proceed.")
            st.stop()
            
        if not os.environ.get("GOOGLE_API_KEY"):
            st.error("Google Gemini API Key is missing. Please set the GOOGLE_API_KEY environment variable in your .env file or system environment.")
            st.stop()
 
        app_graph = build_workflow()
        
        initial_state = {
            "company_name": company_input, 
            "company_overview": None, 
            "key_business_info": None,
            "raw_research_data": "",
            "business_challenges": None, 
            "ai_opportunities": None, 
            "ceo_pitch": None,
            "research_attempts": 0, 
            "critic_feedback": "", 
            "qa_iterations": 0, 
            "error_logs": []
        }
 
        thread_config = {"configurable": {"thread_id": "structured_session_99"}}
        
        # Stepper UI placeholder
        stepper_placeholder = st.empty()
        
        with st.status("⚡ Executing Multi-Agent Intelligence Graph...", expanded=True) as status:
            for event in app_graph.stream(initial_state, config=thread_config):
                for node_name, _ in event.items():
                    status.update(label=f"Active Agent: [{node_name}] processing payload...")
                    with stepper_placeholder:
                        render_stepper(node_name)
            
            with stepper_placeholder:
                render_stepper("Sales") # Done with all nodes
            status.update(label="🏁 Pipeline execution completed and payloads validated!", state="complete", expanded=False)
 
        master_state = app_graph.get_state(thread_config).values
        st.success(f"Analysis Generation Complete for: **{company_input}**")
 
        # Expose execution errors / warnings on the UI
        errors = master_state.get("error_logs", [])
        if errors:
            with st.expander("⚠️ System Execution Logs & API Warnings (Some steps utilized fallbacks)", expanded=True):
                st.warning(
                    "The pipeline encountered errors during execution and fell back to default templates. "
                    "Please check the details below. This is usually caused by an invalid or missing Gemini API Key."
                )
                for idx, err in enumerate(errors):
                    st.error(f"Error {idx+1}: {err}")
 
        # Tabs Layout
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Corporate Overview", 
            "⚠️ Business Challenges", 
            "⚡ Targeted AI Blueprints", 
            "✉️ Executive Pitch Memo"
        ])
        
        # TAB 1: Corporate Overview
        with tab1:
            overview_data: CompanyOverviewSchema = master_state.get("company_overview")
            business_info: KeyBusinessInformationSchema = master_state.get("key_business_info")
            
            if overview_data:
                st.markdown(f"### 🏢 {company_input}")
                st.markdown(f"<div class='glass-card'><p style='font-size: 1.15rem; font-style: italic; color: #e2e8f0; margin:0;'>{overview_data.description}</p></div>", unsafe_allow_html=True)
                
                st.subheader("📊 Profile Matrix")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"<div class='metric-card'><strong>Industry Sector</strong><br/><span style='font-size:1.15rem; font-weight:600;'>{overview_data.industry}</span></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-card'><strong>Scale / Class</strong><br/><span style='font-size:1.15rem; font-weight:600;'>{overview_data.scale}</span></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='metric-card'><strong>Geographic Footprint</strong><br/><span style='font-size:1.15rem; font-weight:600;'>{overview_data.geographic_presence}</span></div>", unsafe_allow_html=True)
            
            if business_info:
                st.write("---")
                st.subheader("🔑 Strategic Intelligence Profile")
                
                col_left, col_right = st.columns(2)
                with col_left:
                    with st.container(border=True):
                        st.markdown("#### 🛠️ Major Product / Service Offerings")
                        for offering in business_info.major_offerings:
                            st.markdown(f"🔹 {offering}")
                    
                    with st.container(border=True):
                        st.markdown("#### 📈 Recent Corporate Developments")
                        for dev in business_info.recent_developments:
                            st.markdown(f"🔹 {dev}")
                            
                with col_right:
                    with st.container(border=True):
                        st.markdown("#### 🚀 Expansion and Scaling Plans")
                        for plan in business_info.expansion_plans:
                            st.markdown(f"🔹 {plan}")
                    
                    with st.container(border=True):
                        st.markdown("#### 📢 Financial Highlights & Public Records")
                        for info in business_info.important_public_information:
                            st.markdown(f"🔹 {info}")
            else:
                st.warning("Overview object payload missing data fields.")
 
        # TAB 2: Business Challenges
        with tab2:
            challenges_data: AnalystOutputSchema = master_state.get("business_challenges")
            if challenges_data and challenges_data.challenges:
                st.subheader("🛑 Identified Bottlenecks & Friction Points")
                
                # 2x2 Grid Layout
                col_c1, col_c2 = st.columns(2)
                for i, challenge in enumerate(challenges_data.challenges):
                    target_col = col_c1 if i % 2 == 0 else col_c2
                    
                    badge_cls = "badge-op"
                    if challenge.category == "Operational Bottleneck":
                        badge_cls = "badge-op"
                    elif challenge.category == "Sales Challenge":
                        badge_cls = "badge-sales"
                    elif challenge.category == "Customer Experience Challenge":
                        badge_cls = "badge-cx"
                    else:
                        badge_cls = "badge-gen"
                        
                    with target_col:
                        st.markdown(f"""
                        <div class="glass-card">
                            <span class="{badge_cls}">{challenge.category}</span>
                            <h4 style="margin-top:0px; margin-bottom:12px;">{challenge.title}</h4>
                            <p style="color:#cbd5e1; font-size:0.95rem; line-height:1.6; margin-bottom:14px;"><strong>Challenge:</strong> {challenge.description}</p>
                            <p style="font-size:0.85rem; color:#94a3b8; border-top:1px solid rgba(255,255,255,0.06); padding-top:12px; font-style:italic; margin:0;">
                                🔎 <strong>Reasoning & Analysis:</strong> {challenge.reasoning}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No validated friction point records returned.")
 
        # TAB 3: Targeted AI Blueprints
        with tab3:
            solutions_data: ArchitectOutputSchema = master_state.get("ai_opportunities")
            if solutions_data and solutions_data.solutions:
                st.subheader("⚙️ Tactical Technical AI Architectures")
                
                for i, solution in enumerate(solutions_data.solutions):
                    with st.container(border=True):
                        st.markdown(f"### Blueprint {i+1}: {solution.title}")
                        
                        col_s1, col_s2 = st.columns([1, 2])
                        with col_s1:
                            st.markdown(f"**🎯 Resolves Challenge:**")
                            st.caption(solution.mapped_challenge_title)
                            
                            st.markdown(f"**📂 Operations Domain:**")
                            st.markdown(f"<span class='badge-gen'>{solution.domain}</span>", unsafe_allow_html=True)
                            
                            st.markdown(f"**🛠️ Architecture Frameworks:**")
                            st.code(solution.technical_mechanism, language="text")
                        with col_s2:
                            st.markdown("**🔄 Enterprise Operational Flow Routing:**")
                            st.markdown(solution.operational_flow)
            else:
                st.warning("No technical design records were produced.")
 
        # TAB 4: Executive Pitch Memo
        with tab4:
            pitch_data: CEOPitchSchema = master_state.get("ceo_pitch")
            if pitch_data:
                st.subheader("🎯 Outbound Enterprise Pitch Memo")
                
                with st.container(border=True):
                    st.markdown(f"**📧 Subject:** `{pitch_data.subject_line}`")
                    st.markdown(f"**📝 Executive Summary:** {pitch_data.executive_summary}")
                
                st.markdown(f"""
                <div class="letter-box">
{pitch_data.pitch_letter}
                </div>
                """, unsafe_allow_html=True)
                
                # Dynamic Markdown Downloader
                pitch_download_payload = f"""# Executive Pitch: {company_input}
**Subject:** {pitch_data.subject_line}
**Executive Summary:** {pitch_data.executive_summary}
 
---
 
{pitch_data.pitch_letter}
"""
                st.divider()
                st.download_button(
                    label="📥 Download CEO Pitch Memo (.md)",
                    data=pitch_download_payload,
                    file_name=f"CEO_Pitch_Memo_{company_input.replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            else:
                st.warning("Executive sales pitch generation aborted due to state field validation failure.")
 
if __name__ == "__main__":
    main()
