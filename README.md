# PrepConcursos

O **PrepConcursos** é uma plataforma de estudos interativa e de alta performance voltada para a resolução de questões de concursos públicos. A aplicação foi construída com **React**, **Vite** e um motor de banco de dados relacional **SQLite (`concurso.db`)** servido via **API Express REST (`server.js`)**.

A extração das questões a partir de arquivos PDF é realizada via **visão computacional / análise geométrica de layout** (`scripts/cv_extract_questions.py`), garantindo alta integridade nos enunciados, suporte a provas de 2 colunas (Cebraspe / Cesgranrio), figuras/tabelas e alternativas.

---

## 📁 Estrutura do Projeto

### Frontend (React + Vite)
*   [index.html](file:///c:/Users/davig/Downloads/Concurso/index.html): Ponto de entrada do navegador.
*   [package.json](file:///c:/Users/davig/Downloads/Concurso/package.json): Dependências do projeto (React, Vite, Express, better-sqlite3).
*   [vite.config.js](file:///c:/Users/davig/Downloads/Concurso/vite.config.js): Configurações de compilação do Vite.
*   [src/main.jsx](file:///c:/Users/davig/Downloads/Concurso/src/main.jsx): Inicialização do React DOM.
*   [src/App.jsx](file:///c:/Users/davig/Downloads/Concurso/src/App.jsx): Componente principal que gerencia navegação, estado global e alternância de temas.
*   [src/services/api.js](file:///c:/Users/davig/Downloads/Concurso/src/services/api.js): Cliente HTTP que conecta o frontend à API REST do SQLite backend.
*   [src/index.css](file:///c:/Users/davig/Downloads/Concurso/src/index.css): Estilos CSS principais com variáveis de design system.
*   [src/utils/storage.js](file:///c:/Users/davig/Downloads/Concurso/src/utils/storage.js): Utilitários para sincronização de temas e configurações no `localStorage`.

#### Componentes (`src/components/`)
*   [Dashboard.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Dashboard.jsx): Painel inicial com indicadores de progresso, total de questões e navegação por concurso.
*   [Practice.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Practice.jsx): Interface de simulado e resolução de questões (Múltipla escolha e Certo/Errado Cebraspe), com cronômetro e explicações via IA.
*   [History.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/History.jsx): Histórico detalhado de respostas diretamente da base SQLite.
*   [Stats.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Stats.jsx): Estatísticas avançadas de desempenho agrupadas por disciplina e caderno de erros.
*   [Settings.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Settings.jsx): Configurações de chave de API Gemini, backups e limpeza de dados.

### Backend & Banco de Dados (Node.js + SQLite)
*   [concurso.db](file:///c:/Users/davig/Downloads/Concurso/concurso.db): Banco de dados SQLite contendo todas as provas, questões, alternativas e histórico de respostas do usuário.
*   [server.js](file:///c:/Users/davig/Downloads/Concurso/server.js): Servidor REST Express que conecta ao `concurso.db` via `better-sqlite3`.

### Processamento & Extração por Visão Computacional (Python)
Os scripts estão na pasta [scripts/](file:///c:/Users/davig/Downloads/Concurso/scripts):
*   [init_db.py](file:///c:/Users/davig/Downloads/Concurso/scripts/init_db.py): Cria o schema e tabelas no banco `concurso.db`.
*   [cv_extract_questions.py](file:///c:/Users/davig/Downloads/Concurso/scripts/cv_extract_questions.py): Extrator geométrico por visão computacional (bounding boxes PyMuPDF), suporte a 2 colunas, desvinculação de itens Cebraspe e escrita direta no SQLite.
*   [gerar_config_prova.py](file:///c:/Users/davig/Downloads/Concurso/scripts/gerar_config_prova.py): Descobre novos PDFs na pasta `provas/` e gera seus arquivos `.json` de configuração.
*   [parse_gabarito.py](file:///c:/Users/davig/Downloads/Concurso/scripts/parse_gabarito.py): Extrai respostas oficiais de gabaritos em PDF.

---

## 🚀 Como Executar

Basta clicar duas vezes no script de inicialização:
```cmd
iniciar.bat
```
Ele iniciará automaticamente:
1. O backend API Express SQLite em `http://localhost:3001`
2. O servidor web Vite frontend em `http://localhost:5173`
