import os
import re
import json
import fitz

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROVAS_DIR = os.path.join(SCRIPT_DIR, "..", "provas")

def parse_gabarito_pdf(pdf_path):
    """Parses answer keys from a gabarito PDF for FGV, Cesgranrio, or Cebraspe."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
        
    answers = {}
    
    # 1. Cebraspe Certo/Errado pattern (e.g., 51 C 52 E or 51 Certo 52 Errado)
    cebraspe_matches = re.findall(r"\b(\d{1,3})\s*[:\-\s]\s*(Certo|Errado|C|E)\b", full_text, re.IGNORECASE)
    if len(cebraspe_matches) >= 20:
        for q_num_str, ans_str in cebraspe_matches:
            q_num = int(q_num_str)
            ans = "C" if ans_str.upper().startswith("C") else "E"
            answers[q_num] = ans
        return answers
        
    # 2. Múltipla escolha pattern (e.g., 1 - A, 2: B, 3 C)
    mc_matches = re.findall(r"\b(\d{1,3})\s*[:\-\s]\s*([A-E])\b", full_text)
    if len(mc_matches) >= 10:
        for q_num_str, ans_str in mc_matches:
            q_num = int(q_num_str)
            answers[q_num] = ans_str.upper()
        return answers
        
    # 3. Compact tabular pattern (e.g. 1 A \n 2 C \n 3 D)
    compact_matches = re.findall(r"(\d{1,3})\s*\n\s*([A-E])\b", full_text)
    if len(compact_matches) >= 10:
        for q_num_str, ans_str in compact_matches:
            q_num = int(q_num_str)
            answers[q_num] = ans_str.upper()
        return answers
        
    return answers


def sync_all_gabaritos():
    """Scans provas/ for gabarito PDFs and updates corresponding .json configs."""
    files = os.listdir(PROVAS_DIR)
    gabarito_pdfs = [f for f in files if f.endswith(".pdf") and ("gabarito" in f.lower() or "gab" in f.lower())]
    
    if not gabarito_pdfs:
        return
        
    print(f"Encontrados {len(gabarito_pdfs)} arquivo(s) de gabarito em PDF...")
    for gab_file in gabarito_pdfs:
        gab_path = os.path.join(PROVAS_DIR, gab_file)
        try:
            answers = parse_gabarito_pdf(gab_path)
            if not answers:
                continue
                
            # Find matching exam PDF base name
            # e.g., gabarito_bb_2023.pdf -> bb_2023.json or escriturario_agente_de_tecnologia.json
            clean_name = re.sub(r"gabarito[s]?[-_]?", "", gab_file, flags=re.IGNORECASE).rsplit(".", 1)[0]
            
            target_json = None
            for f in files:
                if f.endswith(".json"):
                    json_name = f.rsplit(".", 1)[0]
                    if json_name in clean_name or clean_name in json_name:
                        target_json = os.path.join(PROVAS_DIR, f)
                        break
                        
            if target_json and os.path.exists(target_json):
                with open(target_json, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                    
                # Merge parsed answers
                current_answers = data.get("answers", {})
                for k, v in answers.items():
                    current_answers[str(k)] = v
                data["answers"] = current_answers
                
                with open(target_json, "w", encoding="utf-8") as jf:
                    json.dump(data, jf, ensure_ascii=False, indent=2)
                print(f"  [+] Gabarito sincronizado com sucesso em: {os.path.basename(target_json)} ({len(answers)} respostas)")
        except Exception as e:
            print(f"Erro ao processar {gab_file}: {e}")

if __name__ == "__main__":
    sync_all_gabaritos()
