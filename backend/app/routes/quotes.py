# backend/app/routes/quotes.py
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, status

from .. import quotes_storage
from ..pdf import render_quote_pdf
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


def _quote_number(created_at: datetime) -> str:
    return f"{created_at:%Y%m%d}-{created_at:%H%M}"


@router.get("/{quote_id}/pdf")
def get_quote_pdf(quote_id: str) -> Response:
    q = quotes_storage.get(quote_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    pdf_bytes = render_quote_pdf(q, quote_number=_quote_number(q.created_at))
    fname = f"Matrix-Quote-{q.project_name.replace(' ', '-')}-{q.created_at:%Y%m%d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


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
