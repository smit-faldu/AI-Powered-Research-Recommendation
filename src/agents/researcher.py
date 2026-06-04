import traceback
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
from src.state import AgentState
from src.schemas import QueryGenerationSchema, CompanyOverviewSchema, KeyBusinessInformationSchema, CompanyWebsiteExtractionSchema
from src.utils import get_llm, execute_robust_search, crawl_website_text, find_about_page_url, log_scraped_data

def dynamic_researcher_node(state: AgentState) -> dict:
    """Agentic Researcher: Generates queries and extracts Overview and Key Business Info."""
    company = state["company_name"]
    attempts = state.get("research_attempts", 0) + 1
    
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
    search_tool = DuckDuckGoSearchResults(api_wrapper=wrapper)
    llm = get_llm(temperature=0.1)
    
    raw_data = ""
    error_logs = []
    
    # 1. Search for and crawl the official website homepage and about page
    website_url = None
    website_content = ""
    try:
        website_search_results = wrapper.results(f"{company} official website homepage", max_results=5)
        search_formatted = ""
        for idx, res in enumerate(website_search_results):
            search_formatted += f"[{idx+1}] Title: {res.get('title')}\nURL: {res.get('link')}\nSnippet: {res.get('snippet')}\n\n"
        
        if search_formatted:
            log_scraped_data("DuckDuckGo Website Search API", f"{company} official website homepage", search_formatted)
            url_extractor_prompt = (
                f"You are an expert entity resolver. Based on these search results, identify the official website homepage URL for '{company}'. "
                f"Verify that it is the main official corporate domain of '{company}' and not an article, Wikipedia page, or third-party listing.\n\n"
                f"Search Results:\n{search_formatted}\n"
                f"Provide the exact absolute URL of the official homepage, or an empty string if no clear official homepage is found."
            )
            structured_url_extractor = llm.with_structured_output(CompanyWebsiteExtractionSchema)
            extracted_url_obj = structured_url_extractor.invoke(url_extractor_prompt)
            website_url = extracted_url_obj.official_website_url.strip() if extracted_url_obj else None
            
            if website_url:
                homepage_text, homepage_soup = crawl_website_text(website_url)
                if not homepage_text.startswith("Crawl failed"):
                    website_content += f"### Official Homepage Content ({website_url}):\n{homepage_text}\n\n"
                    
                    if homepage_soup:
                        about_url = find_about_page_url(homepage_soup, website_url)
                        if about_url:
                            about_text, _ = crawl_website_text(about_url)
                            if not about_text.startswith("Crawl failed"):
                                website_content += f"### Official About/Profile Page Content ({about_url}):\n{about_text}\n\n"
                else:
                    error_logs.append(homepage_text)
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Researcher Agent - Website Crawl Exception", company, tb_str)
        error_logs.append(f"Official website crawling failed for '{company}': {str(e)}")
        
    if website_content:
        raw_data += f"## OFFICIAL WEBSITE DIRECTLY CRAWLED DATA\n{website_content}\n\n"
    
    # 2. Generate standard search queries for additional news/expansion plans
    query_gen_prompt = (
        f"Identify core business information, offerings, recent developments, expansion plans, "
        f"and public financial data for '{company}'. Generate 3 targeted distinct search query strings."
    )
    if attempts > 1:
        query_gen_prompt += " Adjust search terms to focus on news updates, press releases, or specific geographic regions to avoid rate limit or empty blocks."

    try:
        structured_queries = llm.with_structured_output(QueryGenerationSchema)
        query_obj = structured_queries.invoke(query_gen_prompt)
        queries = query_obj.queries
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Researcher Agent - Query Generation Exception", company, tb_str)
        queries = [
            f"{company} company profile overview business scale",
            f"{company} recent news developments products",
            f"{company} expansion plans projects public info"
        ]

    for q in queries:
        try:
            result = execute_robust_search(search_tool, q)
            raw_data += f"### Query: {q}\n{result}\n\n"
        except Exception as e:
            error_logs.append(f"Search loop {attempts} failed query '{q}': {str(e)}")

    if not raw_data.strip() or len(raw_data) < 200:
        fallback_query = f"{company} business overview developments"
        try:
            result = execute_robust_search(search_tool, fallback_query)
            raw_data += f"### Fallback Query: {fallback_query}\n{result}\n\n"
        except Exception as e:
            error_logs.append(f"Fallback search failed: {str(e)}")

    # Extract CompanyOverviewSchema
    overview_prompt = f"Analyze this profile information for {company} and extract a clean corporate overview:\n\n{raw_data}"
    try:
        structured_overview = llm.with_structured_output(CompanyOverviewSchema)
        overview = structured_overview.invoke(overview_prompt)
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Researcher Agent - Overview Extraction Exception", company, tb_str)
        overview = CompanyOverviewSchema(
            description=f"Overview extraction failed. {company} is a business enterprise.",
            industry="Unknown Sector",
            scale="Unavailable",
            geographic_presence="Global / Regional"
        )
        error_logs.append(f"Overview extraction error: {str(e)}")

    # Extract KeyBusinessInformationSchema
    business_info_prompt = f"Analyze this profile information for {company} and extract key business information including offerings, news, expansion, and public facts:\n\n{raw_data}"
    try:
        structured_business_info = llm.with_structured_output(KeyBusinessInformationSchema)
        business_info = structured_business_info.invoke(business_info_prompt)
    except Exception as e:
        tb_str = traceback.format_exc()
        log_scraped_data("Researcher Agent - Business Info Extraction Exception", company, tb_str)
        business_info = KeyBusinessInformationSchema(
            major_offerings=["Sweep failed, core products unavailable"],
            recent_developments=["Recent developments unavailable in current search block"],
            expansion_plans=["Expansion plans not specified or sweep failed"],
            important_public_information=["Public information sweep failed"]
        )
        error_logs.append(f"Business info extraction error: {str(e)}")

    # Log outputs
    overview_str = overview.model_dump_json(indent=2) if hasattr(overview, 'model_dump_json') else str(overview)
    business_info_str = business_info.model_dump_json(indent=2) if hasattr(business_info, 'model_dump_json') else str(business_info)
    
    log_scraped_data("Researcher Agent - Company Overview", company, overview_str)
    log_scraped_data("Researcher Agent - Key Business Info", company, business_info_str)

    return {
        "raw_research_data": raw_data, 
        "company_overview": overview,
        "key_business_info": business_info,
        "research_attempts": attempts,
        "error_logs": error_logs
    }
