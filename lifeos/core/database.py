"""SQLite database engine, schemas and seed data for LifeOS.
Designed for 100% offline-first reliability on Linux and Android.
"""

import json
import sqlite3
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional
from lifeos.core.config import DB_PATH

def get_connection(db_file: Optional[str] = None) -> sqlite3.Connection:
    """Return a configured sqlite3 connection with dict-like row factory."""
    path = db_file or str(DB_PATH)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_file: Optional[str] = None) -> None:
    """Initialize database tables and populate seed data if empty."""
    conn = get_connection(db_file)
    cur = conn.cursor()

    # 1. Projects table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        category TEXT DEFAULT 'General',
        color TEXT DEFAULT '#C6A76B',
        progress INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        deadline TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. Tasks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
        priority TEXT DEFAULT 'MEDIUM',
        due_date TEXT,
        estimated_minutes INTEGER DEFAULT 30,
        actual_minutes INTEGER DEFAULT 0,
        is_completed INTEGER DEFAULT 0,
        completed_at TEXT,
        tags TEXT DEFAULT '[]',
        subtasks_json TEXT DEFAULT '[]',
        created_at TEXT NOT NULL
    );
    """)

    # 3. Calendar Events
    cur.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        event_type TEXT DEFAULT 'task',
        location TEXT DEFAULT '',
        color TEXT DEFAULT '#C6A76B',
        is_all_day INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    # 4. Study Courses & Hub
    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        professor TEXT DEFAULT '',
        semester TEXT DEFAULT 'S1',
        color TEXT DEFAULT '#DFBA7B',
        target_grade REAL DEFAULT 16.0,
        current_grade REAL DEFAULT 14.5,
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES study_courses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        room TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES study_courses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 45,
        notes TEXT DEFAULT '',
        completed INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # 5. Habits
    cur.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        frequency TEXT DEFAULT 'daily',
        target_per_week INTEGER DEFAULT 7,
        color TEXT DEFAULT '#C6A76B',
        icon TEXT DEFAULT 'star',
        streak_current INTEGER DEFAULT 0,
        streak_best INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
        date TEXT NOT NULL,
        status INTEGER DEFAULT 1,
        notes TEXT DEFAULT '',
        UNIQUE(habit_id, date)
    );
    """)

    # 6. Streaks & Daily Checklist Protocol
    cur.execute("""
    CREATE TABLE IF NOT EXISTS streaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT DEFAULT 'fire',
        current_streak INTEGER DEFAULT 0,
        best_streak INTEGER DEFAULT 0,
        last_completed_date TEXT,
        category TEXT DEFAULT 'protocol'
    );
    """)

    # 7. Goals & Milestones
    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        category TEXT DEFAULT 'Dev',
        target_date TEXT,
        progress INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        milestones_json TEXT DEFAULT '[]',
        created_at TEXT NOT NULL
    );
    """)

    # 8. Focus & Pomodoro Sessions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS focus_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
        course_id INTEGER REFERENCES study_courses(id) ON DELETE SET NULL,
        duration_minutes INTEGER NOT NULL,
        mode TEXT DEFAULT 'pomodoro',
        completed_at TEXT NOT NULL
    );
    """)

    # 9. Settings
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    conn.commit()

    # Populate seed data if database is fresh
    _seed_if_needed(conn)
    conn.close()

