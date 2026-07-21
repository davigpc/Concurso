"""
Discipline mapping helper.
"""

def map_discipline(banca, exam_name, q_num, total_questions):
    """Map question number to a discipline category."""
    name_lower = exam_name.lower()
    if "banco do brasil" in name_lower or "escriturario" in name_lower or "escriturário" in name_lower:
        if q_num <= 10: return "Língua Portuguesa"
        if q_num <= 15: return "Língua Inglesa"
        if q_num <= 20: return "Matemática"
        if q_num <= 25: return "Atualidades do Mercado Financeiro"
        if q_num <= 30: return "Probabilidade e Estatística"
        if q_num <= 35: return "Conhecimentos Bancários"
        return "Tecnologia da Informação"

    if banca == "FGV":
        if total_questions == 80:
            if q_num <= 20: return "Língua Portuguesa"
            if q_num <= 40: return "Legislação / Raciocínio Lógico"
            return "Tecnologia da Informação"
        elif total_questions == 70:
            if q_num <= 12: return "Língua Portuguesa"
            if q_num <= 18: return "Língua Inglesa"
            return "Conhecimentos Específicos (TI)"
        elif total_questions == 60:
            if q_num <= 20: return "Língua Portuguesa / Legislação"
            return "Conhecimentos Específicos (TI)"

    if banca == "CEBRASPE":
        if "segurança" in name_lower: return "Segurança da Informação"
        if "engenharia de dados" in name_lower: return "Banco de Dados & Big Data"

    return "Conhecimentos Específicos"
