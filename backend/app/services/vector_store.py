from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from app.core.config import settings

CHROMA_DIR = Path("data/chroma")
COLLECTION_NAME = "document_chunks"


def _get_client() -> chromadb.ClientAPI:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _get_or_create_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_document_chunks(
    chunks: list[dict],
    embeddings: list,
    doc_title: str,
    department: str,
) -> None:
    collection = _get_or_create_collection()
    ids = [f"{c['doc_id']}_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "doc_id": c["doc_id"],
            "chunk_index": c["chunk_index"],
            "page_num": c["page_num"],
            "doc_title": doc_title,
            "department": department,
        }
        for c in chunks
    ]
    embeddings_list = [e.tolist() if hasattr(e, "tolist") else e for e in embeddings]
    collection.add(ids=ids, documents=documents, embeddings=embeddings_list, metadatas=metadatas)


def search_similar(
    query_embedding,
    department_filter: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    collection = _get_or_create_collection()
    where = None
    if department_filter and department_filter != "all":
        where = {"department": {"$in": [department_filter, "all"]}}
    results = collection.query(
        query_embeddings=[query_embedding.tolist() if hasattr(query_embedding, "tolist") else query_embedding],
        n_results=top_k,
        where=where,
    )
    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "text": results["documents"][0][i],
            "page_num": results["metadatas"][0][i].get("page_num"),
            "doc_title": results["metadatas"][0][i].get("doc_title"),
            "doc_id": results["metadatas"][0][i].get("doc_id"),
            "score": results["distances"][0][i] if results.get("distances") else 0,
        })
    return output


def delete_document_chunks(doc_id: str) -> None:
    collection = _get_or_create_collection()
    results = collection.get(where={"doc_id": doc_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])
