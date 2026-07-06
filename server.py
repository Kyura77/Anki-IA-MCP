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

def map_fields(model_name: str, front_val: str, back_val: str) -> dict:
    """Mapeia dinamicamente a frente e verso para os campos correspondentes do modelo do Anki local."""
    try:
        fields = invoke_anki("modelFieldNames", modelName=model_name)
        if len(fields) >= 2:
            return {
                fields[0]: front_val,
                fields[1]: back_val
            }
    except Exception:
        pass
    # Fallback padrão caso dê erro ou o modelo seja desconhecido
    return {
        "Front": front_val,
        "Back": back_val
    }

@mcp.tool()
def get_capabilities() -> dict:
    """Retorna as capacidades integradas deste MCP, com instruções detalhadas sobre fluxos de trabalho (ex: criação de cards com imagem)."""
    return {
        "server_name": "Anki Sandbox Bridge",
        "description": "Sandbox segura de integração direta com o Anki local. Não possuo acesso a arquivos locais do computador por segurança.",
        "capabilities": [
            "Listar baralhos (list_decks)",
            "Criar novos baralhos (create_deck)",
            "Listar tipos de modelos de nota (list_models)",
            "Listar campos de um modelo específico (list_model_fields)",
            "Adicionar cards básicos com mapeamento de campos automático (add_card)",
            "Adicionar múltiplos cards em lote (add_multiple_cards)",
            "Buscar e ler cards (search_cards)",
            "Editar perguntas/respostas de cards existentes (edit_card)",
            "Deletar cards (delete_card)",
            "Salvar arquivos de mídia isolados no Anki (store_media_file)",
            "Criar cards com imagens anexadas em uma só chamada (add_card_with_media)",
            "Forçar sincronização com o AnkiWeb (sync_anki)",
            "Diagnóstico de conexão local (ping_anki)"
        ],
        "image_workflow_instructions": (
            "Para imagens que você gerar com DALL-E no ChatGPT: "
            "1. Sempre que você gerar uma imagem no chat, ela ficará acessível no seu ambiente (ex: /mnt/data) ou através de uma URL. "
            "2. Para criar o card de forma atômica e confiável, chame a ferramenta 'add_card_with_media'. "
            "3. Forneça o deck_name, front, back, o nome do arquivo de imagem desejado (ex: 'celula.png') e envie os dados em base64 da imagem gerada (ou a URL) no parâmetro correspondente. "
            "4. A ferramenta fará o upload para a pasta de mídias do Anki local e inserirá a tag HTML <img src='...'> na posição correta automaticamente."
        )
    }

@mcp.tool()
def ping_anki() -> str:
    """Verifica se a conexão com o Anki local está ativa e respondendo."""
    try:
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
def list_model_fields(model_name: str) -> list[str]:
    """Lista todos os nomes de campos de um modelo de nota específico (ex: ['Frente', 'Verso'] ou ['Front', 'Back'])."""
    try:
        return invoke_anki("modelFieldNames", modelName=model_name)
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
    """Salva um arquivo de mídia (imagem, áudio, etc.) diretamente na pasta de mídias do Anki a partir de uma URL ou dados em base64."""
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
def add_card_with_media(
    deck_name: str, 
    front: str, 
    back: str, 
    media_filename: str, 
    media_url: str = None, 
    media_base64: str = None, 
    media_position: str = "back",
    model_name: str = "Basic",
    tags: list[str] = None,
    custom_fields: dict = None
) -> str:
    """Adiciona um card contendo uma imagem/mídia. Faz o upload da imagem e insere a tag HTML <img src="..."> no local correto automaticamente.
    
    Parâmetros:
    - deck_name: Nome do baralho.
    - front: Texto da frente do card.
    - back: Texto do verso do card.
    - media_filename: Nome do arquivo para salvar no Anki (ex: 'mitose.png').
    - media_url: URL da imagem na web (opcional).
    - media_base64: Dados da imagem codificados em base64 (opcional).
    - media_position: Onde colocar a imagem ('front' para frente, 'back' para verso, padrão é 'back').
    - model_name: Modelo de nota (padrão 'Basic').
    - tags: Lista de tags (opcional).
    - custom_fields: Dicionário personalizado de campos (opcional, ignora o mapeamento automático).
    """
    if tags is None:
        tags = []
        
    # 1. Salvar arquivo de mídia no Anki
    params = {"filename": media_filename}
    if media_url:
        params["url"] = media_url
    if media_base64:
        params["data"] = media_base64
        
    try:
        saved_filename = invoke_anki("storeMediaFile", **params)
    except Exception as e:
        return f"Erro ao fazer upload da mídia para o Anki: {str(e)}"
        
    # 2. Inserir a imagem no campo apropriado
    img_tag = f'<br><br><img src="{saved_filename}">'
    
    if media_position.lower() == "front":
        front += img_tag
    else:
        back += img_tag
        
    # 3. Mapear campos
    if custom_fields:
        fields = custom_fields
    else:
        fields = map_fields(model_name, front, back)
        
    # 4. Adicionar o card ao Anki
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "tags": tags
    }
    
    try:
        note_id = invoke_anki("addNote", note=note)
        return f"Card de mídia criado com sucesso! Imagem '{saved_filename}' anexada ao {media_position}. ID do Card: {note_id}"
    except Exception as e:
        return f"Erro ao criar o card com mídia no Anki: {str(e)}"

@mcp.tool()
def add_card(deck_name: str, front: str, back: str, model_name: str = "Basic", tags: list[str] = None, custom_fields: dict = None) -> str:
    """Cria e adiciona um novo card de perguntas e respostas a um baralho específico."""
    if tags is None:
        tags = []
    
    if custom_fields:
        fields = custom_fields
    else:
        fields = map_fields(model_name, front, back)
        
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "tags": tags
    }
    try:
        note_id = invoke_anki("addNote", note=note)
        return f"Card adicionado com sucesso ao baralho '{deck_name}' usando o modelo '{model_name}'. ID do Card: {note_id}"
    except Exception as e:
        return f"Erro ao adicionar card: {str(e)}."

@mcp.tool()
def add_multiple_cards(deck_name: str, cards: list[dict], default_model_name: str = "Basic") -> str:
    """Adiciona múltiplos cards ao mesmo tempo. 
    Cada item na lista de 'cards' deve ser um dicionário/objeto com as chaves 'front', 'back' e opcionalmente 'tags', 'model_name' ou 'custom_fields'."""
    notes = []
    for card in cards:
        model = card.get("model_name", default_model_name)
        
        if "custom_fields" in card:
            fields = card["custom_fields"]
        else:
            fields = map_fields(model, card.get("front", ""), card.get("back", ""))
            
        notes.append({
            "deckName": deck_name,
            "modelName": model,
            "fields": fields,
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
        return f"Card ID {note_id} updated successfully."
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
