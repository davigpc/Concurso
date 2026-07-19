"""
Script para consulta de concursos de TI e busca de provas via PCI Concursos.
Endpoint MCP: https://mcp.pciconcursos.com.br/mcp
"""

import json
import re
import urllib.request

MCP_ENDPOINT = "https://mcp.pciconcursos.com.br/mcp"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def call_mcp_tool(tool_name, arguments):
    """Envia uma requisição JSON-RPC 2.0 para o servidor MCP do PCI Concursos."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(MCP_ENDPOINT, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            if "result" in res_body and "content" in res_body["result"]:
                for item in res_body["result"]["content"]:
                    if item.get("type") == "text":
                        return json.loads(item["text"])
    except Exception as e:
        print(f"Erro ao conectar com o servidor MCP: {e}")
    return None


def buscar_concursos_ti(termo="tecnologia"):
    """Busca concursos ativos na área de TI via MCP."""
    print(f"[PCI MCP] Consultando concursos ativos para: '{termo}'...\n")
    dados = call_mcp_tool("pesquisar_concursos", {"termo": termo})
    
    if not dados or "data" not in dados:
        print("Nenhum concurso encontrado ou falha na resposta.")
        return

    concursos = dados["data"]
    print(f"Encontrados {len(concursos)} concurso(s):\n")
    for idx, item in enumerate(concursos, 1):
        print(f"[{idx}] {item.get('titulo')}")
        print(f"    Vagas/Salario : {item.get('vagas_salario')}")
        print(f"    Regiao       : {item.get('regiao')}")
        datas = item.get("datas", {})
        print(f"    Inscricoes   : {datas.get('inicio')} ate {datas.get('fim')} ({datas.get('dias_restantes')} dias restantes)")
        noticia = item.get("noticia", {})
        if noticia.get("link"):
            print(f"    Link Oficial : {noticia.get('link')}")
        print("-" * 60)


def buscar_links_provas(orgao="dataprev"):
    """Localiza links de download de provas anteriores do órgão no PCI Concursos."""
    url = f"https://www.pciconcursos.com.br/provas/{orgao.lower().strip()}/"
    print(f"\n[PCI PROVAS] Buscando arquivos de provas anteriores para '{orgao}' em {url}...\n")
    
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode("utf-8", errors="ignore")
            pattern = r'href=[\x22\x27](https://www\.pciconcursos\.com\.br/provas/download/[^\x22\x27]+)[\x22\x27]'
            links = list(dict.fromkeys(re.findall(pattern, html)))
            
            if not links:
                print(f"Nenhuma prova encontrada diretamente em {url}")
                return
                
            print(f"Encontradas {len(links)} prova(s) disponíveis para download:")
            for idx, link in enumerate(links[:10], 1):
                nome_prova = link.split("/")[-1].replace("-", " ").title()
                print(f"[{idx}] {nome_prova}")
                print(f"    Link: {link}")
    except Exception as e:
        print(f"Erro ao buscar provas para {orgao}: {e}")


if __name__ == "__main__":
    buscar_concursos_ti("tecnologia")
    buscar_links_provas("serpro")
