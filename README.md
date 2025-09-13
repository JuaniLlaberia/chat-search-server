# LangGraph Web Search Agent

This repository contains a configurable LangGraph agent designed to search the internet and return concise, sourced answers, images and related links. The agent behaves like a high-quality web research assistant: it issues web queries, evaluates sources, synthesizes results, and returns short summaries with references, sources, images and follow-up suggestions.

Key design goals:

* Fast, relevant answers to user questions.
* Transparent sourcing (show where results came from).
* Related images and sites.
* Different tools (Finance, weather, time, etc.)
* Web search
  
### Related repositories

Front-end application: [Web Search Agent Frontend](https://github.com/JuaniLlaberia/chat-search-client)

<details>
  <summary>▶️ Watch Demo (1.2x speec)</summary>
  
  https://github.com/user-attachments/assets/f371ea5d-6430-4dca-9e1d-206c990a678d


</details>

---

## 🚀 Features

* Natural-language Q/A over live web search results.
* FastAPI + LangGraph multi-agent architecture
* Web search with Tavily (content, images and sources extraction)
* Data extraction and synthesis
* Citation gathering and ranking
* Streaming responses with SSE for real-time UI updates
* Modular design → easily extendable with new tools/agents
* Transparent reasoning: exposes underlying sources

---
## 📦 Installation & Usage
1. Clone the repo:
   ```bash
   git clone https://github.com/JuaniLlaberia/chat-search-server.git
   cd chat-search-server
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Agent locally (FastAPI):

   ```bash
   python .
   ```
---

## 🗝️ Environment variables

* `GOOGLE_API_KEY` — Gemini API key from google.
* `MODEL_NAME` — Gemini model name to use.
* `TAVILY_SEARCH` — Tavily search API key.

