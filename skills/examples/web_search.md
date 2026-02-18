# Web Search Skill

**Keywords:** search, google, find, look up, research, web, internet
**Triggers:** "search for", "look up", "find information about", "google"

## Description
Performs web searches and retrieves information from the internet.

## Instructions for AI

When the user asks to search for something:

1. **Identify the search query** from their request
2. **Use Brave browser** (via browser container) to perform the search
3. **Extract key information** from results
4. **Summarize findings** in a clear, concise way
5. **Cite sources** when providing facts

## Parameters
- `query`: The search term or question (required)
- `num_results`: Number of results to return (default: 3)

## Example Usage

User: "Search for the latest news on AI"
Action: Use Brave Search to find "latest AI news"
Response: Provide 3-5 key recent developments with sources

User: "Look up the weather in San Francisco"
Action: Use Brave to search weather SF
Response: Current weather + forecast

## Output Format
Always include:
- Summary of findings
- Key facts/data points
- Source URLs
- Timestamp of search

