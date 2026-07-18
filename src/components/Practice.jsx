import React, { useState, useEffect, useRef } from "react";

function parseMarkdown(text) {
  if (!text) return "";
  let html = text;
  html = html.replace(/^### (.*$)/gim, '<h5 style="margin-top: 1rem; margin-bottom: 0.5rem; color: var(--accent-primary);">$1</h5>');
  html = html.replace(/^## (.*$)/gim, '<h4 style="margin-top: 1rem; margin-bottom: 0.5rem; color: var(--accent-primary);">$1</h4>');
  html = html.replace(/^# (.*$)/gim, '<h3 style="margin-top: 1.25rem; margin-bottom: 0.75rem; color: var(--accent-primary);">$1</h3>');
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/`(.*?)`/g, '<code style="background-color: var(--bg-primary); padding: 0.15rem 0.3rem; border-radius: 4px; font-family: monospace; font-size: 0.9em; border: 1px solid var(--border-color);">$1</code>');
  html = html.replace(/^\> (.*$)/gim, '<blockquote style="border-left: 3px solid var(--accent-secondary); padding-left: 1rem; color: var(--text-secondary); margin: 0.75rem 0; font-style: italic;">$1</blockquote>');
  html = html.replace(/^\s*[-\*]\s+(.*$)/gim, '<li style="margin-left: 1.5rem; margin-bottom: 0.25rem;">$1</li>');
  html = html.replace(/\n/g, '<br>');
  return html;
}

export default function Practice({ 
  exam, 
  userState, 
  onSaveQuestionState, 
  onToggleStar, 
  onGoBack,
  initialQuestionIndex = 0
}) {
  const questions = exam.questions;
  const [currentIndex, setCurrentIndex] = useState(initialQuestionIndex);
  const [selectedOption, setSelectedOption] = useState(null);
  
  // Session stats state
  const [sessionSolved, setSessionSolved] = useState(0);
  const [sessionCorrect, setSessionCorrect] = useState(0);
  const [sessionIncorrect, setSessionIncorrect] = useState(0);
  const [seconds, setSeconds] = useState(0);

  // AI state
  const [loadingAi, setLoadingAi] = useState(false);
  const [aiExplanation, setAiExplanation] = useState(null);
  const [aiError, setAiError] = useState(null);

  const activeQuestion = questions[currentIndex];
  const solvedData = userState.solvedQuestions[activeQuestion?.id];
  const isStarred = !!userState.starredQuestions[activeQuestion?.id];

  // Sync currentIndex to initialQuestionIndex on prop change
  useEffect(() => {
    setCurrentIndex(initialQuestionIndex);
  }, [initialQuestionIndex]);

  // Reset selected option and load AI explanation for the active question
  useEffect(() => {
    if (solvedData && solvedData.solved) {
      setSelectedOption(solvedData.selectedOption);
      setAiExplanation(solvedData.aiExplanation || null);
    } else {
      setSelectedOption(null);
      setAiExplanation(null);
    }
    setAiError(null);
  }, [currentIndex, solvedData]);

  // Timer effect
  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Format timer
  const formatTime = () => {
    const mins = Math.floor(seconds / 60).toString().padStart(2, "0");
    const secs = (seconds % 60).toString().padStart(2, "0");
    return `⏱️ ${mins}:${secs}`;
  };

  const handleVerify = () => {
    if (!selectedOption || (solvedData && solvedData.solved)) return;

    const correct = selectedOption === activeQuestion.correct_answer;
    
    // Update session stats
    setSessionSolved(prev => prev + 1);
    if (correct) {
      setSessionCorrect(prev => prev + 1);
    } else {
      setSessionIncorrect(prev => prev + 1);
    }

    onSaveQuestionState(activeQuestion.id, {
      solved: true,
      correct: correct,
      selectedOption: selectedOption,
      timeSpent: 0 // Optional tracking
    });
  };

  const triggerGeminiExplanation = async (force = false) => {
    if (!solvedData || !solvedData.solved) return;
    if (solvedData.aiExplanation && !force) {
      setAiExplanation(solvedData.aiExplanation);
      return;
    }

    setLoadingAi(true);
    setAiError(null);
    setAiExplanation(null);

    const apiKey = userState.geminiApiKey || "";
    if (!apiKey) {
      setAiError("Chave da API do Gemini não configurada nas Configurações!");
      setLoadingAi(false);
      return;
    }

    try {
      const prompt = `Você é um professor experiente em concursos públicos. Analise a seguinte questão e explique detalhadamente de forma didática:
1) Por que a alternativa correta é a verdadeira.
2) O erro de cada uma das outras alternativas.
3) Preste atenção especial na alternativa que o estudante escolheu (se for diferente da correta), mostrando onde está a pegadinha ou o erro de raciocínio.

DADOS DA QUESTÃO:
- Concurso: ${exam.exam_name}
- Disciplina: ${activeQuestion.discipline}
- Enunciado:
${activeQuestion.statement.replace(/<[^>]*>/g, "")}

- Alternativas:
${Object.entries(activeQuestion.options).map(([k, v]) => `  (${k}) ${v.replace(/<[^>]*>/g, "")}`).join('\n')}

- Gabarito Oficial (Correta): Alternativa ${activeQuestion.correct_answer}
- Resposta Escolhida pelo Estudante: Alternativa ${solvedData.selectedOption} (${solvedData.correct ? 'O estudante ACERTOU' : 'O estudante ERROU'})

Escreva a explicação de forma clara, amigável e direta em português. Utilize formatação Markdown (negritos, listas, blocos de citação) para destacar os pontos importantes.`;

      const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=${apiKey}`;
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }]
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error?.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (text) {
        const html = parseMarkdown(text);
        setAiExplanation(html);
        onSaveQuestionState(activeQuestion.id, {
          ...solvedData,
          aiExplanation: html
        });
      } else {
        throw new Error("Resposta inválida da API do Gemini.");
      }
    } catch (e) {
      console.error(e);
      setAiError(`Erro ao chamar o Gemini: ${e.message}`);
    } finally {
      setLoadingAi(false);
    }
  };

  const isSolved = !!solvedData?.solved;
  const isCorrect = !!solvedData?.correct;

  return (
    <section className="app-screen active">
      <div className="practice-container">
        {/* Left Panel: The Question Box */}
        <div className="quiz-card">
          <div className="quiz-header">
            <div className="quiz-meta-info">
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 600 }}>
                {exam.exam_name}
              </span>
              <span className="quiz-discipline">{activeQuestion.discipline}</span>
            </div>
            <div className="timer-box">{formatTime()}</div>
          </div>
          
          <div style={{ fontSize: "0.9rem", color: "var(--text-secondary)", fontWeight: 600, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Questão {currentIndex + 1} de {questions.length}</span>
            <button className="btn btn-secondary btn-sm" onClick={onGoBack}>Voltar ao Painel</button>
          </div>

          <div 
            className="question-text" 
            dangerouslySetInnerHTML={{ __html: activeQuestion.statement.replace(/\n/g, "<br>") }}
          />
          
          {/* Options container */}
          <div className="options-list">
            {Object.entries(activeQuestion.options).map(([optionChar, optionText]) => {
              const isSelected = selectedOption === optionChar;
              let optionClass = "option-item";
              
              if (isSolved) {
                if (optionChar === activeQuestion.correct_answer) {
                  optionClass += " correct";
                } else if (isSelected) {
                  optionClass += " incorrect";
                } else {
                  optionClass += " disabled";
                }
              } else if (isSelected) {
                optionClass += " selected";
              }

              return (
                <div 
                  key={optionChar} 
                  className={optionClass}
                  onClick={() => !isSolved && setSelectedOption(optionChar)}
                >
                  <div className="option-marker">{optionChar}</div>
                  <div 
                    className="option-text" 
                    dangerouslySetInnerHTML={{ __html: optionText }}
                  />
                </div>
              );
            })}
          </div>
          
          <div className="quiz-actions">
            <button 
              className={`btn btn-secondary ${isStarred ? "starred" : ""}`}
              onClick={() => onToggleStar(activeQuestion.id)}
            >
              {isStarred ? "★ Salvo" : "☆ Salvar"}
            </button>
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button 
                className="btn btn-secondary" 
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex(prev => prev - 1)}
              >
                Anterior
              </button>
              
              {isSolved && (
                <button 
                  className="btn btn-secondary"
                  style={{ borderColor: "var(--border-focus)", color: "var(--border-focus)", fontWeight: 500 }}
                  onClick={() => triggerGeminiExplanation()}
                >
                  ✨ {aiExplanation ? "Ver Explicação IA" : "Explicar com IA"}
                </button>
              )}

              {!isSolved && (
                <button 
                  className="btn btn-primary" 
                  disabled={!selectedOption}
                  onClick={handleVerify}
                >
                  Responder
                </button>
              )}

              <button 
                className="btn btn-secondary" 
                disabled={currentIndex === questions.length - 1}
                onClick={() => setCurrentIndex(prev => prev + 1)}
              >
                Próxima
              </button>
            </div>
          </div>

          {/* Comment/Explanation Box (FGV has default explanations sometimes, if provided) */}
          {isSolved && activeQuestion.explanation && (
            <div className="explanation-box">
              <span className="explanation-title">💡 Comentário e Justificativa</span>
              <p 
                className="explanation-content"
                dangerouslySetInnerHTML={{ __html: activeQuestion.explanation.replace(/\n/g, "<br>") }}
              />
            </div>
          )}

          {/* AI Explanation Box */}
          {loadingAi && (
            <div className="explanation-box" style={{ display: "flex", borderLeft: "3px solid var(--accent-primary)", background: "linear-gradient(135deg, rgba(99, 102, 241, 0.03), rgba(168, 85, 247, 0.03))" }}>
              <div className="explanation-content">
                <span className="ai-loading-pulse">🤖 O Gemini está analisando a questão... Aguarde alguns instantes.</span>
              </div>
            </div>
          )}

          {aiExplanation && (
            <div className="explanation-box" style={{ display: "flex", borderLeft: "3px solid var(--accent-primary)", background: "linear-gradient(135deg, rgba(99, 102, 241, 0.03), rgba(168, 85, 247, 0.03))" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%", marginBottom: "0.5rem", flexWrap: "wrap", gap: "0.5rem" }}>
                <span className="explanation-title" style={{ color: "var(--accent-primary)", display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 600 }}>
                  ✨ Explicação do Gemini AI
                </span>
                <button 
                  className="btn btn-secondary btn-sm" 
                  onClick={() => triggerGeminiExplanation(true)}
                >
                  🔄 Recriar Explicação
                </button>
              </div>
              <div 
                className="explanation-content" 
                style={{ lineHeight: 1.6, whiteSpace: "normal" }}
                dangerouslySetInnerHTML={{ __html: aiExplanation }}
              />
            </div>
          )}

          {aiError && (
            <div className="explanation-box" style={{ display: "flex", borderLeft: "3px solid var(--danger)", backgroundColor: "rgba(239, 68, 68, 0.02)" }}>
              <div className="explanation-content" style={{ color: "var(--danger)" }}>
                ❌ {aiError}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel: Session Tracker */}
        <div className="progress-panel">
          <div className="progress-panel-card">
            <h3 className="progress-header-title">Status da Sessão</h3>
            <div className="mini-stats-grid">
              <div className="mini-stat-card">
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Resolvidas</span>
                <span className="mini-stat-num">{sessionSolved}/{questions.length}</span>
              </div>
              <div className="mini-stat-card">
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Acertos</span>
                <span className="mini-stat-num color-correct">{sessionCorrect}</span>
              </div>
            </div>
            <div className="mini-stats-grid">
              <div className="mini-stat-card">
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Erros</span>
                <span className="mini-stat-num color-incorrect">{sessionIncorrect}</span>
              </div>
              <div className="mini-stat-card">
                <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Meta Diária</span>
                <span className="mini-stat-num" style={{ color: "var(--warning)" }}>20</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
