# Anki AI MCP Server 🤖📚

Este é um repositório completo que fornece um servidor **MCP (Model Context Protocol)** para integrar o seu **Anki Desktop** com Inteligências Artificiais modernas. Ele oferece duas formas de uso:

1. **Cliente Local (via TypeScript/Stdio):** Ideal para editores locais como **Cursor, Windsurf, Claude Desktop**, etc.
2. **Cliente Web (via Python/SSE + ngrok):** Ideal para conectar diretamente ao site do **ChatGPT (Web)** no formato Sandbox (seguro).

Com este servidor, a IA ganha "superpoderes" para ler, criar, buscar, editar e analisar seu banco de estudos diretamente pelo chat, inclusive extraindo textos e mídias de documentos PDF.

---

## 🔌 1. Pré-requisitos Gerais (Para Ambos os Métodos)

Para que qualquer uma das integrações funcione, o seu computador precisa estar configurado:

### A. Instalar o Anki Desktop 💻
O servidor MCP precisa se comunicar com o aplicativo instalado no seu computador.
* Baixe e instale o [Anki Desktop](https://apps.ankiweb.net/).
* *(Opcional)* Crie uma conta no [AnkiWeb](https://ankiweb.net/) para sincronizar seus cartões.

### B. Instalar o add-on AnkiConnect 🔌
O Anki precisa de uma extensão para conseguir conversar com o nosso servidor MCP.
1. Abra o seu **Anki Desktop**.
2. Vá no menu superior em **Ferramentas** -> **Complementos** (Add-ons).
3. Clique em **Adquirir Complementos...** (Get Add-ons).
4. Insira o código do [AnkiConnect](https://ankiweb.net/shared/info/2055492159): `2055492159` e clique em OK.
5. Reinicie o Anki para ativar a extensão.

> [!IMPORTANT]
> **O Anki Desktop deve estar sempre aberto** e rodando em segundo plano no seu computador para que a Inteligência Artificial consiga se comunicar com os seus cartões!

---

## 🛠️ Método A: Servidor Local TypeScript (Cursor, Claude Desktop, etc.)

Este método executa o servidor localmente através do terminal (`stdio`). Ele tem acesso completo de leitura/escrita e suporte ao processamento de PDFs locais.

### Requisitos:
* [Node.js](https://nodejs.org/) instalado (versão 18+).
* Dependências do script Python de PDF: `pip install pymupdf pillow`.

### Configuração:
1. Abra a pasta do projeto no terminal e rode:
   ```bash
   npm install
   npx tsc
   ```
2. Adicione o servidor nas configurações MCP do seu editor/cliente. Exemplo de configuração para o `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "anki-server": {
         "command": "node",
         "args": [
           "C:/caminho/do/projeto/build/index.js"
         ]
       }
     }
   }
   ```

---

## 🌐 Método B: Ponte Sandbox Python (ChatGPT Web)

Este método expõe um servidor HTTP/SSE local na porta `8000` e utiliza o **ngrok** para criar um túnel seguro. Ele foi desenvolvido em **modo Sandbox** (sem acesso aos seus arquivos locais), permitindo que você conecte o ChatGPT (Web) com segurança.

### Requisitos:
* Python 3.10+ instalado.
* Conta e CLI do [ngrok](https://ngrok.com/) configurada.

### Como Rodar e Conectar:
1. Inicie o servidor MCP rodando o arquivo `run.bat` ou executando no terminal:
   ```bash
   pip install -r requirements.txt
   python server.py
   ```
2. Abra um terminal e inicie o túnel do ngrok:
   ```bash
   ngrok http 8000
   ```
   *(Dica: Registre 1 domínio estático gratuito no site do ngrok e rode `ngrok http --url=seu-dominio.ngrok-free.dev 8000` para manter a URL permanente).*
3. Acesse o **ChatGPT Web**, vá em **Settings -> Apps**, ative o **Developer Mode** e clique em **Add Custom Connector**.
4. Configure a URL gerada pelo ngrok com `/sse` no final:
   * **URL:** `https://seu-dominio.ngrok-free.dev/sse`

---

## 🧰 Lista de Superpoderes Disponíveis (MCP Tools)

* **`list_decks` / `anki_get_deck_names`**: Lista todos os seus baralhos locais.
* **`create_deck` / `anki_create_deck`**: Cria um novo baralho no Anki.
* **`list_models`**: Lista os modelos de nota disponíveis no Anki (ex: `Básico`, `Basic`).
* **`list_model_fields`**: Lista os campos específicos de um modelo de nota (ex: `['Frente', 'Verso']`).
* **`add_card` / `anki_add_note`**: Cria e adiciona um card (Frente e Verso) no baralho escolhido. Mapeia automaticamente as perguntas/respostas para os campos do modelo (ex: Frente/Verso ou Front/Back).
* **`add_multiple_cards`**: Adiciona múltiplos cards ao mesmo tempo de forma otimizada.
* **`search_cards` / `anki_find_notes`**: Busca e lista cards existentes com base em termos de busca (ex: `"deck:Biologia DNA"`).
* **`edit_card` / `anki_update_note_fields`**: Atualiza a pergunta ou resposta de um card existente usando seu ID.
* **`delete_card` / `anki_delete_decks`**: Remove cards ou baralhos.
* **`sync_anki`**: Força a sincronização dos seus cartões locais com o AnkiWeb.
* **`store_media_file` / `anki_store_media_file`**: Salva imagens ou mídias diretamente no Anki (útil para cards com imagens criadas pelo ChatGPT).
* **`add_card_with_media`**: Cria o card e faz o upload da imagem de forma atômica em um único comando. Resolve automaticamente o mapeamento de campos (Frente/Verso ou Front/Back).
* **`get_capabilities`**: Retorna a lista completa de ferramentas e instruções recomendadas para o assistente de IA.
* **`anki_parse_pdf`**: (*Apenas no Método A*) Lê PDFs locais, extrai textos/mídias e anexa automaticamente as imagens extraídas na pasta de mídia do seu Anki.

---

## 💡 Exemplos de Prompts
* *"Crie 5 cards de inglês no meu baralho de Vocabulário sobre palavras corporativas avançadas."*
* *"Procure no meu Anki por cards que mencionam 'Mitocôndria' e me traga os textos deles."*
* *"Altere a resposta do card de ID 1685890000000 para '42'."*
* *"Sincronize o meu Anki."*

---

## 📄 Licença
Licença ISC. Desenvolvido para uso pessoal e integrações seguras.
