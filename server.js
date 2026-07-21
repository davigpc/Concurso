import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import Database from 'better-sqlite3';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;
const DB_PATH = path.join(__dirname, 'concurso.db');

// Middleware
app.use(cors());
app.use(express.json());
app.use('/images/provas', express.static(path.join(__dirname, 'public', 'images', 'provas')));

// Open SQLite connection
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');

console.log(`[SQLite] Connected to ${DB_PATH}`);

// ---------------------------------------------------------------------------
// 1. GET /api/exams - List all exams with statistics
// ---------------------------------------------------------------------------
app.get('/api/exams', (req, res) => {
  try {
    const exams = db.prepare(`
      SELECT 
        e.id,
        e.name,
        e.banca,
        e.year,
        COUNT(q.id) as total_questions,
        SUM(CASE WHEN p.solved = 1 THEN 1 ELSE 0 END) as solved_count,
        SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct_count
      FROM exams e
      LEFT JOIN questions q ON e.id = q.exam_id
      LEFT JOIN user_progress p ON q.id = p.question_id
      GROUP BY e.id
      ORDER BY e.name ASC
    `).all();

    res.json(exams);
  } catch (err) {
    console.error('Error fetching exams:', err);
    res.status(500).json({ error: 'Failed to fetch exams' });
  }
});

// ---------------------------------------------------------------------------
// 2. GET /api/questions - List/Filter questions
// ---------------------------------------------------------------------------
app.get('/api/questions', (req, res) => {
  try {
    const { exam_id, discipline, solved } = req.query;

    let query = `
      SELECT 
        q.id,
        q.exam_id,
        q.number,
        q.discipline,
        q.type,
        q.statement,
        q.support_text,
        q.correct_answer,
        q.explanation,
        q.images_json,
        e.name as exam_name,
        e.banca,
        p.solved,
        p.selected_option,
        p.is_correct,
        p.is_starred
      FROM questions q
      JOIN exams e ON q.exam_id = e.id
      LEFT JOIN user_progress p ON q.id = p.question_id
      WHERE 1=1
    `;

    const params = [];

    if (exam_id) {
      query += ` AND q.exam_id = ?`;
      params.push(exam_id);
    }
    if (discipline) {
      query += ` AND q.discipline = ?`;
      params.push(discipline);
    }
    if (solved !== undefined) {
      query += ` AND COALESCE(p.solved, 0) = ?`;
      params.push(Number(solved));
    }

    query += ` ORDER BY q.exam_id, q.number ASC`;

    const questions = db.prepare(query).all(params);

    // Attach options & images to each question
    const getOptions = db.prepare(`SELECT option_key, option_text FROM options WHERE question_id = ? ORDER BY option_key ASC`);

    const result = questions.map(q => {
      const optsRows = getOptions.all(q.id);
      const optionsMap = {};
      optsRows.forEach(opt => {
        optionsMap[opt.option_key] = opt.option_text;
      });

      let images = [];
      try {
        if (q.images_json) images = JSON.parse(q.images_json);
      } catch (e) {}

      return {
        id: q.id,
        exam_id: q.exam_id,
        exam_name: q.exam_name,
        banca: q.banca,
        number: q.number,
        discipline: q.discipline,
        type: q.type,
        statement: q.statement,
        support_text: q.support_text,
        correct_answer: q.correct_answer,
        explanation: q.explanation,
        options: optionsMap,
        images: images,
        solved: Boolean(q.solved),
        selected_option: q.selected_option || null,
        is_correct: q.is_correct === 1 ? true : (q.is_correct === 0 ? false : null),
        is_starred: Boolean(q.is_starred)
      };
    });

    res.json(result);
  } catch (err) {
    console.error('Error fetching questions:', err);
    res.status(500).json({ error: 'Failed to fetch questions' });
  }
});

