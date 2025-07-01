from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.message import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FirecrawlService
from .prompts import DeveloperToolsPrompts

class ResearchWorkflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow() #private method below
    
    def _build_workflow(self):
        pass
    #workflow step 1
    def _extract_tools_steps(self, state: ResearchState) -> Dict[str, Any]: #leading with _ means private method not to be called outside of class, each function is a node/stages in langgraph which needs a stage, we update state here
        print(f"Finding articles about: {state.query}")

        article_query = f"{state.query} tools comparison best alternatives" #looks up articles based on user query
        search_results = self.firecrawl.search_companies(article_query, num_results=3) #passes markdown files to LLM

        all_content = "" #stores all content from articles as a string
        for result in search_results.data: #goes through each result
            url = result.get("url", "") #gets url from article results markdown
            scraped = self.firecrawl.scrape_company_pages(url) #scrapes data from page
            if scraped:
                all_content + scraped.markdown[:1500] + "\n\n" #stores content in all_content

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM), #defined in prompt.py
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content)),
        ] #wrap both system and user messages in a list so it can be passed to LLM at once
        
        try:
            response = self.llm.invoke(messages) #invokes LLM
            tool_names =[
                name.strip()
                for name in response.content.split("\n")
                if name.strip()
            ]
            print(f"Extracted tools: {', '.join(tool_names[:5])}") #returns extracted tools
            return {"extracted_tools": tool_names} #langgrapgh updates research state
        except Exception as e:
            print(f"Error extracting tools: {e}")
            return {"extracted_tools": []} #can still move on to the next step
    #workflow step 2
    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis: #helper method that will help with our steps by returning company analysis model
        sturctured_llm = self.llm.with_structured_output(CompanyAnalysis) #wraps llm with structured output as defined in CompanyAnalysis

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content)), #takes company name and content, conver to company analysis object as defined data model
        ]
        try:
            analysis = sturctured_llm.invoke(messages) #structed llm we defined earlier
            return analysis
        except Exception as e:
            print(f"Error analyzing company content: {e}")
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed to analyze content",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            ) #returns empty model

    def _research_step(self, state: ResearchState) -> Dict[str, Any]: #research step
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools: #edge case handling
            print("No tools extracted, falling back to direct search.")
            search_results = self.firecrawl.search_companies(state.query, num_results=5)
            tool_names =[
                result.get("metadata", {}).get("title", "Unknown")
                for result in search_results.data
            ]
        else:
            tool_names = extracted_tools[:5]

        print("Researching specific tools:", {','.join(tool_names)})   

        companies =[]
        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site", num_results=1)
           