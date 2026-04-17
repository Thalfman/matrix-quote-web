"""Public quote prediction routes."""

from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from core.config import QUOTE_CAT_FEATURES, QUOTE_NUM_FEATURES
from service.predict_lib import predict_quote, predict_quotes_df

from .. import storage
from ..schemas_api import QuoteInput, QuotePrediction

router = APIRouter(prefix="/api/quote", tags=["quote"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/single", response_model=QuotePrediction)
def single_quote(payload: QuoteInput) -> QuotePrediction:
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
    return pred


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
def batch_preview(file: UploadFile = File(...)) -> dict:
    raw = file.file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB).")
    buf = io.BytesIO(raw)
    xls = pd.ExcelFile(buf)
    columns_per_sheet: dict[str, list[str]] = {}
    for s in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=s, nrows=0)
        columns_per_sheet[s] = df.columns.astype(str).tolist()
    return {"sheets": xls.sheet_names, "columns_per_sheet": columns_per_sheet}


@router.post("/batch")
def batch_quote(
    file: UploadFile = File(...),
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
