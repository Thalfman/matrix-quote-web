# backend/app/routes/quotes.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .. import quotes_storage
from ..deps import require_admin
from ..pdf import render_quote_pdf
from ..quote_ids import safe_filename_part
from ..schemas_api import (
    SavedQuote,
    SavedQuoteCreate,
    SavedQuoteCreateBody,
    SavedQuoteList,
)

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("", response_model=SavedQuoteList)
def list_quotes(
    _claim: Annotated[dict, Depends(require_admin)],
    project: str | None = None,
    industry: str | None = None,
    search: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> SavedQuoteList:
    return quotes_storage.list_all(project, industry, search, limit, offset)


@router.post("", response_model=SavedQuote, status_code=status.HTTP_201_CREATED)
def create_quote(
    body: SavedQuoteCreateBody,
    claim: Annotated[dict, Depends(require_admin)],
) -> SavedQuote:
    payload = SavedQuoteCreate(**body.model_dump(), created_by=claim["name"])
    return quotes_storage.create(payload)


def _quote_number(created_at: datetime) -> str:
    return f"{created_at:%Y%m%d}-{created_at:%H%M}"


@router.get("/{quote_id}/pdf")
def get_quote_pdf(
    quote_id: str,
    _claim: Annotated[dict, Depends(require_admin)],
) -> Response:
    q = quotes_storage.get(quote_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    pdf_bytes = render_quote_pdf(q, quote_number=_quote_number(q.created_at))
    fname = f"Matrix-Quote-{safe_filename_part(q.project_name)}-{q.created_at:%Y%m%d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/{quote_id}", response_model=SavedQuote)
def get_quote(
    quote_id: str,
    _claim: Annotated[dict, Depends(require_admin)],
) -> SavedQuote:
    q = quotes_storage.get(quote_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return q


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: str,
    _claim: Annotated[dict, Depends(require_admin)],
) -> Response:
    if not quotes_storage.delete(quote_id):
        raise HTTPException(status_code=404, detail="Quote not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{quote_id}/duplicate",
    response_model=SavedQuote,
    status_code=status.HTTP_201_CREATED,
)
def duplicate_quote(
    quote_id: str,
    claim: Annotated[dict, Depends(require_admin)],
) -> SavedQuote:
    q = quotes_storage.duplicate(quote_id, created_by=claim["name"])
    if q is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return q
