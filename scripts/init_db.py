"""
Database schema initialization for concurso.db SQLite database.
Run this script to create/reset the database structure.
"""
import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "..", "concurso.db")


def init_db(db_path=DB_PATH):
    """Creates all tables in the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    
    c = conn.cursor()
    
    # Exams table
    c.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            banca TEXT NOT NULL,
            year INTEGER,
            total_questions INTEGER,
            config_json TEXT
        )
    """)
    
    # Questions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            exam_id TEXT NOT NULL,
            number INTEGER NOT NULL,
            discipline TEXT NOT NULL DEFAULT 'Conhecimentos Específicos',
            type TEXT NOT NULL DEFAULT 'right_wrong',
            statement TEXT NOT NULL,
            support_text TEXT,
            correct_answer TEXT,
            explanation TEXT,
            images_json TEXT,
            page_number INTEGER,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )
    """)
    
    # Options table (A-E or C/E)
    c.execute("""
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT NOT NULL,
            option_key TEXT NOT NULL,
            option_text TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
            UNIQUE(question_id, option_key)
        )
    """)
    
    # Topics table
    c.execute("""
        CREATE TABLE IF NOT EXISTS question_topics (
            question_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            PRIMARY KEY (question_id, topic),
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    """)
    
    # User progress table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            question_id TEXT PRIMARY KEY,
            solved INTEGER DEFAULT 0,
            selected_option TEXT,
            is_correct INTEGER,
            is_starred INTEGER DEFAULT 0,
            ai_explanation TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    """)
    
    # Indexes for performance
    c.execute("CREATE INDEX IF NOT EXISTS idx_questions_exam ON questions(exam_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_questions_number ON questions(exam_id, number)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_options_question ON options(question_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_topics_question ON question_topics(question_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_progress_solved ON user_progress(solved)")
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")
    return db_path


if __name__ == "__main__":
    init_db()