def _seed_if_needed(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks;")
    if cur.fetchone()[0] > 0:
        return

    today = date.today().isoformat()
    now_str = datetime.now().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    in_3_days = (date.today() + timedelta(days=3)).isoformat()
    in_7_days = (date.today() + timedelta(days=7)).isoformat()

    # Seed Settings
    settings_data = [
        ("user_name", "Thomas V."),
        ("theme", "dark_sanctuary"),
        ("accent_color", "#C6A76B"),
        ("pomodoro_work_duration", "25"),
        ("pomodoro_short_break", "5"),
        ("pomodoro_long_break", "15"),
        ("density_mode", "comfortable"),
        ("notifications_enabled", "true"),
    ]
    cur.executemany("INSERT INTO settings (key, value) VALUES (?, ?);", settings_data)

    # Seed Projects
    projects_data = [
        ("Refonte Backend FastAPI", "Architecture modulaire REST API et SQLite offline", "Dev", "#C6A76B", 65, "active", in_7_days, now_str),
        ("Examens Semestre 1", "Préparation et révisions intensives L3 Informatique", "Académique", "#DFBA7B", 40, "active", in_7_days, now_str),
        ("Programme Musculation & Mobilité", "Hypertrophie et étirements quotidiens", "Santé", "#7DD9A3", 80, "active", in_7_days, now_str),
        ("Application Mobile LifeOS", "Client Kivy & KivyMD design Atelier OS", "Dev", "#E5A93B", 50, "active", in_7_days, now_str),
    ]
    cur.executemany("""
        INSERT INTO projects (title, description, category, color, progress, status, deadline, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, projects_data)

    # Seed Tasks
    tasks_data = [
        (
            "Rédiger le rapport d'architecture SQLite",
            "Documenter le schéma relationnel, les index de recherche et les stratégies offline-first.",
            1, "URGENT", today, 45, 30, 0, None,
            json.dumps(["SQLite", "Doc"]),
            json.dumps([
                {"text": "Schéma entités-relations", "done": True},
                {"text": "Stratégie de synchronisation", "done": True},
                {"text": "Revue de performance", "done": False}
            ]),
            now_str
        ),
        (
            "Deep Work Algorithmique",
            "Résolution des problèmes de graphes orientés acycliques (DAG) et tri topologique.",
            2, "HIGH", today, 90, 45, 0, None,
            json.dumps(["Algo", "Study"]),
            json.dumps([
                {"text": "Implémentation DFS/BFS", "done": True},
                {"text": "Calcul chemin critique", "done": False}
            ]),
            now_str
        ),
        (
            "Implémenter l'API REST Tasks & Projects",
            "Créer les routers FastAPI avec validation Pydantic et tests de régression.",
            1, "HIGH", tomorrow, 60, 0, 0, None,
            json.dumps(["FastAPI", "API"]),
            json.dumps([
                {"text": "CRUD Tasks", "done": True},
                {"text": "CRUD Projects", "done": False}
            ]),
            now_str
        ),
        (
            "Séance Sport & Mobilité",
            "45 minutes de renforcement du dos, pectoraux et mobilité des hanches.",
            3, "MEDIUM", today, 45, 45, 1, now_str,
            json.dumps(["Sport"]),
            json.dumps([]),
            now_str
        ),
        (
            "Révision Systèmes Distribués (Amphi B)",
            "Relire les slides sur l'algorithme de Paxos et Raft.",
            2, "MEDIUM", tomorrow, 60, 0, 0, None,
            json.dumps(["Cours"]),
            json.dumps([]),
            now_str
        ),
        (
            "Lecture Technique (20 pages)",
            "Designing Data-Intensive Applications de Martin Kleppmann.",
            4, "LOW", today, 30, 0, 0, None,
            json.dumps(["Lecture"]),
            json.dumps([]),
            now_str
        )
    ]
    cur.executemany("""
        INSERT INTO tasks (title, description, project_id, priority, due_date, estimated_minutes, actual_minutes, is_completed, completed_at, tags, subtasks_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tasks_data)

    # Seed Calendar Events
    cal_data = [
        ("Séance Sport & Mobilité", "Haut du corps & gainage", today, "07:30", "08:15", "sport", "Salle de musculation", "#7DD9A3", 0, now_str),
        ("Cours Magistral Systèmes Distribués", "Paxos & consensus distribué", today, "10:00", "12:00", "study", "Amphi B", "#DFBA7B", 0, now_str),
        ("Deep Work Algorithmique", "Résolution de problèmes et graphes", today, "14:00", "16:00", "deepwork", "Bureau privé", "#C6A76B", 0, now_str),
        ("Rapport d'architecture SQLite", "Rédaction et schémas", today, "16:30", "17:30", "task", "Bureau privé", "#E05D52", 0, now_str),
    ]
    cur.executemany("""
        INSERT INTO calendar_events (title, description, date, start_time, end_time, event_type, location, color, is_all_day, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, cal_data)

    # Seed Study Courses
    courses_data = [
        ("INFO501", "Systèmes Distribués", "Pr. Moreau", "S1", "#DFBA7B", 16.0, 15.0, now_str),
        ("INFO502", "Algorithmique Avancée & Graphes", "Pr. Durand", "S1", "#C6A76B", 17.0, 16.5, now_str),
        ("INFO503", "Bases de Données & Optimisation", "Pr. Leroy", "S1", "#7DD9A3", 16.0, 14.0, now_str),
        ("INFO504", "Architectures Logicielles Mobiles", "Pr. Bernard", "S1", "#E5A93B", 18.0, 17.0, now_str),
    ]
    cur.executemany("""
        INSERT INTO study_courses (code, name, professor, semester, color, target_grade, current_grade, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, courses_data)

    # Seed Exams
    exams_data = [
        (1, "Examen Final Systèmes Distribués", in_7_days, 2.0, "Amphi B", now_str),
        (2, "Partiel Algorithmique & Graphes", in_3_days, 1.5, "Salle 204", now_str),
        (3, "Projet Optimisation SQL", in_7_days, 1.0, "Lab 3", now_str),
    ]
    cur.executemany("""
        INSERT INTO study_exams (course_id, title, date, weight, room, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
    """, exams_data)

    # Seed Habits
    habits_data = [
        ("Séance Sport & Mobilité", "45 minutes minimum", "daily", 7, "#7DD9A3", "dumbbell", 14, 28, now_str),
        ("Lecture Technique (20 pages)", "Livres architecture et systèmes", "daily", 7, "#C6A76B", "book", 21, 35, now_str),
        ("Zéro Alcool & Sommeil 8h", "Récupération physique optimale", "daily", 7, "#E5A93B", "bed", 42, 60, now_str),
        ("Deep Work Matinal (90m)", "Travail sans distraction ni téléphone", "daily", 5, "#DFBA7B", "brain", 9, 21, now_str),
        ("Pratique Langues / Duolingo", "Allemand niveau B2", "daily", 7, "#6B9EE8", "translate", 18, 45, now_str),
    ]
    cur.executemany("""
        INSERT INTO habits (name, description, frequency, target_per_week, color, icon, streak_current, streak_best, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, habits_data)

    # Seed Habit Logs (past 7 days for the first few habits)
    logs_data = []
    for habit_id in range(1, 6):
        for days_back in range(7):
            d = (date.today() - timedelta(days=days_back)).isoformat()
            # Most habits are done, day 0 (today) done for some
            status = 1 if (days_back != 0 or habit_id in (1, 3)) else 0
            logs_data.append((habit_id, d, status, "Rituel accompli"))
    cur.executemany("""
        INSERT OR IGNORE INTO habit_logs (habit_id, date, status, notes)
        VALUES (?, ?, ?, ?);
    """, logs_data)

    # Seed Streaks
    streaks_data = [
        ("Protocole Exécutif Quotidien", "fire", 14, 30, today, "protocol"),
        ("Discipline Deep Work", "brain", 9, 21, today, "study"),
        ("Santé & Entraînement", "fitness", 14, 28, today, "fitness"),
        ("Sommeil Récupérateur", "moon", 12, 19, today, "wellness"),
    ]
    cur.executemany("""
        INSERT INTO streaks (name, icon, current_streak, best_streak, last_completed_date, category)
        VALUES (?, ?, ?, ?, ?, ?);
    """, streaks_data)

    # Seed Goals
    goals_data = [
        (
            "Valider le Semestre 1 avec Mention TB (> 16/20)",
            "Excellence académique sur tous les modules d'informatique théorique et appliquée.",
            "Académique", in_7_days, 75, "active",
            json.dumps([
                {"text": "Moyenne Systèmes Distribués >= 15", "done": True},
                {"text": "Moyenne Algorithmique >= 16", "done": True},
                {"text": "Partiel BD sans faute", "done": False},
                {"text": "Rendu projet mobile LifeOS", "done": False}
            ]),
            now_str
        ),
        (
            "Lancer LifeOS v1.0 sur Play Store & GitHub",
            "Finaliser l'application mobile hors-ligne avec interface Atelier OS irréprochable.",
            "Dev", in_7_days, 60, "active",
            json.dumps([
                {"text": "Maquettes Stitch validées", "done": True},
                {"text": "Backend FastAPI & SQLite fonctionnel", "done": True},
                {"text": "Tests Kivy et interactions UI complètes", "done": False},
                {"text": "Packaging APK Android avec Buildozer", "done": False}
            ]),
            now_str
        ),
        (
            "Atteindre 15% de masse grasse & 80kg au Développé Couché",
            "Programme d'entraînement de force et diète stricte.",
            "Santé", in_7_days, 85, "active",
            json.dumps([
                {"text": "Séances 4x par semaine régulières", "done": True},
                {"text": "Palier 75kg validé", "done": True},
                {"text": "Objectif 80kg validé en série", "done": False}
            ]),
            now_str
        ),
        (
            "Certification Architecture Logicielle Avancée",
            "Maîtrise des patterns hexagonaux, microservices et offline-first.",
            "Carrière", in_7_days, 30, "active",
            json.dumps([
                {"text": "Lecture 3 livres de référence", "done": True},
                {"text": "Réalisation de 2 projets démo", "done": False},
                {"text": "Examen blanc", "done": False}
            ]),
            now_str
        )
    ]
    cur.executemany("""
        INSERT INTO goals (title, description, category, target_date, progress, status, milestones_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, goals_data)

    # Seed Focus Sessions
    focus_data = [
        ("Deep Work Algorithmique", 2, 2, 45, "pomodoro", now_str),
        ("Rapport SQLite", 1, 1, 25, "pomodoro", now_str),
        ("Révision Systèmes Distribués", 5, 1, 25, "pomodoro", now_str),
    ]
    cur.executemany("""
        INSERT INTO focus_sessions (title, task_id, course_id, duration_minutes, mode, completed_at)
        VALUES (?, ?, ?, ?, ?, ?);
    """, focus_data)

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
