"""Public quote prediction routes."""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
from core.config import QUOTE_CAT_FEATURES, QUOTE_NUM_FEATURES
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from service.predict_lib import predict_quote, predict_quotes_df

from .. import storage
from ..pdf import render_quote_pdf
from ..schemas_api import AdHocPdfRequest, ExplainedQuoteResponse, QuoteInput, SavedQuote

router = APIRouter(prefix="/api/quote", tags=["quote"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/single", response_model=ExplainedQuoteResponse)
def single_quote(payload: QuoteInput) -> ExplainedQuoteResponse:
    if not storage.models_ready():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Models are not trained. Please upload a dataset and train first.",
        )
    pred = predict_quote(payload)
    if not pred.ops:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No operation models produced a prediction.",
        )

    # Best-effort explainability. Never fail the quote because of it.
    from ..explain import compute_drivers, compute_neighbors
    try:
        drivers = compute_drivers(payload, top_n=3)
    except Exception:
        drivers = None
    try:
        neighbors = compute_neighbors(payload, k=5)
    except Exception:
        neighbors = None

    return ExplainedQuoteResponse(
        prediction=pred,
        drivers=drivers,
        neighbors=neighbors,
    )


def _read_upload(file: UploadFile, sheet: str | None) -> pd.DataFrame:
    raw = file.file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB).")
    name = (file.filename or "").lower()
    buf = io.BytesIO(raw)
    if name.endswith(".csv"):
        return pd.read_csv(buf)
    try:
        xls = pd.ExcelFile(buf)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}") from exc
    target_sheet = sheet or xls.sheet_names[0]
    if target_sheet not in xls.sheet_names:
        raise HTTPException(status_code=400, detail=f"Sheet '{target_sheet}' not found")
    return pd.read_excel(xls, sheet_name=target_sheet)


@router.post("/batch/preview")
def batch_preview(file: UploadFile = File(...)) -> dict:  # noqa: B008
    raw = file.file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB).")
    buf = io.BytesIO(raw)
    try:
        xls = pd.ExcelFile(buf)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Could not parse file: {exc}"
        ) from exc
    columns_per_sheet: dict[str, list[str]] = {}
    for s in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=s, nrows=0)
        columns_per_sheet[s] = df.columns.astype(str).tolist()
    return {"sheets": xls.sheet_names, "columns_per_sheet": columns_per_sheet}


@router.post("/batch")
def batch_quote(
    file: UploadFile = File(...),  # noqa: B008
    sheet: str | None = Form(None),
) -> StreamingResponse:
    if not storage.models_ready():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Models are not trained. Please upload a dataset and train first.",
        )
    df_in = _read_upload(file, sheet)
    required = set(QUOTE_NUM_FEATURES + QUOTE_CAT_FEATURES)
    missing = sorted(required - set(df_in.columns))
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing}",
        )
    df_out = predict_quotes_df(df_in)
    buf = io.StringIO()
    df_out.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="quote_predictions.csv"'},
    )


@router.post("/pdf")
def adhoc_pdf(payload: AdHocPdfRequest) -> Response:
    # Build a transient SavedQuote so the template doesn't need to branch.
    now = datetime.utcnow()
    transient = SavedQuote(
        id="adhoc",
        created_at=now,
        **payload.model_dump(),
    )
    pdf_bytes = render_quote_pdf(transient, quote_number=f"{now:%Y%m%d}-{now:%H%M}")
    fname = f"Matrix-Quote-{payload.project_name.replace(' ', '-')}-{now:%Y%m%d}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
