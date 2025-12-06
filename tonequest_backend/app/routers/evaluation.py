import json
import logging
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Union

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import firestore
from google.cloud.firestore import Client

from app import schemas
from app.dependencies import get_db, get_redis
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Evaluation"])

_QUESTIONS_COLLECTION = os.getenv("QUESTIONS_COLLECTION", "QnA")
_SUBMISSIONS_COLLECTION = os.getenv("SUBMISSIONS_COLLECTION", "submissions")
_LEADERBOARD_COLLECTION = os.getenv("LEADERBOARD_COLLECTION", "leaderboard")
_DEFAULT_GEMINI_RESULT = {
    "score": 0,
    "toneFeedback": "Evaluation failed",
    "grammarIssues": [],
    "suggestions": "Unable to evaluate response at this time.",
}


def evaluate_with_gemini(
    prompt_text: str,
    user_answer: str,
    use_mock: bool = False,
    mock_result: Optional[dict] = None,
) -> dict:
    """
    Call Gemini with the provided prompt and answer, returning the parsed JSON payload.
    """
    if use_mock:
        if mock_result is not None:
            return mock_result
        return {
            "score": 75,
            "toneFeedback": "Balanced tone with room for more confidence.",
            "grammarIssues": ["Consider varying sentence length."],
            "suggestions": "Add concrete examples to strengthen the response.",
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY environment variable is not configured.",
        )

    instructions = (
        "You are an AI writing evaluator. Analyze the provided prompt and user answer. "
        "You MUST return ONLY a valid JSON object with no markdown formatting, no code blocks, and no extra text. "
        "The JSON object must have exactly these fields:\n"
        '- "score": a number between 0 and 100\n'
        '- "toneFeedback": a string\n'
        '- "grammarIssues": an array of strings\n'
        '- "suggestions": a string\n\n'
        "Tasks:\n"
        "1. Score the writing from 0-100.\n"
        "2. Provide tone feedback.\n"
        "3. List grammar issues.\n"
        "4. Offer improvement suggestions.\n\n"
        "Return ONLY the JSON object, nothing else. Example format:\n"
        '{"score": 75, "toneFeedback": "Professional and clear", "grammarIssues": [], "suggestions": "Good work"}'
    )

    request_payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"{instructions}\n\nPrompt:\n{prompt_text}\n\n"
                            f"User Answer:\n{user_answer}"
                        )
                    }
                ]
            }
        ]
    }

    try:
        # Use v1beta endpoint with API key as query parameter (most reliable format)
        # Alternative: Use header "x-goog-api-key" if query param doesn't work
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
            },
            json=request_payload,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        # Extract detailed error information for debugging
        error_detail = str(exc)
        if hasattr(exc, 'response') and exc.response is not None:
            try:
                error_body = exc.response.json()
                # Include the actual error message from Gemini API
                error_message = error_body.get('error', {}).get('message', 'Unknown error')
                error_detail = f"{exc} - Gemini API Error: {error_message} - Full response: {error_body}"
            except (ValueError, AttributeError):
                error_text = exc.response.text[:500] if hasattr(exc.response, 'text') else "No response text"
                error_detail = f"{exc} - Status: {exc.response.status_code}, Response: {error_text}"
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to reach Gemini API: {error_detail}",
        ) from exc

    try:
        response_payload = response.json()
        logger.debug(f"Gemini API response payload: {json.dumps(response_payload, indent=2)}")
    except ValueError as e:
        logger.error(f"Failed to parse Gemini response as JSON. Status: {response.status_code}, Text: {response.text[:500]}")
        return dict(_DEFAULT_GEMINI_RESULT)

    candidates = response_payload.get("candidates") if isinstance(response_payload, dict) else None
    if not candidates:
        logger.error(f"Gemini response missing 'candidates' field. Response: {json.dumps(response_payload, indent=2)}")
        return dict(_DEFAULT_GEMINI_RESULT)

    parts = candidates[0].get("content", {}).get("parts", [])
    text_segments = [part.get("text", "") for part in parts if part.get("text")]
    if not text_segments:
        logger.error(f"Gemini response missing text content. Candidates: {json.dumps(candidates, indent=2)}")
        return dict(_DEFAULT_GEMINI_RESULT)

    raw_text = " ".join(text_segments).strip()
    logger.debug(f"Gemini returned text (first 500 chars): {raw_text[:500]}")
    
    # Try to extract JSON from markdown code blocks (common LLM behavior)
    json_text = raw_text
    if "```json" in raw_text:
        # Extract JSON from ```json ... ``` block
        start = raw_text.find("```json") + 7
        end = raw_text.find("```", start)
        if end != -1:
            json_text = raw_text[start:end].strip()
            logger.debug("Extracted JSON from markdown code block")
    elif "```" in raw_text:
        # Extract JSON from ``` ... ``` block
        start = raw_text.find("```") + 3
        end = raw_text.find("```", start)
        if end != -1:
            json_text = raw_text[start:end].strip()
            logger.debug("Extracted JSON from code block")
    
    # Try to find JSON object boundaries if text has extra content
    if not json_text.strip().startswith("{"):
        # Look for first { and last }
        start_brace = json_text.find("{")
        end_brace = json_text.rfind("}")
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            json_text = json_text[start_brace:end_brace + 1]
            logger.debug("Extracted JSON object from text")
    
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini text as JSON. Error: {e}")
        logger.error(f"Attempted to parse: {json_text[:1000]}")
        logger.error(f"Original text: {raw_text[:1000]}")
        return dict(_DEFAULT_GEMINI_RESULT)

    if not isinstance(parsed, dict):
        logger.error(f"Parsed JSON is not a dict. Type: {type(parsed)}, Value: {parsed}")
        return dict(_DEFAULT_GEMINI_RESULT)

    score = parsed.get("score")
    try:
        score = float(score) if score is not None else None
    except (TypeError, ValueError):
        score = None

    grammar_issues = parsed.get("grammarIssues")
    if isinstance(grammar_issues, str):
        grammar_issues = [grammar_issues]
    elif not isinstance(grammar_issues, list):
        grammar_issues = []

    result = {
        "score": score,
        "toneFeedback": parsed.get("toneFeedback", ""),
        "grammarIssues": grammar_issues,
        "suggestions": parsed.get("suggestions", ""),
    }
    return result


