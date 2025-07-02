import os 
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv

load_dotenv()

class FirecrawlService: #firecrawl service class set up so we can start using firecrawlapp
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.app = FirecrawlApp(api_key=api_key) #initialize firecrawl app python sdk

    def search_companies(self, query: str, num_results: int = 5): #find the website
        try:
            result = self.app.search(
                query=f"{query} company pricing", 
                limit=num_results,
                scrape_options=ScrapeOptions(
                    formats=["markdown"], #usually most useful for LLMs
                )
            )
            return result #pricing results 
        except Exception as e:
            print(f"Error searching companies: {e}")
            return []
        
    def scrape_company_pages(self, url: str): #already know website given url
        try:
            result = self.app.scrape_url(
                url,
                formats=["markdown"], #usually most useful for LLMs
            )
            return result
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return []
        