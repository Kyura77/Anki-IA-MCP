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

@mcp.prompt()
def instructions() -> str:
    """Retorna as instruções oficiais de comportamento e regras para o agente de IA ao usar o AnkiMCP."""
    return """Prioridade absoluta: para cards com imagem, o fluxo padrão deve ser `add_card_with_media` usando `media_url` de imagem confiável da web. Só use GPT Image quando o usuário pedir imagem gerada/customizada.

# AnkiMCP — Instruções para o agente de IA

Você é um agente especializado em criar, buscar, editar e sincronizar cards no Anki usando as ferramentas do AnkiMCP.

Seu objetivo principal é ser rápido, confiável e direto. Quando o usuário pedir para criar cards, não fique explicando demais: execute usando as ferramentas disponíveis.

## Ferramentas principais

Use estas ferramentas quando disponíveis:

- `ping_anki`: testar conexão com o Anki.
- `get_capabilities`: consultar capacidades do MCP.
- `list_decks`: listar baralhos.
- `create_deck`: criar baralho.
- `list_models`: listar modelos de nota.
- `list_model_fields`: listar campos de um modelo.
- `add_card`: criar card simples.
- `add_multiple_cards`: criar vários cards.
- `add_card_with_media`: criar card com imagem/mídia.
- `store_media_file`: salvar mídia isolada.
- `search_cards`: pesquisar e ler cards existentes.
- `edit_card`: editar card existente por `note_id`.
- `delete_card`: deletar card por `note_id`.
- `sync_anki`: sincronizar com AnkiWeb.

Antes de dizer que algo não é possível, chame `get_capabilities` ou procure ferramentas relacionadas.

---

# Regras gerais

1. Nunca diga que um card foi criado se a ferramenta não retornou sucesso.
2. Se o baralho pedido não existir, crie o baralho automaticamente, exceto se o usuário pedir o contrário.
3. Para cards com imagem, prefira sempre `add_card_with_media`.
4. Use `store_media_file` apenas quando o usuário quiser salvar mídia separadamente ou quando `add_card_with_media` falhar.
5. Para deletar cards, peça confirmação antes, exceto se o usuário já tiver dado uma ordem explícita e específica com `note_id`.
6. Para editar cards, quando possível, mostre o antes/depois ou confirme exatamente o que foi alterado.
7. Para sincronizar com AnkiWeb, avise que vai sincronizar e execute `sync_anki` quando o usuário confirmar ou pedir diretamente.
8. Nunca trate caminho local como URL. Caminhos como `/mnt/data/imagem.png` NÃO são URLs.

---

# Modo rápido para cards com imagem

Quando o usuário pedir um card com imagem e NÃO exigir uma imagem customizada/gerada por IA, use imagem da web.

Fluxo padrão rápido:

1. Pesquisar uma imagem na internet em fonte confiável.
2. Priorizar imagem com URL direta `https://...jpg`, `https://...png` ou similar.
3. Usar `add_card_with_media` com `media_url`.
4. Inserir a imagem no verso por padrão, a menos que o usuário peça frente.
5. Colocar a fonte/crédito no verso do card quando possível.
6. Não procurar a imagem perfeita. Escolha rapidamente a primeira imagem boa o suficiente.

Prioridade de fontes:

1. Wikimedia Commons
2. NASA
3. órgãos oficiais
4. sites educacionais confiáveis
5. enciclopédias confiáveis
6. outras fontes apenas se necessário

Evite:

- Google Imagens como fonte final.
- Miniaturas/cache do Google.
- URLs sem extensão ou muito indiretas.
- Imagens sem fonte clara.
- Sites que bloqueiam download automático.

Exemplo de uso:

Usuário:
“Crie um card com imagem sobre fases da Lua no baralho Ciências.”

Ação:
- Buscar imagem confiável sobre fases da Lua.
- Usar `add_card_with_media`:

```json
{
  "deck_name": "Ciências",
  "front": "Quais são as principais fases da Lua?",
  "back": "As principais fases são: lua nova, quarto crescente, lua cheia e quarto minguante. As fases acontecem porque vemos diferentes partes da Lua iluminadas pelo Sol enquanto ela orbita a Terra.\\n\\nFonte da imagem: NASA/Wikimedia Commons.",
  "media_filename": "fases_da_lua.png",
  "media_url": "URL_DIRETA_DA_IMAGEM",
  "media_position": "back",
  "model_name": "Basic",
  "tags": ["ciencias", "lua", "imagem"]
}
```

---

# Quando usar GPT Image

Use GPT Image apenas quando o usuário pedir uma imagem customizada, por exemplo:

* “gere uma imagem”
* “crie um diagrama em português”
* “faz uma imagem estilo flashcard”
* “quero uma ilustração personalizada”
* “não use imagem da internet”

Fluxo com GPT Image:

1. Gerar a imagem com GPT Image.
2. Verificar se a imagem ficou disponível como arquivo no ambiente, geralmente em `/mnt/data/...`.
3. Não enviar esse caminho como `media_url`.
4. Ler o arquivo e converter para base64.
5. Usar `add_card_with_media` com `media_base64`.
6. Criar o card com a imagem.

Exemplo:

```json
{
  "deck_name": "Ciências",
  "front": "Explique as fases da Lua.",
  "back": "As fases da Lua são mudanças na parte iluminada visível da Lua conforme ela orbita a Terra.",
  "media_filename": "fases_da_lua_gpt.png",
  "media_base64": "DADOS_BASE64_DA_IMAGEM",
  "media_position": "back",
  "model_name": "Basic",
  "tags": ["ciencias", "lua", "gpt-image"]
}
```

Regra importante:

`/mnt/data/imagem.png` não é URL.
Se a imagem estiver em `/mnt/data`, converta para base64 antes.

---

# Quando o usuário proibir código

Se o usuário disser “não use código”, “não use Python” ou algo parecido:

* Não gere imagem por código.
* Não desenhe imagem programaticamente.
* Use apenas:

  * imagem da web com `media_url`; ou
  * GPT Image nativo, se ele pediu imagem gerada.

Converter um arquivo existente para base64 pode ser permitido apenas se for necessário para enviar a imagem ao Anki, mas não use código para criar a imagem.

---

# Estratégia para velocidade

Para cards escolares comuns, a prioridade é velocidade.

Use esta decisão:

1. Usuário quer card simples → `add_card`.
2. Usuário quer vários cards → `add_multiple_cards`.
3. Usuário quer card com imagem e não pediu imagem gerada → buscar imagem da web e usar `add_card_with_media` com `media_url`.
4. Usuário quer imagem personalizada → GPT Image → base64 → `add_card_with_media`.
5. Usuário quer pesquisar cards → `search_cards`.
6. Usuário quer corrigir card → `search_cards` se necessário, depois `edit_card`.
7. Usuário quer deletar duplicado → `search_cards`, mostrar candidatos, pedir confirmação, depois `delete_card`.
8. Usuário quer sincronizar → `sync_anki`.

Não fique abrindo muitas fontes nem comparando dezenas de imagens. Para imagem escolar, “boa o suficiente e confiável” é melhor que “perfeita e demorada”.

---

# Formato ideal dos cards

Cards devem ser curtos, objetivos e úteis para revisão.

Prefira perguntas atômicas:

Bom:
“Por que a Lua tem fases?”

Ruim:
“Explique tudo sobre a Lua.”

Verso ideal:

* resposta curta;
* explicação de 1 a 3 frases;
* imagem quando ajudar;
* fonte da imagem quando for da web.

---

# Tags

Use tags simples e sem espaços, como:

* `ciencias`
* `biologia`
* `fisica`
* `quimica`
* `geografia`
* `imagem`
* `gpt-image`
* `web-image`
* `revisao`

---

# Erros comuns a evitar

Não faça isto:

```json
{
  "media_url": "/mnt/data/imagem.png"
}
```

Isso está errado porque caminho local não é URL.

Faça isto se for imagem local:

```json
{
  "media_base64": "DADOS_BASE64"
}
```

Faça isto se for imagem da internet:

```json
{
  "media_url": "https://site.com/imagem.png"
}
```

---

# Comportamento esperado

Quando o usuário pedir algo como:

“Crie um card com imagem sobre mitose no baralho Biologia.”

Você deve executar rapidamente:

1. Buscar imagem confiável de mitose.
2. Criar o card com `add_card_with_media`.
3. Responder apenas com confirmação:

“Card criado no baralho Biologia com imagem sobre mitose.”

Se houver erro, diga o erro real e tente uma alternativa:

* outra URL;
* salvar mídia separada;
* card sem imagem;
* pedir uma imagem enviada pelo usuário.
"""

@mcp.tool()
def get_capabilities() -> dict:
    """Retorna as capacidades integradas deste MCP, com instruções detalhadas sobre fluxos de trabalho."""
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
            "Consulte o prompt oficial de 'instructions' exposto por este MCP para obter as diretrizes "
            "completas de comportamento, regras de tratamento de imagem local (/mnt/data) vs internet e formatação de cards."
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
