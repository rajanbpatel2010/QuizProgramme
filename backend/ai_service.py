import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import models

# Load environment variables
load_dotenv()

# Support multiple API keys separated by commas
keys_str = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
API_KEYS = [k.strip() for k in keys_str.split(",") if k.strip()]

if not API_KEYS:
    print("WARNING: GEMINI_API_KEYS is not set. AI features will be unavailable.")
    clients = []
else:
    clients = [genai.Client(api_key=key) for key in API_KEYS]

def call_gemini_with_failover(prompt: str, model: str = 'gemini-2.5-flash', response_mime_type: str = "text/plain") -> str:
    """
    Calls the Gemini API and automatically fails over to the next API key if the 
    current one hits a rate limit (429) or service unavailable (503) error.
    """
    if not clients:
        raise ValueError("AI features are unavailable because no GEMINI_API_KEYS are configured.")

    last_error = None
    for i, client in enumerate(clients):
        try:
            config = None
            if response_mime_type != "text/plain":
                config = types.GenerateContentConfig(response_mime_type=response_mime_type)
            
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            # If it's a quota or server overload issue, try the next key
            if "429" in error_str or "503" in error_str or "quota" in error_str or "unavailable" in error_str:
                print(f"[!] API Key {i+1}/{len(clients)} failed. Switching to next key...")
                continue
            else:
                # If it's a malformed prompt (400) or other error, raise it immediately
                raise e
                
    raise Exception(f"All {len(clients)} API keys exhausted. Last error: {last_error}")

def generate_professional_summary(db: Session, attempt: models.TestAttempt) -> str:
    """
    Calls Gemini API to generate a professional assessment summary.
    """
    if not clients:
        return "AI Summary is unavailable because GEMINI_API_KEYS is not configured."
        
    user_role = attempt.user.role
    score = attempt.score
    total = attempt.total if hasattr(attempt, 'total') else len(attempt.responses)
    domain = "your technical assessment"
    
    prompt = f"""
    You are an expert IT career coach and technical assessor.
    The user, a {user_role}, just completed {domain} and scored {score} out of {total}.
    
    Write a brief, highly professional markdown-formatted summary of their performance.
    Include:
    - A congratulatory or encouraging opening.
    - An analysis of what this score means for their role level.
    - 2 specific Strengths they demonstrated.
    - 1-2 Areas for Improvement.
    - 1 highly relevant Suggested Resource (like a book, Microsoft Learn module, or documentation link) for their growth.
    """
    
    try:
        return call_gemini_with_failover(prompt)
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "An error occurred while generating the AI summary. Please try again later."

def scrape_and_generate_new_questions(db: Session, topics: list[str], role: str):
    """
    The 'Enhance Knowledge' worker function.
    Uses AI to dynamically generate new questions and insert them into the DB.
    """
    if not clients:
        print("Skipping dynamic enhancement: GEMINI_API_KEYS is not configured.")
        return

    try:
        topic_str = ", ".join(topics)
        
        prompt = f"""
        You are a technical assessment architect. Create 2 brand new, highly technical multiple-choice questions 
        for a {role} focusing on these topics: {topic_str}.
        
        For each question, provide exactly 4 options, designate which one is correct, and optionally provide a code snippet example.
        Return the result as a strict JSON array matching this structure:
        [
            {{
                "domain": "string",
                "question": "string",
                "practical_example": "string or null",
                "options": ["string", "string", "string", "string"],
                "correct_answer_index": 0
            }}
        ]
        """
        
        response_text = call_gemini_with_failover(prompt, response_mime_type="application/json")
        
        import json
        data = json.loads(response_text)
        
        for q_data in data:
            domain_name = q_data.get("domain", topics[0] if topics else "General")
            cat = db.query(models.Category).filter(models.Category.name == domain_name).first()
            if not cat:
                cat = models.Category(name=domain_name)
                db.add(cat)
                db.flush()
            
            q = models.Question(
                category_id=cat.id,
                role_level=role,
                question_text=q_data.get("question", ""),
                practical_example=q_data.get("practical_example")
            )
            db.add(q)
            db.flush()
            
            options = q_data.get("options", ["A", "B", "C", "D"])
            correct_idx = q_data.get("correct_answer_index", 0)
            for j, opt_text in enumerate(options):
                ans = models.Answer(
                    question_id=q.id,
                    answer_text=str(opt_text),
                    is_correct=(j == correct_idx)
                )
                db.add(ans)
        
        db.commit()
        print("Successfully ran knowledge enhancement worker!")
    except Exception as e:
        print(f"Error running enhancement worker: {e}")
