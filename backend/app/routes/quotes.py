# backend/app/routes/quotes.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from .. import quotes_storage
from ..schemas_api import (
    SavedQuote,
    SavedQuoteCreate,
    SavedQuoteList,
)


router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("", response_model=SavedQuoteList)
def list_quotes(
    project: str | None = None,
    industry: str | None = None,
    search: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> SavedQuoteList:
    return quotes_storage.list_all(project, industry, search, limit, offset)


@router.post("", response_model=SavedQuote, status_code=status.HTTP_201_CREATED)
def create_quote(payload: SavedQuoteCreate) -> SavedQuote:
    return quotes_storage.create(payload)


@router.get("/{quote_id}", response_model=SavedQuote)
def get_quote(quote_id: str) -> SavedQuote:
    q = quotes_storage.get(quote_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return q


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(quote_id: str) -> Response:
    if not quotes_storage.delete(quote_id):
        raise HTTPException(status_code=404, detail="Quote not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{quote_id}/duplicate", response_model=SavedQuote, status_code=status.HTTP_201_CREATED)
def duplicate_quote(quote_id: str) -> SavedQuote:
    q = quotes_storage.duplicate(quote_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return q
