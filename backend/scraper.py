import os
import json
import time
import random
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import database, models
import ai_service

# Load environment variables
load_dotenv()

DOMAINS = [
    "OOPS", ".Net", "C#", "SQL Server", "SSRS", 
    "AngularJS", "TypeScript", "ReactJS", "Azure", "Agentic AI"
]

ROLES = [
    models.RoleEnum.FRESHER, models.RoleEnum.EXPERIENCED, models.RoleEnum.ADVANCED,
    models.RoleEnum.TECH_LEAD, models.RoleEnum.TECH_ARCHITECT, 
    models.RoleEnum.PROJECT_MANAGER, models.RoleEnum.PROGRAM_MANAGER
]

def generate_questions_batch(domain: str, role: str, count: int = 15):
    """
    Calls Gemini AI to generate a batch of highly technical questions.
    """
    
    if "Manager" in role or "Architect" in role or "Lead" in role:
        role_guidance = f"Since this is for a '{role}', focus heavily on system architecture, deployment strategies, risk management, agile delivery, team leadership, scalability, and high-level problem solving within the context of {domain}. Avoid extremely low-level syntax questions."
    else:
        role_guidance = f"Since this is for a '{role}', focus deeply on low-level technical execution, syntax quirks, deep framework knowledge, coding best practices, and hands-on debugging scenarios within {domain}."
        
    prompt = f"""
    You are an expert IT Technical Architect and Interviewer.
    Generate {count} distinct, highly authentic, and challenging multiple-choice interview questions on the topic of "{domain}" strictly tailored for a candidate at the "{role}" level.
    
    {role_guidance}
    
    For each question, provide:
    1. The technical question text.
    2. A practical example (like a code snippet, architectural diagram description, or scenario) relevant to the question.
    3. Exactly 4 possible options.
    4. The index (0-3) of the correct option.
    
    Return the result strictly as a JSON array of objects with the following schema:
    [
        {{
            "question": "string",
            "practical_example": "string",
            "options": ["string", "string", "string", "string"],
            "correct_answer_index": integer
        }}
    ]
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response_text = ai_service.call_gemini_with_failover(
                prompt=prompt,
                response_mime_type="application/json"
            )
            data = json.loads(response_text)
            if isinstance(data, list) and len(data) > 0:
                return data
        except KeyboardInterrupt:
            import sys
            print("\n[!] Manual cancellation detected (CTRL+C). Forcing immediate exit.")
            sys.exit(0)
        except Exception as e:
            print(f"Error generating batch for {domain} ({role}) on attempt {attempt+1}: {e}")
            try:
                time.sleep(10) # Exponential backoff or sleep for rate limits
            except KeyboardInterrupt:
                import sys
                print("\n[!] Manual cancellation detected (CTRL+C) during retry wait. Forcing immediate exit.")
                sys.exit(0)
            
    return []

def seed_database(db: Session):
    print("Starting AI-Driven Database Seeding...")
    
    # 1. Seed Categories
    category_objs = {}
    for domain in DOMAINS:
        cat = db.query(models.Category).filter(models.Category.name == domain).first()
        if not cat:
            cat = models.Category(name=domain)
            db.add(cat)
            db.commit()
            db.refresh(cat)
        category_objs[domain] = cat

    # 2. Generate Real Questions using Gemini
    total_questions = 0
    target_per_domain = 300
    batch_size = 15 # Generate 15 at a time to keep JSON payload sizes manageable
    
    # 3. Determine the latest fetched date per domain to process the oldest first
    import datetime
    domain_updates = []
    for domain in DOMAINS:
        cat = category_objs[domain]
        latest_q = db.query(models.Question).filter(models.Question.category_id == cat.id).order_by(models.Question.created_at.desc()).first()
        
        # If no questions exist, set to absolute minimum datetime so it gets processed first
        last_updated = latest_q.created_at if latest_q and latest_q.created_at else datetime.datetime.min
        domain_updates.append((domain, last_updated))
        
    # Sort domains by last_updated ASC (older ones will be at the front of the list)
    domain_updates.sort(key=lambda x: x[1])
    sorted_domains = [x[0] for x in domain_updates]
    
    print("\n--- Processing Order (Oldest Data First) ---")
    for d, date in domain_updates:
        print(f"{d}: {'Never Fetched' if date == datetime.datetime.min else date}")
        
    for domain in sorted_domains:
        cat = category_objs[domain]
        
        # Check how many questions already exist for this domain to allow resuming
        existing_count = db.query(models.Question).filter(models.Question.category_id == cat.id).count()
        if existing_count >= target_per_domain:
            print(f"[{domain}] Already has {existing_count} questions. Skipping.")
            total_questions += existing_count
            continue
            
        needed = target_per_domain - existing_count
        print(f"\n--- Generating {needed} real questions for {domain} ---")
        
        domain_added = 0
        role_cycle = iter(ROLES * (needed // len(ROLES) + 1))  # Round-robin across all roles
        while domain_added < needed:
            role = next(role_cycle).value
            print(f"[{domain}] Fetching batch of {batch_size} questions for role: {role}...")
            
            questions_data = generate_questions_batch(domain, role, count=batch_size)
            
            if not questions_data:
                print("CRITICAL: AI request failed or was cancelled continuously. Stopping all further requests to prevent infinite loops and save API quotas.")
                return # Stop the entire seeding process
                
            for q_data in questions_data:
                # Add Question
                q = models.Question(
                    category_id=cat.id,
                    role_level=role,
                    question_text=q_data.get("question", "Fallback Question"),
                    practical_example=q_data.get("practical_example", None)
                )
                db.add(q)
                db.flush() # get ID
                
                # Add Answers
                options = q_data.get("options", ["A", "B", "C", "D"])
                correct_idx = q_data.get("correct_answer_index", 0)
                
                for j, opt_text in enumerate(options):
                    ans = models.Answer(
                        question_id=q.id,
                        answer_text=str(opt_text),
                        is_correct=(j == correct_idx)
                    )
                    db.add(ans)
                    
                domain_added += 1
                total_questions += 1
                
                if domain_added >= needed:
                    break
            
            # Commit the batch
            db.commit()
            print(f"[{domain}] Progress: {domain_added}/{needed} questions seeded.")
            
            # Rate limit sleep (15 RPM free tier limit = 1 request every 4 seconds)
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                import sys
                print("\n[!] Manual cancellation detected (CTRL+C). Forcing immediate exit.")
                sys.exit(0)
            
    print(f"\n✅ Successfully seeded database! Total questions available: {total_questions}")

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
