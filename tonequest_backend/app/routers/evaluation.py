import json
import os
import random
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import firestore
from google.cloud.firestore import Client
from sentence_transformers import SentenceTransformer, util

from app import schemas
from app.dependencies import get_db, get_redis
from app.routers.auth import get_current_user

router = APIRouter(tags=["Evaluation"])

_model_lock = threading.Lock()
_model: Optional[SentenceTransformer] = None

_QUESTIONS_COLLECTION = os.getenv("QUESTIONS_COLLECTION", "QnA")
_SUBMISSIONS_COLLECTION = os.getenv("SUBMISSIONS_COLLECTION", "submissions")
_LEADERBOARD_COLLECTION = os.getenv("LEADERBOARD_COLLECTION", "leaderboard")


def _get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:
                _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _load_question(
    question_id: str,
    db: Client,
    redis_client,
) -> Dict:
    cache_key = f"question:{question_id}"
    cached = redis_client.get(cache_key)

    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            # Cache corruption – fall through to Firestore refresh.
            pass

    collection = db.collection(_QUESTIONS_COLLECTION)
    doc = collection.document(str(question_id)).get()

    snapshot = doc if doc.exists else None

    numeric_question_id: Optional[int] = None
    if snapshot is None:
        try:
            numeric_question_id = int(question_id)
        except (TypeError, ValueError):
            numeric_question_id = None

        if numeric_question_id is not None:
            try:
                query = (
                    collection.where("id", "==", numeric_question_id)
                    .limit(1)
                    .stream()
                )
                snapshot = next(query, None)
            except StopIteration:
                snapshot = None
            except Exception as exc:  # pragma: no cover - network failures
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to lookup question: {exc}",
                ) from exc

    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question not found: {question_id}",
        )

    question = snapshot.to_dict() or {}
    question.setdefault("id", numeric_question_id if numeric_question_id is not None else question_id)

    redis_client.set(cache_key, json.dumps(question), ex=300)
    return question


def _compute_similarity(
    answer_text: str,
    reference_answers: List[str],
) -> Tuple[float, str]:
    if not reference_answers:
        return 0.0, ""

    model = _get_embedding_model()
    sentences = [answer_text, *reference_answers]
    embeddings = model.encode(
        sentences, convert_to_tensor=True, normalize_embeddings=True
    )
    sims = util.cos_sim(embeddings[0], embeddings[1:]).squeeze(0)

    best_idx = int(sims.argmax())
    best_score = float(sims[best_idx])
    best_match = reference_answers[best_idx]
    return best_score, best_match


def _persist_submission(
    db: Client,
    submission_data: Dict,
) -> str:
    try:
        doc_ref = db.collection(_SUBMISSIONS_COLLECTION).document()
        doc_ref.set(submission_data)
        return doc_ref.id
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save submission: {exc}",
        ) from exc


def _update_leaderboard(
    db: Client,
    user_id: str,
    best_score: float,
) -> Dict:
    leaderboard_ref = db.collection(_LEADERBOARD_COLLECTION).document(user_id)

    try:
        snapshot = leaderboard_ref.get()
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read leaderboard: {exc}",
        ) from exc

    total_score = best_score
    submission_count = 1
    best_overall = best_score

    if snapshot.exists:
        payload = snapshot.to_dict() or {}
        total_score += float(payload.get("total_score", 0.0))
        submission_count += int(payload.get("submission_count", 0))
        best_overall = max(best_score, float(payload.get("best_score", 0.0)))

    average_score = total_score / submission_count

    leaderboard_payload = {
        "user_id": user_id,
        "total_score": total_score,
        "submission_count": submission_count,
        "average_score": average_score,
        "best_score": best_overall,
        "updated_at": datetime.utcnow(),
    }

    try:
        leaderboard_ref.set(leaderboard_payload, merge=True)
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update leaderboard: {exc}",
        ) from exc

    return leaderboard_payload


