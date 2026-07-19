import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "..", "questions.json")
JS_PATH = os.path.join(SCRIPT_DIR, "..", "questions.js")

TOPIC_RULES = {
    "Bancos de Dados & SQL": [
        r"\b(sql|select|insert|update|delete|join|where|group by|order by|primary key|foreign key|sgbd|postgres|mysql|oracle|nosql|mongodb|redis|transa[çc][ãa]o|acid)\b"
    ],
    "Engenharia de Software & Agilidade": [
        r"\b(scrum|kanban|agil|agile|sprint|product owner|scrum master|extreme programming|xp|tdd|bdd|uml|caso de uso|diagrama|engenharia de software|prototipagem|engenhariade software)\b"
    ],
    "Desenvolvimento & Programação": [
        r"\b(python|java|javascript|typescript|react|angular|vue|swift|kotlin|c\+\+|c#|php|node|scikit-learn|pandas|numpy|algoritmo|busca bin[áa]ria|pilha|fila|árvore|arvore)\b"
    ],
    "Arquitetura de Software & Microsserviços": [
        r"\b(microsservi[çc]os|microservices|rest|restful|api|soap|graphql|design patterns|padroes de projeto|padroniza[çc][ãa]o|mvc|clean architecture|etl|data warehouse)\b"
    ],
    "Segurança da Informação": [
        r"\b(seguran[çc]a|criptografia|hash|rsa|aes|firewall|malware|phishing|ransomware|vulnerabilidade|autentica[çc][ãa]o|autoriza[çc][ãa]o|jwt|oauth|iso 27001|lgpd)\b"
    ],
    "Redes & Infraestrutura": [
        r"\b(tcp|ip|udp|dns|dhcp|http|https|roteador|switch|vlan|nuvem|cloud|docker|kubernetes|aws|azure|devops|linux|unix|bash|shell)\b"
    ],
    "Língua Portuguesa": [
        r"\b(sint[áa]t|sujeito|predicado|crase|v[íi]rgula|reg[êe]ncia|concord[âa]ncia|pronome|sem[âa]ntica|coes[ãa]o|retextualiza[çc][ãa]o|acentua[çc][ãa]o)\b"
    ],
    "Língua Inglesa": [
        r"\b(english|text|passage|according to the text|author|word|meaning|synonym)\b"
    ],
    "Raciocínio Lógico & Matemática": [
        r"\b(probabilidade|estat[íi]stica|regress[ãa]o|matem[áa]tica|l[óo]gica|proposi[çc][ãa]o|tabela verdade|porcentagem|juros)\b"
    ]
}

def classify_question(q):
    text = (q.get("statement", "") + " " + json.dumps(q.get("options", {}))).lower()
    topics = []
    
    for category, patterns in TOPIC_RULES.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                topics.append(category)
                break
                
    if not topics:
        discipline = q.get("discipline", "")
        if discipline:
            topics.append(discipline)
        else:
            topics.append("Geral")
            
    return topics

def run_classification():
    if not os.path.exists(JSON_PATH):
        return
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    total_classified = 0
    for exam in data:
        for q in exam.get("questions", []):
            q["topics"] = classify_question(q)
            total_classified += 1
            
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write("const EXAMS_DATA = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        
    print(f"Classificados tópicos para {total_classified} questões com sucesso!")

if __name__ == "__main__":
    run_classification()
