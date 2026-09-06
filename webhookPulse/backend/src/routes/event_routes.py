from fastapi import APIRouter, Depends

from src.controllers.event_controller import replay
from src.core.dependencies import get_current_user


router = APIRouter(
    prefix="/events",
    tags=["Events"],
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