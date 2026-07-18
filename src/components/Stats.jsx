import React from "react";

export default function Stats({ exams, userState, onReviewQuestion, onStartRandom }) {
  // 1. Gather all questions and build maps
  const qMap = {};
  const examMap = {};
  
  exams.forEach(exam => {
    examMap[exam.exam_id] = {
      name: exam.exam_name,
      banca: exam.banca,
      total: 0,
      correct: 0,
      time: 0
    };
    exam.questions.forEach(q => {
      qMap[q.id] = {
        examId: exam.exam_id,
        examName: exam.exam_name,
        banca: exam.banca,
        discipline: q.discipline,
        number: q.number,
        correctAnswer: q.correct_answer,
        statement: q.statement
      };
    });
  });

  const solved = userState.solvedQuestions;
  let totalSolved = 0;
  let correctCount = 0;
  let incorrectCount = 0;
  let totalTime = 0;

  const disciplines = {};
  const examStats = {};
  const incorrectDetails = [];

  Object.entries(solved).forEach(([qId, info]) => {
    if (!info.solved) return;

    totalSolved++;
    const isCorrect = info.correct;
    const timeSpent = info.timeSpent || 0;
    totalTime += timeSpent;

    if (isCorrect) correctCount++;
    else incorrectCount++;

    const qDetails = qMap[qId] || {
      examId: "unknown",
      examName: "Desconhecido",
      banca: "Desconhecido",
      discipline: "Desconhecido",
      number: 0,
      correctAnswer: "",
      statement: ""
    };

    const disc = qDetails.discipline;
    const examId = qDetails.examId;

    // Group by discipline
    if (!disciplines[disc]) {
      disciplines[disc] = { total: 0, correct: 0, time: 0 };
    }
    disciplines[disc].total++;
    disciplines[disc].time += timeSpent;
    if (isCorrect) disciplines[disc].correct++;

    // Group by exam
    if (!examStats[examId]) {
      examStats[examId] = { name: qDetails.examName, banca: qDetails.banca, total: 0, correct: 0, time: 0 };
    }
    examStats[examId].total++;
    examStats[examId].time += timeSpent;
    if (isCorrect) examStats[examId].correct++;

    if (!isCorrect) {
      incorrectDetails.push({
        id: qId,
        number: qDetails.number,
        discipline: disc,
        examId: examId,
        examName: qDetails.examName,
        statement: qDetails.statement,
        selected: info.selectedOption,
        correctAnswer: qDetails.correctAnswer,
        time: timeSpent
      });
    }
  });

  if (totalSolved === 0) {
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

  const accuracy = totalSolved > 0 ? (correctCount / totalSolved * 100) : 0;
  const avgTime = totalSolved > 0 ? (totalTime / totalSolved) : 0;

  const hours = Math.floor(totalTime / 3600);
  const minutes = Math.floor((totalTime % 3600) / 60);
  const secs = totalTime % 60;
  const timeStr = hours > 0 ? `${hours}h ${minutes}m ${secs}s` : `${minutes}m ${secs}s`;

  // Dataprev score calculation
  const dpExamId = "ati-arquitetura-engenharia-e-sustentacao-tecnologica-cns002-tipo-01";
  const dpExamState = examStats[dpExamId];
  let dataprevCard = null;

  if (dpExamState) {
    let cgCorrect = 0;
    let cgTotal = 0;
    let ceCorrect = 0;
    let ceTotal = 0;

    const dpExam = exams.find(e => e.exam_id === dpExamId);
    if (dpExam) {
      dpExam.questions.forEach(q => {
        const isCorrect = solved[q.id]?.correct || false;
        if (q.number <= 40) {
          cgTotal++;
          if (isCorrect) cgCorrect++;
        } else {
          ceTotal++;
          if (isCorrect) ceCorrect++;
        }
      });
    }

    const dpScore = (cgCorrect * 1.0) + (ceCorrect * 2.5);
    const dpMax = (cgTotal * 1.0) + (ceTotal * 2.5);
    const dpPassed = dpScore >= 57.5;

    dataprevCard = (
      <div className="card analysis-card highlight-card" style={{ marginTop: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1.5rem" }}>
          <div style={{ flex: 1, minWidth: "280px" }}>
            <h4 style={{ fontSize: "1.15rem", marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-primary)" }}>
              🎯 Estimativa de Nota Oficial - DATAPREV 2024
            </h4>
            <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.5, marginBottom: "1rem" }}>
              {dpPassed ? (
                <>Sua nota de <strong>{dpScore.toFixed(1)} pontos</strong> ficou acima da pontuação de corte mínima do edital (<strong>57.5 pontos</strong>). Parabéns! Continue praticando para consolidar sua vaga.</>
              ) : (
                <>Sua nota de <strong>{dpScore.toFixed(1)} pontos</strong> ficou abaixo da pontuação de corte mínima do edital (<strong>57.5 pontos</strong>). Faltam apenas <strong>{(57.5 - dpScore).toFixed(1)} pontos</strong>. Reforce o estudo das matérias com menor precisão!</>
              )}
            </p>
            <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
              <div>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block" }}>Conhecimentos Gerais (Peso 1.0)</span>
                <strong style={{ fontSize: "1.1rem", color: "var(--text-primary)" }}>{cgCorrect} / {cgTotal} acertos ({cgCorrect * 1.0} pts)</strong>
              </div>
              <div>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", display: "block" }}>Conhecimentos Específicos (Peso 2.5)</span>
                <strong style={{ fontSize: "1.1rem", color: "var(--text-primary)" }}>{ceCorrect} / {ceTotal} acertos ({(ceCorrect * 2.5).toFixed(1)} pts)</strong>
              </div>
            </div>
          </div>
          <div style={{ textAlign: "center", minWidth: "180px", alignSelf: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div className="score-radial-progress">
              <span className="score-number">{dpScore.toFixed(1)}</span>
              <span className="score-max">/ {dpMax} pts</span>
            </div>
            <div style={{ marginTop: "0.75rem" }}>
              {dpPassed ? (
                <span className="badge badge-success">🟢 APROVADO NO SIMULADO (Pontuação: {dpScore.toFixed(1)} / {dpMax.toFixed(1)})</span>
              ) : (
                <span className="badge badge-danger">🔴 DESCLASSIFICADO NO SIMULADO (Pontuação: {dpScore.toFixed(1)} / {dpMax.toFixed(1)})</span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Strengths and Weaknesses
  let bestDisc = "";
  let bestAcc = -1;
  let worstDisc = "";
  let worstAcc = 101;

  Object.entries(disciplines).forEach(([disc, stat]) => {
    const acc = stat.correct / stat.total * 100;
    if (stat.total >= 2) {
      if (acc > bestAcc) {
        bestAcc = acc;
        bestDisc = disc;
      }
      if (acc < worstAcc) {
        worstAcc = acc;
        worstDisc = disc;
      }
    }
  });

  // Slowest questions list
  const slowQuestions = Object.entries(solved)
    .filter(([_, info]) => info.solved)
    .map(([qId, info]) => ({ id: qId, ...info }))
    .sort((a, b) => (b.timeSpent || 0) - (a.timeSpent || 0))
    .slice(0, 5);

  return (
    <section className="app-screen active">
      <h3 className="section-title">Análise de Desempenho</h3>
      
      <div className="stats-grid">
        <div className="card card-gradient">
          <div className="stat-icon">📈</div>
          <div className="stat-title">Questões Resolvidas</div>
          <div className="stat-value">{totalSolved}</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">🎯</div>
          <div className="stat-title">Taxa de Acerto</div>
          <div className="stat-value">{accuracy.toFixed(1)}%</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">⏱️</div>
          <div className="stat-title">Tempo de Estudo</div>
          <div className="stat-value" style={{ fontSize: "1.5rem", lineHeight: "1.8rem", marginTop: "0.2rem" }}>{timeStr}</div>
        </div>
        <div className="card card-gradient">
          <div className="stat-icon">⚡</div>
          <div className="stat-title">Média por Questão</div>
          <div className="stat-value">{avgTime.toFixed(1)}s</div>
        </div>
      </div>

      {dataprevCard}

      {(bestDisc || worstDisc) && (
        <div className="analysis-grid-two" style={{ marginTop: "1.5rem" }}>
          <div className="card analysis-card">
            <h4 style={{ color: "var(--success)", display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
              <span>🟢</span> Ponto Forte
            </h4>
            {bestDisc ? (
              <>
                <p style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>{bestDisc}</p>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
                  Aproveitamento excelente de <strong>{bestAcc.toFixed(1)}%</strong>. Você está dominando este assunto!
                </p>
              </>
            ) : (
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Resolva mais questões de cada disciplina para identificar seu ponto forte.
              </p>
            )}
          </div>
          <div className="card analysis-card">
            <h4 style={{ color: "var(--danger)", display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
              <span>🔴</span> Oportunidade de Melhoria
            </h4>
            {worstDisc ? (
              <>
                <p style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>{worstDisc}</p>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
                  Aproveitamento de apenas <strong>{worstAcc.toFixed(1)}%</strong>. Sugerimos focar em revisar a teoria básica desta matéria.
                </p>
              </>
            ) : (
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Resolva mais questões de cada disciplina para identificar áreas de melhoria.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Discipline breakdown table */}
      <div className="card analysis-card" style={{ marginTop: "1.5rem" }}>
        <h4 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-primary)" }}>
          📚 Detalhamento por Disciplina
        </h4>
        <div className="table-responsive">
          <table className="analysis-table">
            <thead>
              <tr>
                <th>Disciplina</th>
                <th style={{ textAlign: "center" }}>Resolvidas</th>
                <th style={{ textAlign: "center" }}>Acertos</th>
                <th style={{ textAlign: "center" }}>Erros</th>
                <th style={{ minWidth: "180px" }}>Aproveitamento</th>
                <th>Tempo Total</th>
                <th>Tempo Médio</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(disciplines)
                .sort((a, b) => (b[1].correct / b[1].total) - (a[1].correct / a[1].total))
                .map(([disc, stat]) => {
                  const discAcc = (stat.correct / stat.total * 100);
                  const discAvg = (stat.time / stat.total);
                  const progressColor = discAcc >= 75 ? "var(--success)" : (discAcc >= 50 ? "var(--warning)" : "var(--danger)");
                  
                  const dh = Math.floor(stat.time / 3600);
                  const dm = Math.floor((stat.time % 3600) / 60);
                  const ds = stat.time % 60;
                  const dTimeStr = dh > 0 ? `${dh}h ${dm}m ${ds}s` : `${dm}m ${ds}s`;

                  return (
                    <tr key={disc}>
                      <td style={{ fontWeight: 600 }}>{disc}</td>
                      <td style={{ textAlign: "center" }}>{stat.total}</td>
                      <td style={{ textAlign: "center", color: "var(--success)", fontWeight: 600 }}>{stat.correct}</td>
                      <td style={{ textAlign: "center", color: "var(--danger)", fontWeight: 600 }}>{stat.total - stat.correct}</td>
                      <td>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
                          <div className="progress-bar-container" style={{ flexGrow: 1, height: "8px" }}>
                            <div className="progress-bar" style={{ width: `${discAcc}%`, backgroundColor: progressColor }}></div>
                          </div>
                          <span style={{ fontSize: "0.85rem", fontWeight: 600, minWidth: "45px", textAlign: "right" }}>{discAcc.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td>{dTimeStr}</td>
                      <td>{discAvg.toFixed(1)}s</td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Exam breakdown table */}
      <div className="card analysis-card" style={{ marginTop: "1.5rem" }}>
        <h4 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-primary)" }}>
          📝 Detalhamento por Concurso
        </h4>
        <div className="table-responsive">
          <table className="analysis-table">
            <thead>
              <tr>
                <th>Concurso</th>
                <th style={{ textAlign: "center" }}>Resolvidas</th>
                <th style={{ textAlign: "center" }}>Acertos</th>
                <th style={{ textAlign: "center" }}>Erros</th>
                <th>Aproveitamento</th>
                <th>Tempo Total</th>
                <th>Tempo Médio</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(examStats)
                .sort((a, b) => (b[1].correct / b[1].total) - (a[1].correct / a[1].total))
                .map(([exId, stat]) => {
                  const exAcc = (stat.correct / stat.total * 100);
                  const exAvg = (stat.time / stat.total);
                  
                  const eh = Math.floor(stat.time / 3600);
                  const em = Math.floor((stat.time % 3600) / 60);
                  const es = stat.time % 60;
                  const eTimeStr = eh > 0 ? `${eh}h ${em}m ${es}s` : `${em}m ${es}s`;

                  return (
                    <tr key={exId}>
                      <td style={{ fontWeight: 600 }}>
                        {stat.name}
                        <span className="badge" style={{ backgroundColor: "var(--bg-tertiary)", color: "var(--text-primary)", marginLeft: "0.5rem" }}>
                          {stat.banca}
                        </span>
                      </td>
                      <td style={{ textAlign: "center" }}>{stat.total}</td>
                      <td style={{ textAlign: "center", color: "var(--success)", fontWeight: 600 }}>{stat.correct}</td>
                      <td style={{ textAlign: "center", color: "var(--danger)", fontWeight: 600 }}>{stat.total - stat.correct}</td>
                      <td style={{ fontWeight: 600, color: "var(--text-primary)" }}>{exAcc.toFixed(1)}%</td>
                      <td>{eTimeStr}</td>
                      <td>{exAvg.toFixed(1)}s</td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Slowest questions table */}
      {slowQuestions.length > 0 && (
        <div className="card analysis-card" style={{ marginTop: "1.5rem" }}>
          <h4 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-primary)" }}>
            ⏱️ Questões mais demoradas
          </h4>
          <div className="table-responsive">
            <table className="analysis-table">
              <thead>
                <tr>
                  <th>Questão</th>
                  <th>Resultado</th>
                  <th>Sua Resposta</th>
                  <th>Tempo Gasto</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                {slowQuestions.map(item => {
                  const qDetails = qMap[item.id] || { discipline: "N/A", number: 0, examId: "" };
                  return (
                    <tr key={item.id}>
                      <td>Q{qDetails.number} ({qDetails.discipline})</td>
                      <td>
                        {item.correct ? (
                          <span style={{ color: "var(--success)", fontWeight: 600 }}>✓ Correta</span>
                        ) : (
                          <span style={{ color: "var(--danger)", fontWeight: 600 }}>✗ Incorreta</span>
                        )}
                      </td>
                      <td>Opção ({item.selectedOption})</td>
                      <td style={{ fontWeight: 600 }}>{item.timeSpent}s</td>
                      <td>
                        <button 
                          className="btn btn-secondary btn-sm" 
                          onClick={() => onReviewQuestion(qDetails.examId, qDetails.number)}
                        >
                          Rever
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Incorrect details list */}
      {incorrectDetails.length > 0 && (
        <div className="card analysis-card" style={{ marginTop: "1.5rem" }}>
          <h4 style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--danger)" }}>
            ❌ Detalhamento dos Erros ({incorrectDetails.length})
          </h4>
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "1.25rem" }}>
            Analise os enunciados das questões incorretas e revise sua linha de raciocínio. Clique em "Rever no Praticar" para responder novamente e visualizar os comentários completos.
          </p>
          <div className="error-details-list">
            {incorrectDetails.map((err, i) => {
              let stmtText = err.statement.trim().replace(/<[^>]*>/g, "");
              if (stmtText.length > 250) {
                stmtText = stmtText.substring(0, 250) + "...";
              }
              return (
                <div key={err.id} className="error-detail-item">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem", gap: "1rem", flexWrap: "wrap" }}>
                    <div>
                      <span className="error-badge">Erro {i + 1}</span>
                      <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)", marginLeft: "0.5rem" }}>
                        Q{err.number} - {err.discipline}
                      </span>
                    </div>
                    <button 
                      className="btn btn-secondary btn-sm" 
                      onClick={() => onReviewQuestion(err.examId, err.number)}
                    >
                      ⚙️ Rever no Praticar
                    </button>
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontStyle: "italic", marginBottom: "0.5rem" }}>
                    "{err.examName}"
                  </p>
                  <p className="error-statement-preview">
                    {stmtText}
                  </p>
                  <div style={{ marginTop: "0.75rem", display: "flex", gap: "1.5rem", fontSize: "0.85rem", flexWrap: "wrap" }}>
                    <span style={{ color: "var(--danger)", fontWeight: 600 }}>Sua Resposta: ({err.selected})</span>
                    <span style={{ color: "var(--success)", fontWeight: 600 }}>Gabarito: ({err.correctAnswer})</span>
                    <span style={{ color: "var(--text-muted)" }}>Tempo Gasto: {err.time}s</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
