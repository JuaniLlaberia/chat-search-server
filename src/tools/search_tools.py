from langchain_community.tools import DuckDuckGoSearchResults

duck_search = DuckDuckGoSearchResults(
    num_results=6,
    output_format="list",
)