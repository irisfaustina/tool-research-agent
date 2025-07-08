# Tool Researcher Agent

A developer-focused research agent that leverages LLMs and web scraping to analyze, compare, and recommend developer tools, platforms, and services. Designed to help developers quickly discover the best tools for their needs, with actionable insights and concise recommendations.

---

## 🚀 Main Features

- **Automated Tool Discovery:**
  - Extracts relevant developer tools, libraries, and platforms from web articles and comparison posts.
- **In-Depth Analysis:**
  - Scrapes official websites and analyzes content using LLMs to extract pricing, open source status, tech stack, API availability, language support, and integration capabilities.
- **Structured Output:**
  - Presents results in a structured, developer-friendly format with key details for each tool.
- **Actionable Recommendations:**
  - Provides concise, senior-engineer-level recommendations tailored to the developer's query.
- **Robust Workflow:**
  - Utilizes a multi-stage workflow (extraction, research, analysis) powered by [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain).

---

## 🛠️ Tech Stack

- **Python 3.13+**
- [Firecrawl Python SDK](https://github.com/firecrawl/firecrawl-py) (`firecrawl-py`)
- [LangChain](https://github.com/langchain-ai/langchain) & [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI LLMs](https://platform.openai.com/docs/models)
- [Pydantic](https://docs.pydantic.dev/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/tool-researcher-agent.git
   cd tool-researcher-agent
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or, if using poetry:
   poetry install
   ```
3. **Set up environment variables:**
   - Create a `.env` file in the project root with your Firecrawl and OpenAI API keys:
     ```env
     FIRECRAWL_API_KEY=your_firecrawl_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

---

## 🏃 Usage

Run the agent from the command line:

```bash
python main.py
```

- Enter your developer tools query (e.g., "best feature flag platforms", "alternatives to Postman").
- The agent will:
  1. Search and extract relevant tools from articles.
  2. Scrape and analyze official tool websites.
  3. Present structured results and a concise recommendation.
- Type `quit` or `exit` to stop.

---

## 📋 Example Output

```
🔍 Developer Tools Query: best feature flag platforms

📊 Results for: best feature flag platforms
============================================================

1. 🏢 LaunchDarkly
   🌐 Website: https://launchdarkly.com
   💰 Pricing: Paid
   📖 Open Source: False
   🛠️  Tech Stack: Go, React, AWS
   💻 Language Support: Python, JavaScript, Java
   🔌 API: ✅ Available
   🔗 Integrations: GitHub, Slack, Jira
   📝 Description: Feature management platform for modern development teams.

Developer Recommendations:
----------------------------------------
LaunchDarkly is the top choice for robust feature flag management, offering strong integration and language support. Pricing is enterprise-focused. Its main advantage is reliability and developer experience.
```

---

## 🤖 How It Works

- **Workflow:**
  1. **Extract Tools:** Finds relevant tools from articles using Firecrawl and LLM extraction.
  2. **Research:** Scrapes official sites and analyzes content for developer-relevant details.
  3. **Analyze:** LLM generates a concise recommendation based on structured data.
- **Prompt Engineering:** Custom prompts ensure developer-focused, actionable outputs.
- **Extensible:** Easily adaptable for other research domains or LLM providers.

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.
