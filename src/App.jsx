import React, { useState, useEffect } from "react";
import { loadState, saveState, initialUserState } from "./utils/storage";
import { fetchExams, fetchQuestions, saveProgress } from "./services/api";

// Screen Components
import Dashboard from "./components/Dashboard";
import Practice from "./components/Practice";
import History from "./components/History";
import Stats from "./components/Stats";
import Settings from "./components/Settings";

export default function App() {
  const [userState, setUserState] = useState(() => loadState());
  const [currentScreen, setCurrentScreen] = useState("dashboard-screen");
  const [exams, setExams] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);
  const [initialQuestionIndex, setInitialQuestionIndex] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [loadingExams, setLoadingExams] = useState(true);

  // Sync theme to root element
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", userState.theme);
  }, [userState.theme]);

  // Load exams list from Express/SQLite backend
  const refreshExams = async () => {
    try {
      setLoadingExams(true);
      const data = await fetchExams();
      setExams(data);
    } catch (err) {
      console.error("Failed to load exams from API:", err);
    } finally {
      setLoadingExams(false);
    }
  };

  useEffect(() => {
    refreshExams();
  }, []);

  const toggleTheme = () => {
    setUserState(prev => {
      const next = { ...prev, theme: prev.theme === "dark" ? "light" : "dark" };
      saveState(next);
      return next;
    });
  };

  const handleStartExam = async (examId) => {
    try {
      const examMeta = exams.find(e => e.id === examId);
      const questions = await fetchQuestions({ exam_id: examId });
      
      const fullExam = {
        exam_id: examId,
        id: examId,
        exam_name: examMeta?.name || examId,
        banca: examMeta?.banca || "FGV",
        questions: questions
      };

      setInitialQuestionIndex(0);
      setSelectedExam(fullExam);
      setCurrentScreen("practice-screen");
    } catch (err) {
      console.error("Failed to load questions for exam:", err);
    }
  };

  const handleStartRandom = async () => {
    try {
      const questions = await fetchQuestions();
      if (questions.length === 0) return;

      const randomIdx = Math.floor(Math.random() * questions.length);
      const targetQ = questions[randomIdx];

      const fullExam = {
        exam_id: targetQ.exam_id,
        id: targetQ.exam_id,
        exam_name: targetQ.exam_name,
        banca: targetQ.banca,
        questions: questions.filter(q => q.exam_id === targetQ.exam_id)
      };

      const qIdx = fullExam.questions.findIndex(q => q.id === targetQ.id);
      setInitialQuestionIndex(qIdx !== -1 ? qIdx : 0);
      setSelectedExam(fullExam);
      setCurrentScreen("practice-screen");
    } catch (err) {
      console.error("Failed to load random questions:", err);
    }
  };

  const handleSaveQuestionState = async (questionId, solvedInfo) => {
    try {
      await saveProgress({
        question_id: questionId,
        selected_option: solvedInfo.selectedOption,
        is_correct: solvedInfo.correct
      });

      setUserState(prev => {
        const next = {
          ...prev,
          solvedQuestions: {
            ...prev.solvedQuestions,
            [questionId]: {
              ...prev.solvedQuestions[questionId],
              ...solvedInfo
            }
          }
        };
        saveState(next);
        return next;
      });

      refreshExams();
    } catch (err) {
      console.error("Failed to save progress to SQLite:", err);
    }
  };

  const handleToggleStar = async (questionId) => {
    try {
      const isStarred = !userState.starredQuestions[questionId];
      await saveProgress({
        question_id: questionId,
        is_starred: isStarred
      });

      setUserState(prev => {
        const next = {
          ...prev,
          starredQuestions: {
            ...prev.starredQuestions,
            [questionId]: isStarred
          }
        };
        saveState(next);
        return next;
      });
    } catch (err) {
      console.error("Failed to toggle star:", err);
    }
  };

  const handleReviewQuestion = async (examId, questionNum) => {
    try {
      const examMeta = exams.find(e => e.id === examId);
      const questions = await fetchQuestions({ exam_id: examId });

      const fullExam = {
        exam_id: examId,
        id: examId,
        exam_name: examMeta?.name || examId,
        banca: examMeta?.banca || "FGV",
        questions: questions
      };

      const qIdx = questions.findIndex(q => q.number === questionNum);
      setInitialQuestionIndex(qIdx !== -1 ? qIdx : 0);
      setSelectedExam(fullExam);
      setCurrentScreen("practice-screen");
    } catch (err) {
      console.error("Failed to review question:", err);
    }
  };

  const handleSaveApiKey = (key) => {
    setUserState(prev => {
      const next = { ...prev, geminiApiKey: key };
      saveState(next);
      return next;
    });
  };

  const handleResetData = () => {
    setUserState(() => {
      const next = { ...initialUserState };
      saveState(next);
      return next;
    });
  };

  const handleImportBackup = (backupData) => {
    setUserState(prev => {
      const next = { ...prev, ...backupData };
      saveState(next);
      return next;
    });
  };

  const handleExportBackup = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(userState, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `prepconcursos_backup_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="app-container">
      {/* Mobile Header bar */}
      <header className="mobile-header">
        <div className="brand-section">
          <div className="brand-logo">P</div>
          <span className="brand-title">PrepConcursos</span>
        </div>
        <button 
          className="menu-toggle-btn" 
          aria-label="Abrir menu"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          ☰
        </button>
      </header>

      {/* Sidebar Navigation */}
      <aside className={`sidebar ${mobileMenuOpen ? "open" : ""}`}>
        <div className="brand-section">
          <div className="brand-logo">P</div>
          <h1 className="brand-title">PrepConcursos</h1>
        </div>
        
        <nav className="sidebar-nav">
          <ul className="nav-menu">
            <li className={`nav-item ${currentScreen === "dashboard-screen" ? "active" : ""}`}>
              <a 
                href="#dashboard-screen" 
                onClick={(e) => {
                  e.preventDefault();
                  setCurrentScreen("dashboard-screen");
                  setMobileMenuOpen(false);
                }}
              >
                <span className="nav-icon">📊</span> Painel de Controle
              </a>
            </li>
            <li className={`nav-item ${currentScreen === "practice-screen" ? "active" : ""}`}>
              <a 
                href="#practice-screen" 
                onClick={(e) => {
                  e.preventDefault();
                  handleStartRandom();
                  setMobileMenuOpen(false);
                }}
              >
                <span className="nav-icon">✏️</span> Estudar Questões
              </a>
            </li>
            <li className={`nav-item ${currentScreen === "history-screen" ? "active" : ""}`}>
              <a 
                href="#history-screen" 
                onClick={(e) => {
                  e.preventDefault();
                  setCurrentScreen("history-screen");
                  setMobileMenuOpen(false);
                }}
              >
                <span className="nav-icon">📜</span> Histórico & Revisão
              </a>
            </li>
            <li className={`nav-item ${currentScreen === "analysis-screen" ? "active" : ""}`}>
              <a 
                href="#analysis-screen" 
                onClick={(e) => {
                  e.preventDefault();
                  setCurrentScreen("analysis-screen");
                  setMobileMenuOpen(false);
                }}
              >
                <span className="nav-icon">📈</span> Análise Detalhada
              </a>
            </li>
            <li className={`nav-item ${currentScreen === "settings-screen" ? "active" : ""}`}>
              <a 
                href="#settings-screen" 
                onClick={(e) => {
                  e.preventDefault();
                  setCurrentScreen("settings-screen");
                  setMobileMenuOpen(false);
                }}
              >
                <span className="nav-icon">⚙️</span> Configurações
              </a>
            </li>
          </ul>
        </nav>
        
        <div className="sidebar-footer">
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {userState.theme === "dark" ? (
              <><span className="nav-icon">☀️</span> Modo Claro</>
            ) : (
              <><span className="nav-icon">🌙</span> Modo Escuro</>
            )}
          </button>
        </div>
      </aside>

      {/* Main Workspace Wrapper */}
      <main className="main-wrapper">
        <header className="main-header">
          <div>
            <h2 className="font-display" style={{ fontSize: "1.4rem" }}>Área de Estudos</h2>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              Bem-vindo de volta! Resolva questões com motor SQLite local.
            </p>
          </div>
          <div className="header-user">
            <div className="user-info" style={{ textAlign: "right" }}>
              <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>Estudante</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>SQLite Persistence</div>
            </div>
            <div className="user-avatar">E</div>
          </div>
        </header>

        {/* Content Area */}
        <div className="main-content">
          {currentScreen === "dashboard-screen" && (
            <Dashboard 
              exams={exams}
              userState={userState}
              onStartExam={handleStartExam}
              onStartRandom={handleStartRandom}
              onSwitchScreen={setCurrentScreen}
              loading={loadingExams}
            />
          )}

          {currentScreen === "practice-screen" && selectedExam && (
            <Practice 
              exam={selectedExam}
              userState={userState}
              onSaveQuestionState={handleSaveQuestionState}
              onToggleStar={handleToggleStar}
              onGoBack={() => setCurrentScreen("dashboard-screen")}
              initialQuestionIndex={initialQuestionIndex}
            />
          )}

          {currentScreen === "history-screen" && (
            <History 
              exams={exams}
              userState={userState}
              onReviewQuestion={handleReviewQuestion}
              onToggleStar={handleToggleStar}
            />
          )}

          {currentScreen === "analysis-screen" && (
            <Stats 
              exams={exams}
              userState={userState}
            />
          )}

          {currentScreen === "settings-screen" && (
            <Settings 
              userState={userState}
              onSaveApiKey={handleSaveApiKey}
              onResetData={handleResetData}
              onExportBackup={handleExportBackup}
              onImportBackup={handleImportBackup}
            />
          )}
        </div>
      </main>
    </div>
  );
}