def evaluate_answer_with_model(model_name: str, question: str, answer: str) -> dict:
    """
    Dispatch evaluation to the model-specific implementation.
    """
    if model_name.lower() == "gemini":
        return evaluate_with_gemini(question, answer)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported evaluation model: {model_name}",
    )


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
        is_last_question=True,
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

    return schemas.Question(
        id=str(payload.get("id") or document.id),
        question_text=question_text,
        is_last_question=False,  # Random question, can't determine if last
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
    
    # Find all unanswered questions
    unanswered = [q for q in questions_with_ids if q[0] not in answered_ids]
    
    if not unanswered:
        return schemas.QuestionStatus(
            status="completed",
            message="You've answered all the questions, congratulations!"
        )
    
    # Get the first unanswered question
    q_id, doc, data = unanswered[0]
    fallback = _fallback_question()
    # Check if this is the last unanswered question
    is_last = len(unanswered) == 1
    
    return schemas.Question(
        id=str(q_id),
        question_text=data.get("question_text") or fallback.question_text,
        is_last_question=is_last,
    )


@router.get("/user/score-history", response_model=List[schemas.ScoreHistoryEntry])
def get_user_score_history(
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db),
):
    """
    Return all submissions for the current user ordered chronologically.
    """
    import traceback
    
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to identify authenticated user",
        )

    try:
        query = (
            db.collection(_SUBMISSIONS_COLLECTION)
            .where("user_id", "==", user_id)
            .order_by("submitted_at")
        )
        documents = list(query.stream())
        
        logger.info(f"Found {len(documents)} submissions for user {user_id}")
        
        history = []
        for doc in documents:
            try:
                data = doc.to_dict() or {}
                logger.debug(f"Processing document {doc.id}: {data}")
                
                question_id = int(data.get("question_id", 0))
                score = float(data.get("score", 0.0))
                submitted_at = data.get("submitted_at")
                
                # Handle Firestore Timestamp serialization
                if submitted_at:
                    if hasattr(submitted_at, 'isoformat'):
                        submitted_at_str = submitted_at.isoformat()
                    elif hasattr(submitted_at, 'seconds'):
                        # Firestore Timestamp object
                        from datetime import datetime as dt, timezone
                        submitted_at_str = dt.fromtimestamp(submitted_at.seconds, tz=timezone.utc).isoformat()
                    else:
                        submitted_at_str = str(submitted_at)
                    
                    history.append(schemas.ScoreHistoryEntry(
                        question_id=question_id,
                        score=score,
                        submitted_at=submitted_at_str,
                    ))
            except Exception as doc_exc:
                logger.error(f"Error processing document {doc.id}: {doc_exc}")
                logger.error(traceback.format_exc())
                continue
        
        return history
        
    except Exception as exc:
        logger.error(f"Failed to fetch score history: {exc}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch score history: {str(exc)}",
        ) from exc


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
    prompt_text = question.get("question_text") or ""

    gemini_result = evaluate_answer_with_model("gemini", prompt_text, data.answer_text)
    gemini_score = gemini_result.get("score")
    try:
        numeric_score = float(gemini_score) if gemini_score is not None else 0.0
    except (TypeError, ValueError):
        numeric_score = 0.0

    submission_payload = {
        "user_id": user_id,
        "question_id": data.question_id,
        "submitted_answer": data.answer_text,
        "score": numeric_score,
        "tone_feedback": gemini_result.get("toneFeedback"),
        "grammar_issues": gemini_result.get("grammarIssues"),
        "suggestions": gemini_result.get("suggestions"),
        "llm_feedback": {
            "score": gemini_result.get("score"),
            "toneFeedback": gemini_result.get("toneFeedback"),
            "grammarIssues": gemini_result.get("grammarIssues"),
            "suggestions": gemini_result.get("suggestions"),
        },
        "submitted_at": datetime.utcnow(),
    }
    submission_id = _persist_submission(db, submission_payload)

    leaderboard_data = _update_leaderboard(db, user_id, numeric_score)

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
        "question_id": data.question_id,
        "user_who_submitted": user_id,
        "score": numeric_score,
        "tone_feedback": gemini_result.get("toneFeedback"),
        "grammar_issues": gemini_result.get("grammarIssues"),
        "suggestions": gemini_result.get("suggestions"),
        "submission_id": submission_id,
        "leaderboard": {
            "average_score": leaderboard_data["average_score"],
            "best_score": leaderboard_data["best_score"],
            "submission_count": leaderboard_data["submission_count"],
        },
    }