def _fallback_question() -> schemas.Question:
    return schemas.Question(
        id="sample-question",
        question_text="Describe a professional accomplishment you are particularly proud of.",
        reference_answers=[
            "I led a cross-functional team that delivered a critical project ahead of schedule by coordinating stakeholders and removing blockers early.",
            "I launched a new onboarding program that reduced ramp-up time for new hires by 30%.",
        ],
    )


@router.get("/questions/next", response_model=schemas.Question)
def get_next_question(
    _: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    Return a random question for the authenticated user to answer.
    Falls back to a static sample question if the collection is empty.
    """
    collection = db.collection(_QUESTIONS_COLLECTION)

    try:
        documents = list(collection.stream())
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load questions: {exc}",
        ) from exc

    if not documents:
        return _fallback_question()

    document = random.choice(documents)
    payload = document.to_dict() or {}
    fallback_question = _fallback_question()

    question_text = payload.get("question_text") or fallback_question.question_text
    reference_answers = payload.get("answers") or fallback_question.reference_answers

    return schemas.Question(
        id=str(payload.get("id") or document.id),
        question_text=question_text,
        reference_answers=list(reference_answers),
    )


@router.get("/questions/current", response_model=Union[schemas.Question, schemas.QuestionStatus])
def get_current_question(
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    Return the next unanswered question for the user in sequential order.
    Returns completion status if all questions are answered.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to identify authenticated user",
        )

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user_data = user_doc.to_dict() or {}
    answered_ids = user_data.get("answeredQuestionIds", [])
    
    collection = db.collection(_QUESTIONS_COLLECTION)
    
    try:
        all_docs = list(collection.stream())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load questions: {exc}",
        ) from exc
    
    if not all_docs:
        return _fallback_question()
    
    questions_with_ids = []
    for doc in all_docs:
        data = doc.to_dict() or {}
        q_id = data.get("id")
        if q_id is not None:
            questions_with_ids.append((int(q_id), doc, data))
    
    questions_with_ids.sort(key=lambda x: x[0])
    
    for q_id, doc, data in questions_with_ids:
        if q_id not in answered_ids:
            fallback = _fallback_question()
            return schemas.Question(
                id=str(q_id),
                question_text=data.get("question_text") or fallback.question_text,
                reference_answers=list(data.get("answers") or fallback.reference_answers),
            )
    
    return schemas.QuestionStatus(
        status="completed",
        message="You've answered all the questions, congratulations!"
    )


@router.post("/evaluate_answer")
def evaluate_answer(
    data: schemas.AnswerInput,
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
    redis_client=Depends(get_redis),
):
    """
    Evaluate the submitted answer, persist the result, and update leaderboard
    aggregates for the current user.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to identify authenticated user",
        )

    question = _load_question(data.question_id, db, redis_client)
    reference_answers = question.get("answers") or []

    best_score, best_match_answer = _compute_similarity(
        data.answer_text, reference_answers
    )

    submission_payload = {
        "user_id": user_id,
        "question_id": data.question_id,
        "submitted_answer": data.answer_text,
        "similarity_score": best_score,
        "best_match_answer": best_match_answer,
        "submitted_at": datetime.utcnow(),
    }
    submission_id = _persist_submission(db, submission_payload)

    leaderboard_data = _update_leaderboard(db, user_id, best_score)

    # Update user's totalSubmissions count and track answered question
    user_ref = db.collection("users").document(user_id)
    try:
        question_id_int = int(data.question_id)
        user_ref.update({
            "totalSubmissions": firestore.Increment(1),
            "answeredQuestionIds": firestore.ArrayUnion([question_id_int])
        })
    except (ValueError, TypeError):
        user_ref.update({"totalSubmissions": firestore.Increment(1)})

    return {
        "submission_id": submission_id,
        "similarity_score": best_score,
        "best_match_answer": best_match_answer,
        "leaderboard": {
            "average_score": leaderboard_data["average_score"],
            "best_score": leaderboard_data["best_score"],
            "submission_count": leaderboard_data["submission_count"],
        },
    }

