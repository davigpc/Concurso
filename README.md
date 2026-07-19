# PrepConcursos

O **PrepConcursos** é uma plataforma de estudos interativa e de alta performance voltada para a resolução de questões de concursos públicos. A aplicação foi migrada de uma arquitetura estática vanilla para uma aplicação web moderna baseada em **React** e **Vite**, mantendo o processamento totalmente em client-side com persistência local em cache.

A plataforma utiliza um banco de dados local estruturado contendo dados das provas, o qual é atualizado periodicamente através de scripts em Python para extração automática de textos de PDFs e gabaritos.

---

## 📁 Estrutura do Projeto

O projeto é organizado da seguinte forma:

### Frontend (React + Vite)
*   [index.html](file:///c:/Users/davig/Downloads/Concurso/index.html): Ponto de entrada do navegador que inicializa o script do React.
*   [package.json](file:///c:/Users/davig/Downloads/Concurso/package.json): Dependências do projeto (React 19, Vite, Oxlint).
*   [vite.config.js](file:///c:/Users/davig/Downloads/Concurso/vite.config.js): Configurações de compilação e plugins do Vite.
*   [src/main.jsx](file:///c:/Users/davig/Downloads/Concurso/src/main.jsx): Inicialização do React DOM.
*   [src/App.jsx](file:///c:/Users/davig/Downloads/Concurso/src/App.jsx): Componente principal que gerencia o estado global, navegação, alternância de temas (claro/escuro) e importação/exportação de backups.
*   [src/index.css](file:///c:/Users/davig/Downloads/Concurso/src/index.css): Estilos CSS principais com variáveis de design system e tokens para temas claro e escuro.
*   [src/utils/storage.js](file:///c:/Users/davig/Downloads/Concurso/src/utils/storage.js): Utilitários para sincronização do estado de progresso com o `localStorage` do navegador.

#### Componentes (`src/components/`)
*   [Dashboard.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Dashboard.jsx): Painel de boas-vindas com cartões de estatísticas gerais resumidas e a listagem de provas disponíveis para estudo.
*   [Practice.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Practice.jsx): Tela de simulação e treino. Suporta questões de múltipla escolha e de Certo/Errado (Cebraspe). Possui cronômetro por questão, sinalizador de favoritos (estrelas), correção em tempo real e integração com IA.
*   [History.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/History.jsx): Histórico detalhado de tentativas do usuário, permitindo revisar questões e respostas submetidas anteriormente.
*   [Stats.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Stats.jsx): Estatísticas aprofundadas com gráficos de acertos/erros e métricas detalhadas separadas por disciplina e tópicos.
*   [Settings.jsx](file:///c:/Users/davig/Downloads/Concurso/src/components/Settings.jsx): Painel para configurações, como cadastro da chave da API do Gemini, importação/exportação do arquivo de backup do progresso e limpeza de dados salvos.

### Banco de Dados Local
*   [questions.json](file:///c:/Users/davig/Downloads/Concurso/questions.json): Base de dados local contendo todas as provas estruturadas com enunciados, disciplinas, alternativas, gabaritos e justificativas pré-geradas.
*   [questions.js](file:///c:/Users/davig/Downloads/Concurso/questions.js): Versão em formato JS global (para retrocompatibilidade com execução via protocolo `file://`).

### Scripts & Processamento de Dados (Python)
Os scripts estão localizados na pasta [scripts/](file:///c:/Users/davig/Downloads/Concurso/scripts):
*   [extract_questions.py](file:///c:/Users/davig/Downloads/Concurso/scripts/extract_questions.py): Extrai o texto dos PDFs das provas na pasta `provas/` identificando cabeçalhos de questões e opções por meio de expressões regulares. Converte a formatação original do PDF (como negrito, itálico e sublinhado) em tags HTML seguras.
*   [patch_db.py](file:///c:/Users/davig/Downloads/Concurso/scripts/patch_db.py): Aplica o gabarito oficial às questões extraídas, cria justificativas baseadas na disciplina correspondente e salva o resultado final no formato JSON e JS.
*   [check_json.py](file:///c:/Users/davig/Downloads/Concurso/scripts/check_json.py): Ferramenta de integridade do JSON gerado, reportando se há campos vazios ou inconsistências nas questões.

### Outros Arquivos
*   [provas/](file:///c:/Users/davig/Downloads/Concurso/provas): Diretório contendo os PDFs das provas originais e seus mapeamentos parciais em formato JSON.
*   [app.js.vanilla](file:///c:/Users/davig/Downloads/Concurso/app.js.vanilla), [index.html.vanilla](file:///c:/Users/davig/Downloads/Concurso/index.html.vanilla), [style.css.vanilla](file:///c:/Users/davig/Downloads/Concurso/style.css.vanilla): Arquivos da versão anterior (Vanilla JavaScript) guardados para referência histórica e compatibilidade simples.

---

## 🤖 Integração com Gemini AI

A plataforma dispõe de uma funcionalidade de explicação avançada baseada em Inteligência Artificial utilizando o modelo **Gemini 3.5 Flash** da Google. 
Nas configurações, o usuário pode inserir sua própria chave de API. Durante as sessões de treino, se errar ou quiser aprofundar os estudos em uma questão específica, poderá requisitar a explicação gerada na hora pela IA para obter análises personalizadas sobre por que cada alternativa está correta ou incorreta.

---

## 🚀 Como Executar

### 1. Executando a Plataforma Frontend (React + Vite)

Para rodar a interface de estudos localmente em ambiente de desenvolvimento, você precisará ter o [Node.js](https://nodejs.org/) instalado.

1.  Instale as dependências do projeto:
    ```bash
    npm install
    ```
2.  Inicie o servidor de desenvolvimento local do Vite:
    ```bash
    npm run dev
    ```
3.  Abra o navegador no endereço exibido no terminal (geralmente `http://localhost:5173`).

#### Outros Comandos Disponíveis:
*   `npm run build`: Cria a versão de produção otimizada do projeto na pasta `dist/`.
*   `npm run preview`: Executa um servidor local apontando para a pasta de build de produção (`dist/`).
*   `npm run lint`: Executa a verificação estática do código (Lint) utilizando o **Oxlint** para garantir boas práticas.

---

### 2. Rodando os Scripts de Processamento (Python)

Caso queira extrair novas questões de PDFs ou atualizar o banco de dados:

#### Opção A: Usando o Script Automatizado (.bat) no Windows
Basta dar um duplo clique no arquivo [extrair_provas.bat](file:///c:/Users/davig/Downloads/Concurso/extrair_provas.bat) na raiz do projeto. Ele executará todas as etapas de extração, correção e verificação automaticamente.

#### Opção B: Execução Manual via Terminal
1.  Certifique-se de ter o Python 3 instalado em sua máquina.
2.  Instale o **PyMuPDF** (`fitz`), que é a biblioteca utilizada para a leitura avançada e mapeamento de estilos dos PDFs:
    ```bash
    pip install pymupdf
    ```
3.  Coloque os arquivos PDF correspondentes na pasta [provas/](file:///c:/Users/davig/Downloads/Concurso/provas).
4.  Execute a extração das questões:
    ```bash
    python scripts/extract_questions.py
    ```
5.  Aplique os gabaritos e construa o banco de dados atualizado:
    ```bash
    python scripts/patch_db.py
    ```
6.  Valide a qualidade dos dados gerados no JSON:
    ```bash
    python scripts/check_json.py
    ```

---

## 🛠️ Tecnologias Utilizadas

*   **Frontend:** React 19, Vite 8, CSS3 Custom Properties (CSS variables e layout flex/grid) e JSX.
*   **Análise de Código:** Oxlint (linter ultra rápido escrito em Rust).
*   **Processamento & Ingestão de Dados:** Python 3 e biblioteca PyMuPDF (fitz) para análise estilística e geométrica de documentos PDF.
*   **Integração Externa:** Google Gemini API (modelo `gemini-3.5-flash`).