// ---------------------------------------------------------------------------
// 3. GET /api/questions/:id - Single question details
// ---------------------------------------------------------------------------
app.get('/api/questions/:id', (req, res) => {
  try {
    const q = db.prepare(`
      SELECT 
        q.*,
        e.name as exam_name,
        e.banca,
        p.solved,
        p.selected_option,
        p.is_correct,
        p.is_starred
      FROM questions q
      JOIN exams e ON q.exam_id = e.id
      LEFT JOIN user_progress p ON q.id = p.question_id
      WHERE q.id = ?
    `).get(req.params.id);

    if (!q) {
      return res.status(404).json({ error: 'Question not found' });
    }

    const optsRows = db.prepare(`SELECT option_key, option_text FROM options WHERE question_id = ? ORDER BY option_key ASC`).all(q.id);
    const optionsMap = {};
    optsRows.forEach(opt => {
      optionsMap[opt.option_key] = opt.option_text;
    });

    let images = [];
    try {
      if (q.images_json) images = JSON.parse(q.images_json);
    } catch (e) {}

    res.json({
      id: q.id,
      exam_id: q.exam_id,
      exam_name: q.exam_name,
      banca: q.banca,
      number: q.number,
      discipline: q.discipline,
      type: q.type,
      statement: q.statement,
      support_text: q.support_text,
      correct_answer: q.correct_answer,
      explanation: q.explanation,
      options: optionsMap,
      images: images,
      solved: Boolean(q.solved),
      selected_option: q.selected_option || null,
      is_correct: q.is_correct === 1 ? true : (q.is_correct === 0 ? false : null),
      is_starred: Boolean(q.is_starred)
    });
  } catch (err) {
    console.error('Error fetching question:', err);
    res.status(500).json({ error: 'Failed to fetch question' });
  }
});

// ---------------------------------------------------------------------------
// 4. POST /api/progress - Save user answer & progress
// ---------------------------------------------------------------------------
app.post('/api/progress', (req, res) => {
  try {
    const { question_id, selected_option, is_correct, is_starred } = req.body;

    if (!question_id) {
      return res.status(400).json({ error: 'question_id is required' });
    }

    const stmt = db.prepare(`
      INSERT INTO user_progress (question_id, solved, selected_option, is_correct, is_starred, updated_at)
      VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(question_id) DO UPDATE SET
        solved = excluded.solved,
        selected_option = COALESCE(excluded.selected_option, selected_option),
        is_correct = COALESCE(excluded.is_correct, is_correct),
        is_starred = COALESCE(excluded.is_starred, is_starred),
        updated_at = CURRENT_TIMESTAMP
    `);

    const isCorrectInt = is_correct === true ? 1 : (is_correct === false ? 0 : null);
    const isStarredInt = is_starred === true ? 1 : (is_starred === false ? 0 : null);
    const solvedInt = (selected_option !== undefined || is_correct !== undefined) ? 1 : 0;

    stmt.run(question_id, solvedInt, selected_option || null, isCorrectInt, isStarredInt);

    res.json({ success: true, question_id });
  } catch (err) {
    console.error('Error saving progress:', err);
    res.status(500).json({ error: 'Failed to save progress' });
  }
});

// ---------------------------------------------------------------------------
// 5. GET /api/stats - Dashboard analytics
// ---------------------------------------------------------------------------
app.get('/api/stats', (req, res) => {
  try {
    const overall = db.prepare(`
      SELECT 
        (SELECT COUNT(*) FROM questions) as total_questions,
        (SELECT COUNT(*) FROM user_progress WHERE solved = 1) as solved_count,
        (SELECT COUNT(*) FROM user_progress WHERE is_correct = 1) as correct_count,
        (SELECT COUNT(*) FROM user_progress WHERE is_correct = 0) as incorrect_count,
        (SELECT COUNT(*) FROM user_progress WHERE is_starred = 1) as starred_count
    `).get();

    const byDiscipline = db.prepare(`
      SELECT 
        q.discipline,
        COUNT(q.id) as total,
        SUM(CASE WHEN p.solved = 1 THEN 1 ELSE 0 END) as solved,
        SUM(CASE WHEN p.is_correct = 1 THEN 1 ELSE 0 END) as correct
      FROM questions q
      LEFT JOIN user_progress p ON q.id = p.question_id
      GROUP BY q.discipline
      ORDER BY total DESC
    `).all();

    res.json({
      overall: {
        total_questions: overall.total_questions,
        solved_count: overall.solved_count,
        correct_count: overall.correct_count,
        incorrect_count: overall.incorrect_count,
        starred_count: overall.starred_count,
        accuracy: overall.solved_count > 0 
          ? Math.round((overall.correct_count / overall.solved_count) * 100) 
          : 0
      },
      by_discipline: byDiscipline
    });
  } catch (err) {
    console.error('Error fetching stats:', err);
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});

// Start Express Server
app.listen(PORT, () => {
  console.log(`[Express API] Server running at http://localhost:${PORT}`);
});
