from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from google.cloud import firestore
from google.cloud.firestore import Client

from app import schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user

router = APIRouter(tags=["Leaderboard"])


@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
def read_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db: Client = Depends(get_db),
):
    """
    Return the top ``limit`` leaderboard entries ordered by average score.
    """
    try:
        query = (
            db.collection("leaderboard")
            .order_by("average_score", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        documents = list(query.stream())
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leaderboard: {exc}",
        ) from exc

    entries: List[schemas.LeaderboardEntry] = []
    for index, document in enumerate(documents, start=1):
        payload = document.to_dict() or {}
        entries.append(
            schemas.LeaderboardEntry(
                rank=index,
                user_id=payload.get("user_id", document.id),
                score=float(payload.get("average_score", payload.get("best_score", 0.0))),
            )
        )
    return entries


@router.post("/leaderboard/update")
def adjust_score(
    payload: schemas.ScoreUpdate,
    _: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    Apply a manual score adjustment to a leaderboard entry.
    This requires authentication and is intended for administrative usage.
    """
    doc_ref = db.collection("leaderboard").document(payload.user_id)

    try:
        db.run_transaction(
            lambda transaction: _apply_score_delta(transaction, doc_ref, payload.delta)
        )
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update leaderboard: {exc}",
        ) from exc

    return {"status": "ok"}


def _apply_score_delta(
    transaction: firestore.Transaction,
    doc_ref: firestore.DocumentReference,
    delta: float,
) -> None:
    snapshot = doc_ref.get(transaction=transaction)
    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard entry not found",
        )

    payload = snapshot.to_dict() or {}
    total_score = float(payload.get("total_score", 0.0)) + delta
    submission_count = int(payload.get("submission_count", 1))
    best_score = float(payload.get("best_score", 0.0))

    average_score = total_score / max(submission_count, 1)

    transaction.update(
        doc_ref,
        {
            "total_score": total_score,
            "average_score": average_score,
            "best_score": best_score,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
    )
