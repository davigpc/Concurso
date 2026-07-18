import React, { useState, useEffect } from "react";

export default function Settings({ userState, onSaveApiKey, onResetData, onImportBackup, onExportBackup }) {
  const [apiKeyInput, setApiKeyInput] = useState("");

  useEffect(() => {
    setApiKeyInput(userState.geminiApiKey || "");
  }, [userState.geminiApiKey]);

  const handleSaveKey = () => {
    onSaveApiKey(apiKeyInput.trim());
    alert("Chave de API do Gemini salva com sucesso!");
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const fileReader = new FileReader();
    fileReader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target.result);
        if (parsed.solvedQuestions && parsed.starredQuestions) {
          onImportBackup(parsed);
          alert("Backup importado com sucesso!");
        } else {
          alert("Estrutura de arquivo de backup inválida.");
        }
      } catch (err) {
        alert("Erro ao ler o arquivo de backup. Verifique se é um arquivo JSON válido.");
      }
    };
    fileReader.readAsText(file);
  };

  return (
    <section className="app-screen active">
      <h3 className="section-title">Configurações Gerais</h3>
      
      <div className="card settings-section">
        <div className="settings-group">
          <h4>Integração Inteligente (Google AI Studio)</h4>
          <p className="settings-description">
            Insira sua chave de API do Gemini para receber explicações detalhadas e personalizadas quando errar ou rever questões.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.5rem", maxWidth: "500px" }}>
            <input 
              type="password" 
              className="select-filter" 
              style={{ width: "100%", fontFamily: "monospace", padding: "0.6rem 0.75rem" }} 
              placeholder="Insira sua API Key (AQ.Ab8RN...)"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
            />
            <button className="btn btn-primary" style={{ alignSelf: "flex-start" }} onClick={handleSaveKey}>
              Salvar Chave API
            </button>
          </div>
        </div>
        
        <hr style={{ border: 0, borderTop: "1px solid var(--border-color)", margin: "1rem 0" }} />

        <div className="settings-group">
          <h4>Limpar Dados de Progresso</h4>
          <p className="settings-description">
            Se você deseja reiniciar seus estudos e limpar todo o histórico de questões respondidas, acertos, erros e marcações, utilize o botão abaixo.
          </p>
          <button 
            className="btn btn-danger" 
            style={{ alignSelf: "flex-start", marginTop: "0.5rem" }}
            onClick={() => {
              if (window.confirm("Tem certeza que deseja apagar todo o seu progresso? Esta ação não pode ser desfeita.")) {
                onResetData();
                alert("Dados limpos com sucesso!");
              }
            }}
          >
            Limpar Histórico Local
          </button>
        </div>
        
        <hr style={{ border: 0, borderTop: "1px solid var(--border-color)", margin: "1rem 0" }} />

        <div className="settings-group">
          <h4>Backup do Progresso</h4>
          <p className="settings-description">
            Exporte todas as suas respostas, questões salvas e estatísticas para um arquivo no seu computador, ou recupere seu progresso a partir de um backup existente.
          </p>
          <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
            <button className="btn btn-secondary" onClick={onExportBackup}>
              📥 Exportar Backup
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => document.getElementById("import-backup-file-react").click()}
            >
              📤 Importar Backup
            </button>
            <input 
              type="file" 
              id="import-backup-file-react" 
              accept=".json" 
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
          </div>
        </div>
        
        <hr style={{ border: 0, borderTop: "1px solid var(--border-color)", margin: "1rem 0" }} />
        
        <div className="settings-group">
          <h4>Sobre a Aplicação</h4>
          <p className="settings-description">
            Esta plataforma foi desenvolvida utilizando tecnologias web modernas para processar e disponibilizar provas de concursos locais, permitindo a prática focada e resoluções com feedbacks e justificativas completas.
          </p>
          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.5rem" }}>
            Versão 1.0.0 (Estável)
          </p>
        </div>
      </div>
    </section>
  );
}
