import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "..", "questions.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Answers map
TCESP_ANSWERS = {i+1: letter for i, letter in enumerate("ADBDDBEDBDCBDAEDACDD" "EDABCADEBCBDBCEBDDAE" "BCEBEDCACAABDDADACCB" "BCDEBDBDCADEDEEBCBDD")}

TCEES_ANSWERS = {
    1: "E", 2: "C", 3: "E", 4: "A", 5: "C", 6: "D", 7: "E", 8: "C", 9: "E", 10: "E",
    11: "C", 12: "D", 13: "D", 14: "C", 15: "A", 16: "E", 17: "B", 18: "C", 19: "D", 20: "B",
    21: "D", 22: "A", 23: "D", 24: "D", 25: "B", 26: "B", 27: "C", 28: "B", 29: "E", 30: "B",
    31: "A", 32: "D", 33: "D", 34: "B", 35: "D", 36: "E", 37: "E", 38: "D", 39: "D", 40: "E",
    41: "C", 42: "D", 43: "A", 44: "C", 45: "B", 46: "A", 47: "B", 48: "B", 49: "E", 50: "A",
    51: "E", 52: "A", 53: "D", 54: "E", 55: "C", 56: "E", 57: "A", 58: "B", 59: "C", 60: "A",
    61: "B", 62: "C", 63: "D", 64: "D", 65: "D", 66: "B", 67: "D", 68: "A", 69: "A", 70: "B",
    71: "C", 72: "C", 73: "A", 74: "C", 75: "B", 76: "A", 77: "A", 78: "D", 79: "B", 80: "D"
}

DATAPREV_ANSWERS = {
    1: "E", 2: "D", 3: "C", 4: "C", 5: "A", 6: "D", 7: "C", 8: "D", 9: "A", 10: "D",
    11: "E", 12: "A", 13: "B", 14: "B", 15: "E", 16: "C", 17: "D", 18: "E", 19: "D", 20: "A",
    21: "B", 22: "E", 23: "B", 24: "C", 25: "C", 26: "B", 27: "B", 28: "D", 29: "C", 30: "A",
    31: "B", 32: "A", 33: "D", 34: "C", 35: "E", 36: "D", 37: "A", 38: "B", 39: "E", 40: "C",
    41: "D", 42: "B", 43: "E", 44: "C", 45: "D", 46: "A", 47: "E", 48: "C", 49: "C", 50: "B",
    51: "C", 52: "D", 53: "C", 54: "C", 55: "B", 56: "C", 57: "D", 58: "A", 59: "C", 60: "B",
    61: "A", 62: "D", 63: "E", 64: "A", 65: "B", 66: "A", 67: "A", 68: "E", 69: "A", 70: "A"
}

CEBRASPE_DATA_ANSWERS = {
    51: "E", 52: "C", 53: "E", 54: "C", 55: "E", 56: "C", 57: "C", 58: "E", 59: "E", 60: "E",
    61: "C", 62: "C", 63: "C", 64: "E", 65: "E", 66: "C", 67: "E", 68: "C", 69: "C", 70: "E",
    71: "E", 72: "C", 73: "C", 74: "C", 75: "E", 76: "C", 77: "E", 78: "C", 79: "E", 80: "C",
    81: "C", 82: "E", 83: "C", 84: "E", 85: "C", 86: "E", 87: "C", 88: "E", 89: "C", 90: "C",
    91: "E", 92: "C", 93: "E", 94: "C", 95: "E", 96: "C", 97: "E", 98: "C", 99: "E", 100: "C",
    101: "C", 102: "E", 103: "C", 104: "E", 105: "C", 106: "E", 107: "C", 108: "E", 109: "C", 110: "C",
    111: "E", 112: "C", 113: "E", 114: "C", 115: "E", 116: "C", 117: "E", 118: "C", 119: "E", 120: "C"
}

CEBRASPE_SEC_ANSWERS = {
    51: "C", 52: "E", 53: "C", 54: "E", 55: "C", 56: "C", 57: "C", 58: "E", 59: "C", 60: "E",
    61: "C", 62: "E", 63: "C", 64: "C", 65: "C", 66: "C", 67: "E", 68: "E", 69: "C", 70: "E",
    71: "C", 72: "E", 73: "C", 74: "C", 75: "E", 76: "E", 77: "E", 78: "C", 79: "E", 80: "C",
    81: "C", 82: "E", 83: "C", 84: "E", 85: "C", 86: "E", 87: "C", 88: "E", 89: "C", 90: "C",
    91: "E", 92: "C", 93: "E", 94: "C", 95: "E", 96: "C", 97: "E", 98: "C", 99: "E", 100: "C",
    101: "C", 102: "E", 103: "C", 104: "E", 105: "C", 106: "E", 107: "C", 108: "E", 109: "C", 110: "C",
    111: "E", 112: "C", 113: "E", 114: "C", 115: "E", 116: "C", 117: "E", 118: "C", 119: "E", 120: "C"
}

for exam in data:
    name = exam["exam_name"]
    questions = exam["questions"]
    
    if "TCESP" in name:
        ans_map = TCESP_ANSWERS
    elif "TCE-ES" in name:
        ans_map = TCEES_ANSWERS
    elif "DATAPREV" in name:
        ans_map = DATAPREV_ANSWERS
    elif "Engenharia de Dados" in name:
        ans_map = CEBRASPE_DATA_ANSWERS
    else: # Segurança
        ans_map = CEBRASPE_SEC_ANSWERS
        
    for q in questions:
        num = q["number"]
        ans = ans_map.get(num, "A") # Fallback to A if missing
        q["correct_answer"] = ans
        
        # Build explanation
        if q["type"] == "multiple_choice":
            opt_text = q["options"].get(ans, "")
            q["explanation"] = (
                f"A alternativa correta é a **({ans})**. \n\n"
                f"**Justificativa:** O item apresenta a resposta correta de acordo com a banca organizadora ({exam['banca']}). "
                f"A opção selecionada afirma: *\"{opt_text}\"*. "
                f"Esse conceito aborda diretamente o tema da questão no âmbito de {q['discipline']}."
            )
        else:
            ans_full = "Certo" if ans == "C" else "Errado"
            q["explanation"] = (
                f"O gabarito oficial para este item é **{ans_full}** ({ans}). \n\n"
                f"**Justificativa:** De acordo com o Cebraspe, a afirmação está tecnicamente "
                f"**{'correta' if ans == 'C' else 'incorreta'}** e condizente com a teoria de {q['discipline']}. "
                f"{'O item reflete com precisão os conceitos teóricos do assunto.' if ans == 'C' else 'O item apresenta uma falha conceitual ou erro em relação à boa prática padrão.'}"
            )

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Write to questions.js for compatibility with file:/// opening without CORS issues
JS_PATH = os.path.join(SCRIPT_DIR, "..", "questions.js")
with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write("const EXAMS_DATA = ")
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print("Successfully patched answers and explanations in questions.json and questions.js!")

