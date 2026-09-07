from fastapi import APIRouter, Depends

from src.core.dependencies import get_current_user
from src.controllers.event_controller import (
    get_event,
    get_events,
    replay,
    get_stats,
)


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

@router.get("")
def list_events_route(
    current_user: dict = Depends(get_current_user),
):
    return get_events(
        tenant_id=current_user["tenant_id"],
    )


@router.get("/stats")
def get_event_stats_route(
    current_user: dict = Depends(get_current_user),
):
    return get_stats(
        tenant_id=current_user["tenant_id"],
    )


@router.get("/{event_id}")
def get_event_route(
    event_id: str,
    current_user: dict = Depends(get_current_user),
):
    return get_event(
        event_id=event_id,
        tenant_id=current_user["tenant_id"],
    )


@router.post("/{event_id}/replay")
def replay_event_route(
    event_id: str,
    current_user: dict = Depends(get_current_user),
):
    return replay(
        event_id=event_id,
        tenant_id=current_user["tenant_id"],
    )

