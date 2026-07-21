import React, { useState, useEffect } from "react";
import { fetchStats, fetchQuestions } from "../services/api";

export default function Stats({ onReviewQuestion, onStartRandom }) {
  const [statsData, setStatsData] = useState(null);
  const [solvedQuestions, setSolvedQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        setLoading(true);
        const [sData, qData] = await Promise.all([
          fetchStats(),
          fetchQuestions({ solved: 1 })
        ]);
        setStatsData(sData);
        setSolvedQuestions(qData);
      } catch (err) {
        console.error("Failed to load analytics stats:", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return (
      <section className="app-screen active">
        <h3 className="section-title">Análise de Desempenho</h3>
        <div style={{ padding: "4rem", textAlign: "center", color: "var(--text-secondary)" }}>
          Calculando estatísticas com SQLite local...
        </div>
      </section>
    );
  }

  const overall = statsData?.overall || { total_questions: 0, solved_count: 0, correct_count: 0, accuracy: 0 };

  if (overall.solved_count === 0) {
    return (
      <section className="app-screen active">
        <h3 className="section-title">Análise de Desempenho</h3>
        <div className="card" style={{ textAlign: "center", color: "var(--text-secondary)", padding: "4rem" }}>
          <span style={{ fontSize: "3rem", display: "block", marginBottom: "1rem" }}>📈</span>
          <h3>Nenhum dado de desempenho encontrado</h3>
          <p style={{ marginTop: "0.5rem", maxWidth: "500px", marginLeft: "auto", marginRight: "auto" }}>
            Comece a resolver questões nos simulados para visualizar aqui suas notas, pontos fortes, fracos e a estimativa de aprovação.
          </p>
          <button className="btn btn-primary" style={{ marginTop: "1.5rem" }} onClick={onStartRandom}>
            Iniciar Estudo Rápido
          </button>
        </div>
      </section>
    );
  }

  const incorrectQuestions = solvedQuestions.filter(q => q.is_correct === false);

  return (
    <section className="app-screen active">
      <h3 className="section-title">Análise de Desempenho (SQLite Motor Local)</h3>

      {/* Main KPI Grid */}
      <div className="stats-grid">
        <div className="card card-gradient">
          <div className="stat-icon">📊</div>
          <div className="stat-title">Questões Resolvidas</div>
          <div className="stat-value">{overall.solved_count} / {overall.total_questions}</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">🎯</div>
          <div className="stat-title">Taxa de Precisão Geral</div>
          <div className="stat-value">{overall.accuracy}%</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">✅</div>
          <div className="stat-title">Acertos</div>
          <div className="stat-value">{overall.correct_count}</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">❌</div>
          <div className="stat-title">Erros</div>
          <div className="stat-value">{overall.incorrect_count}</div>
        </div>
      </div>

      {/* Discipline Breakdown */}
      <h4 style={{ marginTop: "2rem", marginBottom: "1rem" }}>📚 Desempenho por Disciplina</h4>
      <div className="card">
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-secondary)" }}>
              <th style={{ padding: "0.75rem 0.5rem" }}>Disciplina</th>
              <th style={{ padding: "0.75rem 0.5rem" }}>Resolvidas</th>
              <th style={{ padding: "0.75rem 0.5rem" }}>Acertos</th>
              <th style={{ padding: "0.75rem 0.5rem" }}>Precisão</th>
            </tr>
          </thead>
          <tbody>
            {(statsData?.by_discipline || []).map(row => {
              const acc = row.solved > 0 ? Math.round((row.correct / row.solved) * 100) : 0;
              return (
                <tr key={row.discipline} style={{ borderBottom: "1px solid var(--border-color)" }}>
                  <td style={{ padding: "0.75rem 0.5rem", fontWeight: 500 }}>{row.discipline}</td>
                  <td style={{ padding: "0.75rem 0.5rem" }}>{row.solved} / {row.total}</td>
                  <td style={{ padding: "0.75rem 0.5rem" }}>{row.correct}</td>
                  <td style={{ padding: "0.75rem 0.5rem" }}>
                    <span className={`badge ${acc >= 70 ? "badge-success" : (acc >= 50 ? "badge-warning" : "badge-danger")}`}>
                      {acc}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Incorrect items review list */}
      {incorrectQuestions.length > 0 && (
        <>
          <h4 style={{ marginTop: "2rem", marginBottom: "1rem", color: "var(--color-danger)" }}>
            ⚠️ Caderno de Erros ({incorrectQuestions.length} questões para reforço)
          </h4>
          <div className="history-list">
            {incorrectQuestions.map(q => {
              const plainText = q.statement ? q.statement.replace(/<[^>]*>/g, "") : "";
              const preview = plainText.length > 120 ? plainText.substring(0, 120) + "..." : plainText;

              return (
                <div key={q.id} className="history-item" style={{ borderLeft: "4px solid var(--color-danger)" }}>
                  <div className="history-status-badge badge-incorrect">✗</div>
                  <div className="history-details">
                    <span className="history-exam-name">{q.exam_name}</span>
                    <p className="history-question-preview">Q{q.number}: {preview}</p>
                    <div className="history-meta">
                      <span>Disciplina: {q.discipline}</span> | 
                      <span>Sua Escolha: ({q.selected_option})</span> | 
                      <span>Gabarito: ({q.correct_answer || "N/A"})</span>
                    </div>
                  </div>
                  <div className="history-actions">
                    <button 
                      className="btn btn-secondary" 
                      onClick={() => onReviewQuestion && onReviewQuestion(q.exam_id, q.number)}
                    >
                      Rever
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </section>
  );
}
