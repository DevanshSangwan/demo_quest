import logging
import traceback
from typing import Iterable, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from google.cloud import firestore
from google.cloud.firestore import Client

from app import schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

_RANK_HISTORY_COLLECTION = "rank_history"

router = APIRouter(tags=["Leaderboard"])


def _build_leaderboard_entries(
    documents: Iterable[firestore.DocumentSnapshot],
    db: Client,
    start_rank: int = 1,
) -> List[schemas.LeaderboardEntry]:
    entries: List[schemas.LeaderboardEntry] = []
    for offset, document in enumerate(documents):
        payload = document.to_dict() or {}
        user_id = payload.get("user_id", document.id)
        
        # Fetch user's display name from users collection
        display_name = user_id
        try:
            user_doc = db.collection("users").document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict() or {}
                display_name = user_data.get("displayName") or user_data.get("email") or user_id
        except Exception:
            pass  # Fallback to user_id if fetch fails
        
        entries.append(
            schemas.LeaderboardEntry(
                rank=start_rank + offset,
                user_id=user_id,
                display_name=display_name,
                score=float(payload.get("average_score", payload.get("best_score", 0.0))),
            )
        )
    return entries


@router.get("/leaderboard", response_model=List[schemas.LeaderboardEntry])
@router.get("/leaderboard/global", response_model=List[schemas.LeaderboardEntry])
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

    return _build_leaderboard_entries(documents, db)


@router.get("/leaderboard/rank-history", response_model=List[schemas.RankHistoryEntry])
def get_user_rank_history(
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    Return rank history for the current user from daily snapshots.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to identify authenticated user",
        )

    try:
        query = (
            db.collection(_RANK_HISTORY_COLLECTION)
            .where("user_id", "==", user_id)
            .order_by("date")
        )
        documents = list(query.stream())
        
        logger.info(f"Found {len(documents)} rank history entries for user {user_id}")
        
        history = []
        for doc in documents:
            try:
                data = doc.to_dict() or {}
                logger.debug(f"Processing rank history document {doc.id}: {data}")
                
                date_value = data.get("date", "")
                rank_value = data.get("rank", 0)
                
                # Ensure date is a string
                if not isinstance(date_value, str):
                    date_value = str(date_value)
                
                # Ensure rank is an integer
                rank_int = int(rank_value)
                
                history.append(schemas.RankHistoryEntry(
                    date=date_value,
                    rank=rank_int,
                ))
            except Exception as doc_exc:
                logger.error(f"Error processing rank history document {doc.id}: {doc_exc}")
                logger.error(traceback.format_exc())
                continue
        
        return history
        
    except Exception as exc:
        logger.error(f"Failed to fetch rank history: {exc}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch rank history: {str(exc)}",
        ) from exc


@router.get(
    "/leaderboard/around_me",
    response_model=schemas.RelativeLeaderboardResponse,
)
def read_relative_leaderboard(
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    Return leaderboard entries surrounding the current user:
    five ranks above and four ranks below, where possible.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to determine current user",
        )

    try:
        query = (
            db.collection("leaderboard")
            .order_by("average_score", direction=firestore.Query.DESCENDING)
        )
        documents = list(query.stream())
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leaderboard standings: {exc}",
        ) from exc

    entries = _build_leaderboard_entries(documents, db)
    try:
        current_index = next(
            index for index, entry in enumerate(entries) if entry.user_id == user_id
        )
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found on leaderboard",
        )

    start_index = max(current_index - 5, 0)
    end_index = min(current_index + 5, len(entries))
    window = entries[start_index:end_index]

    return schemas.RelativeLeaderboardResponse(
        rank=current_index + 1,
        entries=window,
    )


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
