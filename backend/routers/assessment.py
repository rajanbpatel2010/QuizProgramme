from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy import and_
import models, schemas, database, security
from datetime import datetime
import random

router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"]
)

QUESTIONS_PER_TEST = 10

@router.post("/start", response_model=schemas.TestAttemptResponse)
def start_assessment(db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    # Create a new test attempt
    attempt = models.TestAttempt(user_id=current_user.id)
    db.add(attempt)
    db.flush()

    # Select 10 random questions for the user's role and bind them to this attempt
    questions = db.query(models.Question).filter(
        models.Question.role_level == current_user.role
    ).order_by(func.random()).limit(QUESTIONS_PER_TEST).all()

    # Fallback to any questions if role has none
    if not questions or len(questions) < QUESTIONS_PER_TEST:
        fallback = db.query(models.Question).order_by(func.random()).limit(QUESTIONS_PER_TEST).all()
        if len(fallback) > len(questions):
            questions = fallback

    if not questions:
        db.rollback()
        raise HTTPException(status_code=404, detail="No questions available in the database. Please seed the database first.")

    # Bind questions to this attempt with a fixed position order
    for idx, q in enumerate(questions):
        aq = models.AttemptQuestion(
            attempt_id=attempt.id,
            question_id=q.id,
            position=idx
        )
        db.add(aq)

    db.commit()
    db.refresh(attempt)
    return attempt

@router.get("/{attempt_id}/questions", response_model=schemas.AssessmentStateResponse)
def get_assessment_questions(attempt_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == attempt_id, models.TestAttempt.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.completed_at:
        raise HTTPException(status_code=400, detail="Test already completed")

    # Fetch the pre-bound questions in their fixed position order
    assigned = attempt.assigned_questions  # Already ordered by position via relationship

    if not assigned:
        raise HTTPException(status_code=404, detail="No questions assigned to this attempt.")

    response_questions = []
    for aq in assigned:
        q = aq.question
        shuffled_answers = list(q.answers)
        random.shuffle(shuffled_answers)
        rq = schemas.QuestionResponse.model_validate(q)
        rq.answers = [schemas.AnswerResponse.model_validate(ans) for ans in shuffled_answers]
        response_questions.append(rq)

    # Build map of already answered questions
    answered_map = {resp.question_id: resp.selected_answer_id for resp in attempt.responses if resp.selected_answer_id is not None}

    return schemas.AssessmentStateResponse(
        questions=response_questions,
        answered_map=answered_map
    )

@router.post("/{attempt_id}/finish")
def finish_assessment(attempt_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == attempt_id, models.TestAttempt.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.completed_at:
        raise HTTPException(status_code=400, detail="Test already completed")

    attempt.completed_at = datetime.utcnow()

    # H3 Fix: Single joined query for score calculation instead of N+1
    correct_responses = db.query(models.TestResponse).join(
        models.Answer,
        and_(
            models.Answer.id == models.TestResponse.selected_answer_id,
            models.Answer.is_correct == True
        )
    ).filter(models.TestResponse.attempt_id == attempt_id).count()

    attempt.score = correct_responses
    
    # Generate Professional AI Summary
    import ai_service
    attempt.ai_summary = ai_service.generate_professional_summary(db, attempt)
    
    db.commit()
    return {"message": "Assessment finished", "score": correct_responses, "total": len(attempt.assigned_questions)}

@router.post("/{attempt_id}/submit")
def submit_answer(attempt_id: int, answer_data: schemas.SubmitAnswer, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == attempt_id, models.TestAttempt.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.completed_at:
        raise HTTPException(status_code=400, detail="Test already completed")

    # Validate that the question is actually assigned to this attempt
    assigned_q_ids = [aq.question_id for aq in attempt.assigned_questions]
    if answer_data.question_id not in assigned_q_ids:
        raise HTTPException(status_code=400, detail="This question is not part of your current assessment.")

    existing_resp = db.query(models.TestResponse).filter(
        models.TestResponse.attempt_id == attempt_id,
        models.TestResponse.question_id == answer_data.question_id
    ).first()
    
    if existing_resp:
        existing_resp.selected_answer_id = answer_data.selected_answer_id
    else:
        test_resp = models.TestResponse(
            attempt_id=attempt_id,
            question_id=answer_data.question_id,
            selected_answer_id=answer_data.selected_answer_id
        )
        db.add(test_resp)
        
    db.commit()
    
    return {"message": "Answer recorded successfully"}

@router.get("/{attempt_id}/result", response_model=schemas.TestAttemptResponse)
def get_result(attempt_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == attempt_id, models.TestAttempt.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if not attempt.completed_at:
        raise HTTPException(status_code=400, detail="Test not completed yet")
    return attempt

@router.post("/{attempt_id}/enhance-knowledge")
def enhance_knowledge(attempt_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    """
    Dynamically generates new questions based on the topics the user was tested on.
    """
    attempt = db.query(models.TestAttempt).filter(models.TestAttempt.id == attempt_id, models.TestAttempt.user_id == current_user.id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Dynamically infer topics from the user's assigned questions
    assigned_q_ids = [aq.question_id for aq in attempt.assigned_questions]
    questions = db.query(models.Question).filter(models.Question.id.in_(assigned_q_ids)).all()
    category_ids = list(set(q.category_id for q in questions))
    categories = db.query(models.Category).filter(models.Category.id.in_(category_ids)).all()
    topics = [c.name for c in categories]
    
    if not topics:
        topics = ["General IT"]
    
    import ai_service
    ai_service.scrape_and_generate_new_questions(db, topics, current_user.role)
    
    return {"message": "Knowledge enhancement process initiated successfully!"}
