import arxiv

def handle_query(query, max_results=5):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    summaries = []
    for result in search.results():
        title = result.title
        summary = result.summary.replace('\n', ' ').strip()
        url = result.entry_id
        summaries.append(f"{title}\n{summary}\n{url}\n")
    if not summaries:
        return "No recent papers found on ArXiv."
    return "\n---\n".join(summaries)

if __name__ == "__main__":
    print(handle_query("machine learning"))
