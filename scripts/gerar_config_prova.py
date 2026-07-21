"""
Script para identificar PDFs sem configuração na pasta 'provas/' e gerar automaticamente os arquivos .json.
Ignora automaticamente provas duplicadas do mesmo concurso (Tipo 2, Tipo 3, Tipo 4).
"""

import os
import json
import fitz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROVAS_DIR = os.path.join(SCRIPT_DIR, "..", "provas")


def auto_detect_config(pdf_path):
    """Lê a primeira página do PDF para tentar identificar a banca, título e total de questões."""
    base_name = os.path.basename(pdf_path).rsplit(".", 1)[0]
    
    try:
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text("text").upper() if len(doc) > 0 else ""
    except Exception as e:
        print(f"Erro ao ler {pdf_path}: {e}")
        first_page_text = ""

    banca = "FGV"
    if "CEBRASPE" in first_page_text or "CESPE" in first_page_text:
        banca = "CEBRASPE"
    elif "CESGRANRIO" in first_page_text:
        banca = "CESGRANRIO"

    raw_name = base_name.replace("_", " ").replace("-", " ")
    clean_name = raw_name.title()

    # Normalization dictionary for common terms and acronyms
    replacements = {
        r"\bTi\b": "TI",
        r"\bBcb\b": "BCB",
        r"\bBdmg\b": "BDMG",
        r"\bCvm\b": "CVM",
        r"\bTcesp\b": "TCESP",
        r"\bTce\b": "TCE",
        r"\bRn\b": "RN",
        r"\bEs\b": "ES",
        r"\bAce\b": "ACE",
        r"\bSerpro\b": "SERPRO",
        r"\bDataprev\b": "DATAPREV",
        r"\bInformacao\b": "Informação",
        r"\bEspecializao\b": "Especialização",
        r"\bEspecializacao\b": "Especialização",
        r"\bSustentacao\b": "Sustentação",
        r"\bSeguranca\b": "Segurança",
        r"\bEspecficos\b": "Específicos",
        r"\bEspecificos\b": "Específicos",
        r"\bEscriturrio\b": "Escriturário",
        r"\bEscriturario\b": "Escriturário",
        r"\bFiscalizao\b": "Fiscalização",
        r"\bFiscalizacao\b": "Fiscalização",
        r"\bManha\b": "Manhã"
    }

    import re
    for pat, repl in replacements.items():
        clean_name = re.sub(pat, repl, clean_name, flags=re.IGNORECASE)

    total_questions = 70
    if banca == "CEBRASPE":
        total_questions = 120

    return {
        "name": clean_name,
        "banca": banca,
        "total_questions": total_questions,
        "answers": {}
    }



def sync_provas_json():
    """Gera arquivos .json para todos os PDFs em 'provas/' que ainda não possuam configuração."""
    print("[AUTOSYNC] Verificando arquivos PDF na pasta 'provas/'...\n")
    
    pdfs = [f for f in os.listdir(PROVAS_DIR) if f.endswith(".pdf")]
    created_count = 0
    
    for pdf_file in pdfs:
        # Ignorar provas que são apenas variações de ordem (Tipo 2, 3, 4)
        pdf_file_lower = pdf_file.lower()
        if any(t in pdf_file_lower for t in ["tipo-02", "tipo-03", "tipo-04", "tipo 2", "tipo 3", "tipo 4"]):
            continue

        base_name = pdf_file.rsplit(".", 1)[0]
        json_path = os.path.join(PROVAS_DIR, base_name + ".json")
        
        if not os.path.exists(json_path):
            pdf_path = os.path.join(PROVAS_DIR, pdf_file)
            config_data = auto_detect_config(pdf_path)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
                
            print(f"[NOVO CONFIG] Criado arquivo de configuracao: {base_name}.json")
            print(f"   - Titulo detectado: {config_data['name']}")
            print(f"   - Banca detectada : {config_data['banca']}")
            created_count += 1

    if created_count == 0:
        print("Nenhum novo PDF pendente de configuracao.")
    else:
        print(f"\n[SUCESSO] {created_count} novo(s) arquivo(s) .json configurado(s) com sucesso!")


if __name__ == "__main__":
    sync_provas_json()
