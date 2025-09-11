# LangGraph Web Search Agent (Finder)

Related repositories

Frontend (UI): [Web Search Agent Frontend](https://github.com/JuaniLlaberia/chat-search-client)

## Project overview

This repository contains a configurable LangGraph agent designed to search the internet and return concise, sourced answers and related links. The agent behaves like a high-quality web research assistant: it issues web queries, evaluates sources, synthesizes results, and returns short summaries with references and follow-up suggestions.

Key design goals:

* Fast, relevant answers to user questions.
* Transparent sourcing (show where results came from).
* Extensible toolset (search engines, browser, site-specific scrapers).
* Safe defaults (rate limits, content filters, refusal policies).

---

## Features

* Natural-language Q/A over live web search results.
* Multi-source aggregation with scoring and de-duplication.
* Citation-aware responses.
* Rate-limiting and politeness options for scrapers and browser tools.

---

## Architecture (high level)

1. **Client UI**: a simple chat interface that accepts user queries and displays agent replies and citations.
2. **LangGraph Agent**: orchestrates tools (search, browser, scraper, summarizer) and composes the final answer.
3. **Tools / Connectors**:
   * *Search tool(s)*: external search engine API(s) or self-hosted index.
   * (Can add more)
4. **Evaluator & Synthesizer**: ranks candidates, removes duplicates, crafts the final natural-language response, and generates citations.

---

## Environment variables

* `GOOGLE_API_KEY` — gemini API key from google.
* `MODEL_NAME` — gemini model name to use.

