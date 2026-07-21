import React, { useState, useEffect } from "react";
import { fetchQuestions } from "../services/api";

export default function History({ exams = [], onReviewQuestion }) {
  const [selectedExamFilter, setSelectedExamFilter] = useState("all");
  const [selectedStatusFilter, setSelectedStatusFilter] = useState("all");
  const [solvedQuestions, setSolvedQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await fetchQuestions({ solved: 1 });
        setSolvedQuestions(data);
      } catch (err) {
        console.error("Failed to load history:", err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  const filteredQuestions = solvedQuestions.filter(q => {
    if (selectedExamFilter !== "all" && q.exam_id !== selectedExamFilter) return false;
    if (selectedStatusFilter === "correct" && !q.is_correct) return false;
    if (selectedStatusFilter === "incorrect" && q.is_correct) return false;
    return true;
  });

  return (
    <section className="app-screen active">
      <h3 className="section-title">Histórico de Questões</h3>
      
      <div className="filters-bar">
        <div className="filters-group">
          <span className="filter-label">Filtrar por:</span>
          <select 
            className="select-filter" 
            aria-label="Filtrar por Concurso"
            value={selectedExamFilter}
            onChange={(e) => setSelectedExamFilter(e.target.value)}
          >
            <option value="all">Todos os Concursos</option>
            {exams.map(exam => {
              const examId = exam.id || exam.exam_id;
              const examName = exam.name || exam.exam_name;
              return (
                <option key={examId} value={examId}>
                  {examName}
                </option>
              );
            })}
          </select>

          <select 
            className="select-filter" 
            aria-label="Filtrar por Status"
            value={selectedStatusFilter}
            onChange={(e) => setSelectedStatusFilter(e.target.value)}
          >
            <option value="all">Todos os Status</option>
            <option value="correct">Apenas Acertos</option>
            <option value="incorrect">Apenas Erros</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-secondary)" }}>
          Carregando histórico do banco de dados SQLite...
        </div>
      ) : (
        <div className="history-list">
          {filteredQuestions.length === 0 ? (
            <div className="card" style={{ textAlign: "center", color: "var(--text-secondary)", padding: "3rem" }}>
              Nenhuma questão encontrada nos filtros. Resolva questões para popular seu histórico!
            </div>
          ) : (
            filteredQuestions.map(q => {
              const isCorrect = q.is_correct;
              const statusIcon = isCorrect ? "✓" : "✗";
              const statusBadgeClass = isCorrect ? "badge-correct" : "badge-incorrect";

              const plainStatement = q.statement ? q.statement.replace(/<[^>]*>/g, "") : "";
              const previewText = plainStatement.length > 140 ? plainStatement.substring(0, 140) + "..." : plainStatement;

              return (
                <div key={q.id} className="history-item">
                  <div className={`history-status-badge ${statusBadgeClass}`}>{statusIcon}</div>
                  <div className="history-details">
                    <span className="history-exam-name">{q.exam_name}</span>
                    <p className="history-question-preview">Q{q.number}: {previewText}</p>
                    <div className="history-meta">
                      <span>Disciplina: {q.discipline}</span> | 
                      <span>Sua Resposta: ({q.selected_option})</span> | 
                      <span>Gabarito: ({q.correct_answer || "N/A"})</span>
                    </div>
                  </div>
                  <div className="history-actions">
                    <button 
                      className="btn btn-secondary" 
                      onClick={() => onReviewQuestion(q.exam_id, q.number)}
                    >
                      Rever
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </section>
  );
}
