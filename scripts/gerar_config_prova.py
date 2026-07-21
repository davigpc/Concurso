import os
import json

PROVAS_DIR = r"c:\Users\davig\Downloads\Concurso\provas"

EXAM_METADATA = {
    "031_BDMG_002_01.json": {
        "nome_prova": "BDMG 2024 - Analista de TI: Desenvolvimento de Sistemas",
        "banca": "CEBRASPE",
        "ano": 2024,
        "total_questoes": 72
    },
    "031_BDMG_CG1_01.json": {
        "nome_prova": "BDMG 2024 - Conhecimentos Gerais (Todos os Cargos)",
        "banca": "CEBRASPE",
        "ano": 2024,
        "total_questoes": 48
    },
    "D794D51B24F49D57884C4BACA10D545C9D56B8CBBB3ACBE82A0CA2B6B3DBE3E3.json": {
        "nome_prova": "TCE-RN 2025 - Auditor de Controle Externo: Engenharia de Dados",
        "banca": "CEBRASPE",
        "ano": 2025,
        "total_questoes": 72
    },
    "F76B359685CEB1E2FC5733837BC9E9D34C248F466B0C323B3C2D765582283A44.json": {
        "nome_prova": "TCE-RN 2025 - Auditor de Controle Externo: Segurança da Informação",
        "banca": "CEBRASPE",
        "ano": 2025,
        "total_questoes": 70
    },
    "analista_especializacao_tecnologia.json": {
        "nome_prova": "SERPRO 2023 - Analista de TI: Especialização Tecnologia",
        "banca": "CEBRASPE",
        "ano": 2023,
        "total_questoes": 120
    },
    "analista_tecnologia_da_informacao.json": {
        "nome_prova": "Banco Central (BCB) 2024 - Analista: Tecnologia da Informação",
        "banca": "CEBRASPE",
        "ano": 2024,
        "total_questoes": 120
    },
    "ati-arquitetura-engenharia-e-sustentacao-tecnologica-cns002-tipo-01.json": {
        "nome_prova": "DATAPREV 2024 - Analista de TI: Arquitetura, Engenharia e Sustentação",
        "banca": "FGV",
        "ano": 2024,
        "total_questoes": 70
    },
    "ati-desenvolvimento-de-software-cns003-tipo-01.json": {
        "nome_prova": "DATAPREV 2024 - Analista de TI: Desenvolvimento de Software",
        "banca": "FGV",
        "ano": 2024,
        "total_questoes": 70
    },
    "auditor-de-controle-externo-ace-tecnologia-da-informacaotecnologiadainformacao-tipo-1.json": {
        "nome_prova": "TCE-ES 2023 - Auditor de Controle Externo: Tecnologia da Informação",
        "banca": "FGV",
        "ano": 2023,
        "total_questoes": 80
    },
    "escriturario_agente_de_tecnologia.json": {
        "nome_prova": "Banco do Brasil 2023 - Escriturário: Agente de Tecnologia",
        "banca": "CESGRANRIO",
        "ano": 2023,
        "total_questoes": 70
    },
    "manha-analista-cvm-perfil-8-ti-sistemas-e-desenvolvimentoperfil-8-tipo-1.json": {
        "nome_prova": "CVM 2024 - Analista: Perfil 8 - Sistemas e Desenvolvimento (Manhã)",
        "banca": "FGV",
        "ano": 2024,
        "total_questoes": 40
    },
    "manha-analista-cvm-perfil-9-ti-infraestrutura-e-segurancaperfil-9-tipo-1.json": {
        "nome_prova": "CVM 2024 - Analista: Perfil 9 - Infraestrutura e Segurança (Manhã)",
        "banca": "FGV",
        "ano": 2024,
        "total_questoes": 40
    },
    "tarde-analista-cvm-perfil-8-ti-sistemas-e-desenvolvimentoperfil-8-tipo-1.json": {
        "nome_prova": "CVM 2024 - Analista: Perfil 8 - Sistemas e Desenvolvimento (Tarde)",
        "banca": "FGV",
        "ano": 2024,
        "total_questoes": 60
    },
    "tarde-analista-cvm-perfil-9-ti-infraestrutura-e-segurancaperfil-9-tipo-1.json": {
        "nome_prova": "CVM 2024 - Analista: Perfil 9 - Infraestrutura e Segurança (Tarde)",
        "banca": "FGV",
        "ano": 2024,
        "total_questoes": 60
    },
    "Prova Agente da Fiscalização - TI Tipo 1.json": {
        "nome_prova": "TCESP 2023 - Agente da Fiscalização: Tecnologia da Informação",
        "banca": "FGV",
        "ano": 2023,
        "total_questoes": 80
    }
}

def fix_all_exam_json_configs():
    for fname, meta in EXAM_METADATA.items():
        json_path = os.path.join(PROVAS_DIR, fname)
        if not os.path.exists(json_path):
            for f in os.listdir(PROVAS_DIR):
                if f.lower().startswith(fname[:15].lower()):
                    json_path = os.path.join(PROVAS_DIR, f)
                    break

        cfg = {}
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as jf:
                try:
                    cfg = json.load(jf)
                except Exception:
                    cfg = {}

        cfg["nome_prova"] = meta["nome_prova"]
        cfg["banca"] = meta["banca"]
        cfg["ano"] = meta["ano"]
        cfg["total_questoes"] = meta["total_questoes"]

        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(cfg, jf, ensure_ascii=False, indent=2)
            print(f"Updated {os.path.basename(json_path)} -> {meta['nome_prova']} ({meta['total_questoes']} q)")

if __name__ == "__main__":
    fix_all_exam_json_configs()
