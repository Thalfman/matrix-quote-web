"""Admin routes (login, train, dataset, drivers, similar, overview, reset).

All /api/admin/* routes except /login depend on require_admin.
Most handlers are stubbed (501) at the scaffold stage — subsequent vertical
slices fill them in per the approved plan.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from .. import demo
from ..deps import (
    Settings,
    create_admin_token,
    get_settings,
    require_admin,
    verify_admin_password,
)
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    token, expires_at = create_admin_token(settings, display_name=body.name or "admin")
    return LoginResponse(token=token, expires_at=expires_at)


_NOT_IMPLEMENTED_DETAIL = "Pending vertical slice"


def _not_implemented() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_NOT_IMPLEMENTED_DETAIL,
    )


@router.post("/train/preview", response_model=TrainPreviewResponse)
def train_preview(_: dict = Depends(require_admin)) -> TrainPreviewResponse:
    raise _not_implemented()


@router.post("/train", response_model=TrainResponse)
def train(_: dict = Depends(require_admin)) -> TrainResponse:
    raise _not_implemented()


@router.get("/dataset", response_model=DatasetPage)
def dataset(_: dict = Depends(require_admin)) -> DatasetPage:
    raise _not_implemented()


@router.get("/drivers/{op}", response_model=DriversResponse)
def drivers(op: str, _: dict = Depends(require_admin)) -> DriversResponse:
    raise _not_implemented()


@router.post("/similar", response_model=SimilarResponse)
def similar(body: SimilarRequest, _: dict = Depends(require_admin)) -> SimilarResponse:
    raise _not_implemented()


@router.get("/overview", response_model=OverviewResponse)
def overview(_: dict = Depends(require_admin)) -> OverviewResponse:
    raise _not_implemented()


@router.post("/reset/prepare", response_model=ResetPrepareResponse)
def reset_prepare(_: dict = Depends(require_admin)) -> ResetPrepareResponse:
    raise _not_implemented()


@router.post("/reset")
def reset(body: ResetRequest, _: dict = Depends(require_admin)) -> dict:
    raise _not_implemented()


@router.post("/demo/load", response_model=DemoLoadResponse)
def load_demo(_: dict = Depends(require_admin)) -> DemoLoadResponse:
    loaded, reason = demo.seed_on_demand()
    return DemoLoadResponse(loaded=loaded, reason=reason)
