import json
import urllib.request
import urllib.error
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor FastMCP
mcp = FastMCP("Anki Sandbox Bridge")

# Configura o host, porta e desativa a proteção de DNS rebinding para permitir o túnel do ngrok
mcp.settings.host = "0.0.0.0"
mcp.settings.port = 8000
mcp.settings.transport_security = None

ANKI_CONNECT_URL = "http://localhost:8765"

def invoke_anki(action: str, **params):
    """Auxiliar para fazer chamadas HTTP ao AnkiConnect local."""
    payload = {
        "action": action,
        "params": params,
        "version": 6
    }
    req_json = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ANKI_CONNECT_URL, 
        data=req_json, 
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            if res.get("error") is not None:
                raise Exception(res["error"])
            return res.get("result")
    except urllib.error.URLError as e:
        raise Exception(
            "Não foi possível conectar ao Anki. "
            "Certifique-se de que o Anki está aberto e com o add-on AnkiConnect instalado e ativo."
        ) from e

@mcp.tool()
def ping_anki() -> str:
    """Verifica se a conexão com o Anki local está ativa e respondendo."""
    try:
        # Ação simples apenas para testar a comunicação
        invoke_anki("deckNames")
        return "Conexão com o Anki está ativa e funcionando perfeitamente!"
    except Exception as e:
        return f"Erro de conexão com o Anki: {str(e)}"

@mcp.tool()
def list_decks() -> list[str]:
    """Lista todos os baralhos (decks) existentes no Anki."""
    try:
        return invoke_anki("deckNames")
    except Exception as e:
        return [f"Erro: {str(e)}"]

@mcp.tool()
def list_models() -> list[str]:
    """Lista todos os modelos de nota (tipos de card) instalados no seu Anki (ex: 'Basic', 'Básico', 'Cloze', etc.)."""
    try:
        return invoke_anki("modelNames")
    except Exception as e:
        return [f"Erro: {str(e)}"]

@mcp.tool()
def create_deck(deck_name: str) -> str:
    """Cria um novo baralho (deck) no Anki com o nome fornecido."""
    try:
        invoke_anki("createDeck", deck=deck_name)
        return f"Baralho '{deck_name}' criado com sucesso."
    except Exception as e:
        return f"Erro ao criar baralho: {str(e)}"

@mcp.tool()
def store_media_file(filename: str, url: str = None, base64_data: str = None) -> str:
    """Salva um arquivo de mídia (imagem, áudio, etc.) diretamente na pasta de mídias do Anki a partir de uma URL ou dados em base64. 
    Retorna o nome do arquivo salvo, que pode ser inserido no campo do card como '<img src=\"nome_do_arquivo.png\">'."""
    params = {"filename": filename}
    if url:
        params["url"] = url
    if base64_data:
        params["data"] = base64_data
        
    try:
        result = invoke_anki("storeMediaFile", **params)
        return f"Mídia '{result}' salva com sucesso no Anki. Use '<img src=\"{result}\">' no campo do card."
    except Exception as e:
        return f"Erro ao salvar arquivo de mídia: {str(e)}"

@mcp.tool()
def add_card(deck_name: str, front: str, back: str, model_name: str = "Basic", tags: list[str] = None) -> str:
    """Cria e adiciona um novo card de perguntas e respostas a um baralho específico.
    O 'model_name' define o tipo de nota do card (padrão é 'Basic'). Use list_models para descobrir os tipos disponíveis."""
    if tags is None:
        tags = []
    
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": {
            "Front": front,
            "Back": back
        },
        "tags": tags
    }
    try:
        note_id = invoke_anki("addNote", note=note)
        return f"Card adicionado com sucesso ao baralho '{deck_name}' usando o modelo '{model_name}'. ID do Card: {note_id}"
    except Exception as e:
        return f"Erro ao adicionar card: {str(e)}. (Dica: verifique se o model_name existe ou se os campos do modelo exigem nomes diferentes de 'Front' e 'Back')."

@mcp.tool()
def add_multiple_cards(deck_name: str, cards: list[dict], default_model_name: str = "Basic") -> str:
    """Adiciona múltiplos cards ao mesmo tempo. 
    Cada item na lista de 'cards' deve ser um dicionário/objeto com as chaves 'front', 'back' e opcionalmente 'tags' ou 'model_name'."""
    notes = []
    for card in cards:
        model = card.get("model_name", default_model_name)
        notes.append({
            "deckName": deck_name,
            "modelName": model,
            "fields": {
                "Front": card.get("front", ""),
                "Back": card.get("back", "")
            },
            "tags": card.get("tags", [])
        })
    try:
        results = invoke_anki("addNotes", notes=notes)
        added_count = sum(1 for r in results if r is not None)
        return f"Adicionados com sucesso {added_count} de {len(cards)} cards ao baralho '{deck_name}'."
    except Exception as e:
        return f"Erro ao adicionar múltiplos cards: {str(e)}"

@mcp.tool()
def search_cards(query: str) -> list[dict]:
    """Busca cards que atendem a um critério do Anki (ex: 'deck:Biologia' ou uma palavra-chave) 
    e retorna as informações detalhadas deles, incluindo o note_id."""
    try:
        note_ids = invoke_anki("findNotes", query=query)
        if not note_ids:
            return []
        notes_info = invoke_anki("notesInfo", notes=note_ids)
        
        cards_list = []
        for note in notes_info:
            fields = note.get("fields", {})
            cards_list.append({
                "note_id": note.get("noteId"),
                "deck": note.get("deckName"),
                "model": note.get("modelName"),
                "front": fields.get("Front", {}).get("value", ""),
                "back": fields.get("Back", {}).get("value", ""),
                "tags": note.get("tags", [])
            })
        return cards_list
    except Exception as e:
        return [{"erro": str(e)}]

@mcp.tool()
def edit_card(note_id: int, front: str = None, back: str = None) -> str:
    """Edita a Frente (front) e/ou o Verso (back) de um card existente a partir de seu note_id."""
    fields = {}
    if front is not None:
        fields["Front"] = front
    if back is not None:
        fields["Back"] = back
        
    if not fields:
        return "Nenhuma alteração fornecida para atualizar."
        
    try:
        invoke_anki("updateNoteFields", note={"id": note_id, "fields": fields})
        return f"Card ID {note_id} atualizado com sucesso."
    except Exception as e:
        return f"Erro ao atualizar o card: {str(e)}"

@mcp.tool()
def delete_card(note_id: int) -> str:
    """Deleta permanentemente um card do Anki usando o note_id."""
    try:
        invoke_anki("deleteNotes", notes=[note_id])
        return f"Card ID {note_id} deletado com sucesso."
    except Exception as e:
        return f"Erro ao deletar o card: {str(e)}"

@mcp.tool()
def sync_anki() -> str:
    """Sincroniza a coleção local do Anki com o servidor oficial AnkiWeb."""
    try:
        invoke_anki("sync")
        return "Sincronização com o AnkiWeb iniciada com sucesso."
    except Exception as e:
        return f"Erro ao iniciar sincronização: {str(e)}"

if __name__ == "__main__":
    # Inicia o servidor usando o protocolo SSE
    mcp.run(transport="sse")
