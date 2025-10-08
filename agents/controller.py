import datetime
import json
import os

LOG_FILE = "logs/traces.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def route_query(query, pdf_uploaded):
    """Decide agents to call based on rules."""
    q = query.lower()
    if pdf_uploaded and "summarize" in q:
        agents = ["PDF_RAG"]
        rationale = "PDF uploaded and query requests summary → use PDF_RAG"
    elif "recent papers" in q or "arxiv" in q or "paper" in q:
        agents = ["ARXIV"]
        rationale = "Query about recent papers or arXiv → use ARXIV agent"
    elif "latest news" in q or "recent developments" in q:
        agents = ["WEB_SEARCH"]
        rationale = "Query about news or recent developments → use WEB_SEARCH"
    else:
        agents = ["WEB_SEARCH"]
        rationale = "No special keywords → default to WEB_SEARCH"
    return {"agents_to_call": agents, "rationale": rationale}

def log_trace(query, route, agent_responses):
    timestamp = datetime.datetime.utcnow().isoformat()
    trace_entry = {
        "timestamp": timestamp,
        "input": query,
        "decision": route,
        "agent_responses": agent_responses
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace_entry) + "\n")

def synthesize_answer(query, responses):
    """Placeholder for LLM synthesis logic."""
    # For now, concatenate agent results
    answers = []
    for agent, result in responses.items():
        answers.append(f"[{agent}]: {result}")
    return "\n\n".join(answers)

def get_traces(n=10):
    """Return last n log traces."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_lines = lines[-n:]
        return [json.loads(line) for line in last_lines]

if __name__ == "__main__":
    # Basic test
    test_query = "Summarize this PDF please"
    route = route_query(test_query, pdf_uploaded=True)
    print("Routing decision:", route)
    log_trace(test_query, route, {"PDF_RAG": "Sample response"})
    print("Last traces:", get_traces(1))
