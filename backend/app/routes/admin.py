"""Admin routes (login, train, dataset, drivers, similar, overview, reset).

All /api/admin/* routes except /login depend on require_admin.
Most handlers are stubbed (501) at the scaffold stage — subsequent vertical
slices fill them in per the approved plan.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ..deps import (
    Settings,
    create_admin_token,
    get_settings,
    require_admin,
    verify_admin_password,
)
from .. import demo
from ..schemas_api import (
    DatasetPage,
    DemoLoadResponse,
    DriversResponse,
    LoginRequest,
    LoginResponse,
    OverviewResponse,
    ResetPrepareResponse,
    ResetRequest,
    SimilarRequest,
    SimilarResponse,
    TrainPreviewResponse,
    TrainResponse,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponse:
    if not verify_admin_password(settings, body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    token, expires_at = create_admin_token(settings)
    return LoginResponse(token=token, expires_at=expires_at)


@router.post("/train/preview", response_model=TrainPreviewResponse)
def train_preview(_: str = Depends(require_admin)) -> TrainPreviewResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.post("/train", response_model=TrainResponse)
def train(_: str = Depends(require_admin)) -> TrainResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.get("/dataset", response_model=DatasetPage)
def dataset(_: str = Depends(require_admin)) -> DatasetPage:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.get("/drivers/{op}", response_model=DriversResponse)
def drivers(op: str, _: str = Depends(require_admin)) -> DriversResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.post("/similar", response_model=SimilarResponse)
def similar(body: SimilarRequest, _: str = Depends(require_admin)) -> SimilarResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.get("/overview", response_model=OverviewResponse)
def overview(_: str = Depends(require_admin)) -> OverviewResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.post("/reset/prepare", response_model=ResetPrepareResponse)
def reset_prepare(_: str = Depends(require_admin)) -> ResetPrepareResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.post("/reset")
def reset(body: ResetRequest, _: str = Depends(require_admin)) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pending vertical slice")


@router.post("/demo/load", response_model=DemoLoadResponse)
def load_demo(_: str = Depends(require_admin)) -> DemoLoadResponse:
    loaded, reason = demo.seed_on_demand()
    return DemoLoadResponse(loaded=loaded, reason=reason)
