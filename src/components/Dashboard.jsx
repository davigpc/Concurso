import React from "react";

export default function Dashboard({ exams, userState, onStartExam, onStartRandom, onSwitchScreen }) {
  // Compute global stats
  let totalSolved = 0;
  let correctCount = 0;
  let starredCount = Object.keys(userState.starredQuestions).filter(k => userState.starredQuestions[k]).length;

  exams.forEach(exam => {
    exam.questions.forEach(q => {
      const state = userState.solvedQuestions[q.id];
      if (state && state.solved) {
        totalSolved++;
        if (state.correct) correctCount++;
      }
    });
  });

  const accuracy = totalSolved > 0 ? Math.round((correctCount / totalSolved) * 100) : 0;

  return (
    <section className="app-screen active">
      <div className="stats-grid">
        <div className="card card-gradient">
          <div className="stat-icon">✅</div>
          <div className="stat-title">Questões Resolvidas</div>
          <div className="stat-value">{totalSolved}</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">🎯</div>
          <div className="stat-title">Taxa de Precisão</div>
          <div className="stat-value">{accuracy}%</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">🏆</div>
          <div className="stat-title">Total de Acertos</div>
          <div className="stat-value">{correctCount}</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">⭐</div>
          <div className="stat-title">Questões Salvas</div>
          <div className="stat-value">{starredCount}</div>
        </div>
      </div>

      <div className="card" style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginTop: "1.5rem",
        padding: "1.25rem",
        background: "linear-gradient(135deg, var(--bg-secondary), var(--bg-primary))",
        border: "1px dashed var(--border-color)",
        borderRadius: "var(--radius-md)",
        gap: "1rem",
        flexWrap: "wrap"
      }}>
        <div>
          <h4 style={{ margin: "0 0 0.25rem 0", fontSize: "1rem", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            📈 Relatório Estatístico e Notas de Corte
          </h4>
          <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            Veja o cálculo ponderado da sua nota oficial para a prova da DATAPREV (conforme edital FGV) e comparação com a lista de aprovados.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={() => onSwitchScreen("analysis-screen")}>
          Ver Análise Detalhada
        </button>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1.5rem" }}>
        <h3 className="section-title">Navegar por Concurso</h3>
        <button className="btn btn-primary" onClick={onStartRandom}>⚡ Estudo Rápido (Aleatório)</button>
      </div>

      <div className="exams-list">
        {exams.map(exam => {
          const totalExamQuestions = exam.questions.length;
          let examSolved = 0;
          
          exam.questions.forEach(q => {
            if (userState.solvedQuestions[q.id]?.solved) {
              examSolved++;
            }
          });

          const progressPercent = Math.round((examSolved / totalExamQuestions) * 100) || 0;

          return (
            <div key={exam.exam_id} className="exam-card">
              <div className="exam-header">
                <span className="exam-badge">{exam.banca}</span>
              </div>
              <h3 className="exam-title">{exam.exam_name}</h3>
              <div className="exam-meta">
                <span>{totalExamQuestions} Questões</span>
                <span>Resolvidas: {examSolved}/{totalExamQuestions}</span>
              </div>
              <div className="exam-progress">
                <div className="progress-bar-container">
                  <div className="progress-bar" style={{ width: `${progressPercent}%` }}></div>
                </div>
                <div style={{ fontSize: "0.8rem", textAlign: "right", color: "var(--text-secondary)" }}>
                  {progressPercent}% Concluído
                </div>
              </div>
              <button className="exam-btn" onClick={() => onStartExam(exam.exam_id)}>
                Estudar Agora
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}
