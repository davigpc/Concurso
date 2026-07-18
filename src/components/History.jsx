import React, { useState } from "react";

export default function History({ exams, userState, onReviewQuestion }) {
  const [selectedExamFilter, setSelectedExamFilter] = useState("all");
  const [selectedStatusFilter, setSelectedStatusFilter] = useState("all");

  const itemsToRender = [];

  exams.forEach(exam => {
    if (selectedExamFilter !== "all" && exam.exam_id !== selectedExamFilter) return;

    exam.questions.forEach(q => {
      const state = userState.solvedQuestions[q.id];
      if (!state || !state.solved) return;

      if (selectedStatusFilter === "correct" && !state.correct) return;
      if (selectedStatusFilter === "incorrect" && state.correct) return;

      itemsToRender.push({
        question: q,
        exam: exam,
        state: state
      });
    });
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
            {exams.map(exam => (
              <option key={exam.exam_id} value={exam.exam_id}>
                {exam.exam_name}
              </option>
            ))}
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

      <div className="history-list">
        {itemsToRender.length === 0 ? (
          <div className="card" style={{ textAlign: "center", color: "var(--text-secondary)", padding: "3rem" }}>
            Nenhuma questão encontrada nos filtros. Resolva questões para popular seu histórico!
          </div>
        ) : (
          itemsToRender.map(item => {
            const statusBadgeClass = item.state.correct ? "badge-correct" : "badge-incorrect";
            const statusIcon = item.state.correct ? "✓" : "✗";

            const plainStatement = item.question.statement.replace(/<[^>]*>/g, "");
            const previewText = plainStatement.length > 140 ? plainStatement.substring(0, 140) + "..." : plainStatement;

            return (
              <div key={item.question.id} className="history-item">
                <div className="history-status-badge badge-correct">{statusIcon}</div>
                <div className="history-details">
                  <span className="history-exam-name">{item.exam.exam_name}</span>
                  <p className="history-question-preview">Q{item.question.number}: {previewText}</p>
                  <div className="history-meta">
                    <span>Assunto: {item.question.discipline}</span> | 
                    <span>Resposta: ({item.state.selectedOption})</span> | 
                    <span>Tempo: {item.state.timeSpent || 0}s</span>
                  </div>
                </div>
                <div className="history-actions">
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => onReviewQuestion(item.exam.exam_id, item.question.number)}
                  >
                    Rever
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
