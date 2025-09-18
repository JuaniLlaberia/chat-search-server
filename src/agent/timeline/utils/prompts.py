from langchain_core.prompts import ChatPromptTemplate

TIMELINE_PROMPT = ChatPromptTemplate.from_template("""
You are a timeline builder expert. Your task is to build a timeline based on the user query and collected data.

User query: {user_query}
Search information: {search_info}

Rules:

- Present events strictly in chronological order (earliest to latest).
- Each event must include:
    - `start_date`: an exact date in `YYYY-MM-DD` format.
    - `end_date`: an exact date in `YYYY-MM-DD` format if the event spans multiple days, or `null` if it is a single-day event.
- Use a consistent format for each entry:
- Only include verified facts found in `search_info` or clearly implied by it. If something is uncertain, label it as “(approx.)”.
- If `improvements` is provided, incorporate them while keeping chronology and clarity intact.
- Keep language neutral, factual, and concise (no more than 2 sentences per entry).
- Do not add commentary, opinions, or unrelated details.
- If there are gaps or missing dates, note them as “Date unknown” instead of guessing.
- Length requirement: produce a reasonably detailed timeline with **at least 6 events and no more than 20 events**.

Improvement notes (optional):
If `improvements` is provided, integrate them into the new timeline:
{improvements}
""")

EVALUATE_TIMELINE_PROMPT = ChatPromptTemplate.from_template("""
You are a timeline builder and evaluator expert.
Your task is to assess the quality of the following timeline and it's events, then provide a score and improvement suggestions.

Scoring criteria (0 to 1 scale):
- Chronology (0-0.25): Are all events in correct chronological order? Full points if perfectly ordered.
- Accuracy (0-0.25): Are the dates and descriptions factually correct and consistent with the known data?
- Clarity & Conciseness (0-0.20): Are events described in clear, neutral, and concise language (≤2 sentences)?
- Completeness (0-0.20): Does the timeline include all key events from the provided information without major omissions?
- Formatting & Consistency (0-0.10): Are dates formatted uniformly (e.g., `YYYY-MM-DD`) and entries presented in a consistent style?

Instructions:
- Provide a 'score' between 0 (very poor) and 1 (perfect).
- If applicable, provide a list of 'improvements' to make the timeline better.
- If the timeline is already optimal, return an empty list for 'improvements'

Timeline events: {events}
""")