from ddgs import DDGS

def handle_query(query, max_results=5):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query):
            results.append(r)
            if len(results) >= max_results:
                break
    if not results:
        return "No results from web search."
    summaries = []
    for res in results:
        title = res.get("title", "")
        snippet = res.get("body", "")
        url = res.get("url", "")
        summaries.append(f"{title}\n{snippet}\n{url}\n")
    return "\n---\n".join(summaries)

if __name__ == "__main__":
    print(handle_query("latest developments in NLP 2025"))

