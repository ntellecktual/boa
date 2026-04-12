"""
RAG (Retrieval-Augmented Generation) engine for the chatbot.
Uses ChromaDB for vector storage and Anthropic/OpenAI for generation.
"""

import hashlib
import logging
import os
from pathlib import Path

import nbformat
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy-loaded globals
_chroma_client = None
_embedding_fn = None


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        import chromadb

        persist_dir = str(settings.CHROMADB_PERSIST_DIR)
        os.makedirs(persist_dir, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
    return _chroma_client


def _get_embedding_function():
    global _embedding_fn
    if _embedding_fn is None:
        from chromadb.utils import embedding_functions

        _embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    return _embedding_fn


def _collection_name_for_document(document_id):
    return f'doc_{document_id}'


def index_document(document_id):
    """Index a document's notebook content into ChromaDB for RAG retrieval."""
    from .models import Document

    doc = Document.objects.get(pk=document_id)
    notebook_path = Path(settings.MEDIA_ROOT) / doc.uploaded_file.name

    if not notebook_path.exists():
        logger.error(f'Notebook not found for indexing: {notebook_path}')
        return

    with open(notebook_path, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Extract chunks from notebook cells
    chunks = []
    chunk_ids = []
    chunk_metadata = []

    for idx, cell in enumerate(nb.cells):
        source = cell.get('source', '').strip()
        if not source:
            continue

        cell_type = cell.get('cell_type', 'unknown')
        chunk_id = hashlib.md5(f'{document_id}_{idx}_{source[:50]}'.encode()).hexdigest()

        chunks.append(source)
        chunk_ids.append(chunk_id)
        chunk_metadata.append(
            {
                'cell_index': idx,
                'cell_type': cell_type,
                'document_id': document_id,
            }
        )

    if not chunks:
        logger.warning(f'No content found in notebook for document {document_id}')
        return

    client = _get_chroma_client()
    collection_name = _collection_name_for_document(document_id)

    # Delete existing collection if present, then create fresh
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=_get_embedding_function(),
    )

    # Add in batches
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        collection.add(
            documents=chunks[i : i + batch_size],
            ids=chunk_ids[i : i + batch_size],
            metadatas=chunk_metadata[i : i + batch_size],
        )

    logger.info(f'Indexed {len(chunks)} chunks for document {document_id}')


def get_rag_response(query, document_id=None):
    """
    Retrieve relevant context from ChromaDB and generate an AI response.
    Returns (response_text, sources_list).
    """
    # --- Dev stub mode: zero API cost ---
    if not getattr(settings, 'USE_LLM', True):
        logger.info('USE_LLM=False — returning stub chat response')
        return (
            f"[DEV MODE] This is a stub response for: '{query}'. Set USE_LLM=True in your .env to enable real AI chat.",
            [],
        )

    context_chunks = []
    sources = []

    if document_id:
        try:
            client = _get_chroma_client()
            collection_name = _collection_name_for_document(document_id)
            collection = client.get_collection(
                name=collection_name,
                embedding_function=_get_embedding_function(),
            )

            results = collection.query(
                query_texts=[query],
                n_results=5,
            )

            if results and results['documents']:
                for doc_text, metadata in zip(results['documents'][0], results['metadatas'][0]):
                    context_chunks.append(doc_text)
                    sources.append(
                        {
                            'cell_index': metadata.get('cell_index'),
                            'cell_type': metadata.get('cell_type'),
                            'preview': doc_text[:100] + '...' if len(doc_text) > 100 else doc_text,
                        }
                    )
        except Exception as e:
            logger.warning(f'RAG retrieval failed for document {document_id}: {e}')

    # Build prompt with context
    context_text = '\n\n---\n\n'.join(context_chunks) if context_chunks else 'No specific notebook context available.'

    system_prompt = (
        'You are a helpful AI teaching assistant for a data science learning platform. '
        'Answer questions based on the notebook content provided as context. '
        "If the context doesn't contain the answer, say so honestly but try to provide helpful general guidance. "
        'Keep answers concise and educational. Use code examples when relevant.'
    )

    user_prompt = f'Context from the notebook:\n\n{context_text}\n\n---\n\nStudent question: {query}'

    # Try Anthropic first, then OpenAI
    response_text = _call_llm(system_prompt, user_prompt)
    return response_text, sources


def _call_llm(system_prompt, user_prompt):
    """Call LLM for response generation. Tries Anthropic, falls back to OpenAI."""
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=1024,
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.warning(f'Anthropic call failed: {e}')

    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    if openai_key:
        try:
            import openai

            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                max_tokens=1024,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f'OpenAI call failed: {e}')

    return "I'm sorry, no AI backend is configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your environment."
