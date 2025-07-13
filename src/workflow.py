from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FirecrawlService
from .prompts import DeveloperToolsPrompts

class ResearchWorkflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow() #private method below
    
    def _build_workflow(self): #LAST STEP: finally go back to langgraph and build workflow
        graph = StateGraph(ResearchState)

        graph.add_node("extract_tools", self._extract_tools_step) #create nodes for each step
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools") #1st entry point we want to begin and then order of execution
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()
     
    #node #1
    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]: #leading with _ means private method not to be called outside of class, each function is a node/stages in langgraph which needs a stage, we update state here
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
   #helper function not a node
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
    #node #2
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
        for tool_name in tool_names: #loolkup official site of tool for every tool
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site", num_results=1)
            
            if tool_search_results:
                result = tool_search_results.data[0]
                url = result.get("url", "") #get url of official site
                
                company= CompanyInfo( #set up company info object
                    name=tool_name,
                    description=result.get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[],
                )

                scraped = self.firecrawl.scrape_company_pages(url) #scrape content from official site
                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content) #lllm to analyze content
                    #update company info with analysis
                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company) #put llm analyzed result back to companies list

        return {"companies": companies}
    #node #3
    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print ("Gnerating recommendations")

        company_data = ", ".join([
            company.json() for company in state.companies #look through all companies and convert to json
        ])

        messages = [ #pass data to llm
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data)),
        ]

        response = self.llm.invoke(messages)
        return {"analysis": response.content}
    
    def run(self, query: str) -> ResearchState: #run langgrpah grapgh for us
        initial_state = ResearchState (query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state) #convert dict into python object with custom class