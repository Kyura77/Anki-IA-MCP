# Anki AI MCP Server 🤖📚

Este é um servidor MCP (Model Context Protocol) desenvolvido em TypeScript/Node.js que atua como uma ponte local entre qualquer Inteligência Artificial moderna (como Claude Desktop, Cursor, Windsurf, etc.) e o seu **Anki Desktop**.

Com ele, a IA ganha "superpoderes" para ler, criar, editar e analisar o seu banco de estudos diretamente pelo chat.

## 🚀 Funcionalidades

- **Gerenciamento de Cards (`anki_add_note`, `anki_update_note_fields`, `anki_get_notes_info`, `anki_find_notes`):** Crie, edite, busque e leia o conteúdo de seus flashcards.
- **Gerenciamento de Baralhos (`anki_create_deck`, `anki_get_deck_names`, `anki_delete_decks`):** Crie novos baralhos (suportando a hierarquia `Pai::Filho`) e organize sua estrutura de estudos.
- **Estatísticas de Estudo (`anki_get_collection_stats`, `anki_get_reviews_of_cards`):** Permite que a IA analise o seu rendimento diário, histórico de revisões e dê dicas de estudo.
- **Upload de Mídias (`anki_store_media_file`):** Salve imagens e áudios diretamente na pasta de mídias (`collection.media`) do seu perfil no Anki.
- **Leitura Avançada de PDFs (`anki_parse_pdf`):** Extrai textos e imagens nativas de PDFs locais coordenando suas posições, permitindo que a IA monte cards perfeitos com diagramas associados sem vazar textos.

---

## 🛠️ Pré-requisitos

1. **Anki Desktop** aberto em seu computador.
2. O add-on **AnkiConnect** instalado no Anki (código: `2055492159`).
3. **Node.js** instalado (versão 18 ou superior).
4. **Python** instalado com a biblioteca `pymupdf` (usada pelo parser de PDF do servidor):
   ```bash
   pip install pymupdf pillow
   ```

---

## 📦 Instalação e Configuração

### 1. Buildar o projeto localmente:
Baixe as dependências e compile o código TypeScript:
```bash
npm install
npx tsc
```

### 2. Configurar a sua IA (MCP Client):

Adicione a configuração do servidor ao arquivo de configurações MCP da sua IA (como o `claude_desktop_config.json` ou as configurações de MCP do Cursor):

```json
{
  "mcpServers": {
    "anki-server": {
      "command": "node",
      "args": [
        "C:/Users/cd250/.gemini/antigravity/scratch/anki-mcp-server/build/index.js"
      ]
    }
  }
}
```
*(Certifique-se de ajustar o caminho absoluto da pasta `build/index.js` para o local exato onde o projeto está no seu computador).*

---

## 💡 Como Usar (Prompt Natural)

Uma vez ativo, você pode pedir naturalmente para a sua IA realizar ações no Anki. Exemplos:

- *"Crie um novo baralho chamado 'Física::Leis de Newton'."*
- *"Leia o PDF em 'C:/caminho/lista.pdf', resolva os exercícios e gere os flashcards contendo as imagens no meu baralho de Física."*
- *"Busque todas as notas no meu baralho de Biologia que contêm a palavra 'Mitose'."*
- *"Analise o meu rendimento de estudos e veja quais cartões estão me dando mais trabalho."*

---

## 📄 Licença
Licença ISC. Desenvolvido para uso pessoal e integrações locais seguras.
