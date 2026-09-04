"""
Database Persistence Engine (Gaurang & Harsh Co-Ownership)
SQLite database manager for persisting LearnerProfile history and session progress across sessions.
"""

import sqlite3
import json
import os
from typing import Optional, Dict, Any
from backend.app.db.models import LearnerProfile
from backend.app.config import settings

DB_PATH = os.path.join(settings.STORAGE_DIR, "ai_teacher.db")

def init_db():
    """Initializes SQLite database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learner_profiles (
            student_id TEXT PRIMARY KEY,
            data JSON NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_learner_profile(profile: LearnerProfile) -> None:
    """Saves or updates a LearnerProfile in SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    profile_json = profile.model_dump_json()
    
    cursor.execute("""
        INSERT INTO learner_profiles (student_id, data)
        VALUES (?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            data = excluded.data,
            updated_at = CURRENT_TIMESTAMP
    """, (profile.student_id, profile_json))
    
    conn.commit()
    conn.close()

def get_learner_profile(student_id: str = "u123") -> LearnerProfile:
    """Retrieves a LearnerProfile by student_id or returns a default profile if missing."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT data FROM learner_profiles WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data_dict = json.loads(row[0])
        return LearnerProfile(**data_dict)
    else:
        default_profile = LearnerProfile(student_id=student_id)
        save_learner_profile(default_profile)
        return default_profile

def update_student_concepts(student_id: str, new_strong: list = None, new_weak: list = None):
    """Updates strong and weak concepts for a student."""
    profile = get_learner_profile(student_id)
    if new_strong:
        profile.strong_concepts = list(set(profile.strong_concepts + new_strong))
    if new_weak:
        profile.weak_concepts = list(set(profile.weak_concepts + new_weak))
    save_learner_profile(profile)
    return profile
