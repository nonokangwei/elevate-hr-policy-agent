"""Track A — RAG retrieval tool (Vertex AI Search).

The agent uses this to semantically search the handbook corpus you ingested into
a Vertex AI Search data store (see rag/). It returns grounded context + citations.

Prerequisite: complete rag/README.md (provision, ingest, verify) first.
"""
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

from .. import config

_client = None


def _get_client():
    global _client
    if _client is None:
        location = config.VERTEX_AI_SEARCH_LOCATION
        opts = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        _client = discoveryengine.SearchServiceClient(client_options=opts)
    return _client


def search_policy_docs(query: str) -> dict:
    """Semantic search over the HR policy corpus in Vertex AI Search.

    Args:
        query: a natural-language policy question or search phrase.

    Returns:
        {"grounded_context": str, "citations": [str, ...]}
    """
    serving_config = (
        f"projects/{config.GOOGLE_CLOUD_PROJECT}/locations/{config.VERTEX_AI_SEARCH_LOCATION}"
        f"/collections/default_collection/engines/{config.VERTEX_AI_SEARCH_ENGINE_ID}"
        f"/servingConfigs/default_search"
    )
    content_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_answer_count=3,
            max_extractive_segment_count=3,
        )
    )
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=3,
        content_search_spec=content_spec,
    )

    try:
        response = _get_client().search(request)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Vertex AI Search failed: {e}"}

    context_parts: list[str] = []
    citations: list[str] = []
    for result in response.results:
        d = result.document.derived_struct_data
        title = d.get("title", "Untitled")
        link = d.get("link")
        for seg in d.get("extractive_segments", []) or []:
            content = seg.get("content", "")
            if content:
                context_parts.append(f"[{title}]\n{content}")
        for ans in d.get("extractive_answers", []) or []:
            content = ans.get("content", "")
            if content:
                context_parts.append(f"[{title}]\n{content}")
        if link and link not in citations:
            citations.append(link)

    return {
        "grounded_context": "\n\n---\n\n".join(context_parts) if context_parts else "",
        "citations": citations,
    }
