from pydantic import BaseModel
from typing import List, Optional
from pydantic import ConfigDict

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    displayName: Optional[str] = None

class UserSignup(BaseModel):
    email: str
    password: str
    displayName: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    user: 'User'
    token: str
    message: str

class User(UserBase):
    uid: str
    totalSubmissions: int = 0
    
    model_config = ConfigDict(from_attributes=True)

# --- Question Schemas ---
class QuestionBase(BaseModel):
    prompt_text: str
    category: str
    difficulty: str

class Question(QuestionBase):
    id: str
    reference_answers: List[str]
    
    model_config = ConfigDict(from_attributes=True)

# --- Submission Schemas ---
class AnswerInput(BaseModel):
    """ Replaces UserAnswer from evaluation.py """
    question_id: str
    answer_text: str

class SubmissionBase(BaseModel):
    user_id: str
    question_id: str
    submitted_answer: str
    similarity_score: float
    best_match_answer: str

class Submission(SubmissionBase):
    id: str
    submitted_at: str
    
    model_config = ConfigDict(from_attributes=True)

# --- Leaderboard Schemas ---
class ScoreUpdate(BaseModel):
    """ From leaderboard.py """
    user_id: str
    delta: float

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    score: float