# Anki AI MCP Server 🤖📚

Este é um servidor MCP (Model Context Protocol) desenvolvido em TypeScript/Node.js que atua como uma ponte local entre qualquer Inteligência Artificial moderna (como Claude Desktop, Cursor, Windsurf, etc.) e o seu **Anki Desktop**.

Com ele, a IA ganha "superpoderes" para ler, criar, editar e analisar o seu banco de estudos diretamente pelo chat, inclusive extraindo textos e diagramas/imagens de documentos de estudo.

---

## 🛠️ Pré-requisitos e Instalação

Para que o servidor funcione, você deve configurar o seu ambiente local seguindo estes passos:

### 1. Instalar o Anki Desktop 💻
O servidor MCP precisa se comunicar com o aplicativo instalado no seu computador.
- Baixe e instale o [Anki Desktop](https://apps.ankiweb.net/).
- *(Opcional)* Crie uma conta no [AnkiWeb](https://ankiweb.net/) para sincronizar seus cartões em nuvem com o celular ou outros dispositivos.

### 2. Instalar o add-on AnkiConnect 🔌
O Anki precisa de uma extensão para conseguir conversar com o nosso servidor MCP.
1. Abra o seu **Anki Desktop**.
2. Vá no menu superior em **Ferramentas** -> **Extensões** (ou `Ctrl+Shift+A`).
3. Clique em **Obter extensões...**.
4. Insira o código do [AnkiConnect](https://ankiweb.net/shared/info/2055492159): `2055492159` e clique em OK.
5. Reinicie o Anki para ativar a extensão.

> [!IMPORTANT]
> **O Anki Desktop deve estar sempre aberto** e rodando em segundo plano no seu computador para que a Inteligência Artificial consiga criar, ler ou atualizar os seus cartões!

### 3. Requisitos do Sistema (Node.js & Python) 🐍
O servidor utiliza Node.js e um script Python auxiliar para quebrar documentos complexos de estudo.
- Certifique-se de ter o [Node.js](https://nodejs.org/) instalado (versão 18+).
- Instale as bibliotecas Python necessárias para processar arquivos de mídia e PDFs rodando:
  ```bash
  pip install pymupdf pillow
  ```

---

## 📄 Suporte a Documentos (PDF, DOCX, etc.)

O servidor vem equipado com a ferramenta avançada `anki_parse_pdf`, que extrai de forma inteligente:
- Textos e enunciados formatados de **PDFs**.
- Imagens, tabelas e diagramas nativos do documento, salvando-os de forma automática e coordenada diretamente na pasta de mídias do seu Anki.

*Nota:* Para documentos em outros formatos (como **.docx**, **.txt**, etc.), você pode pedir para a sua IA ler o conteúdo do arquivo no próprio chat usando as ferramentas internas do editor (Cursor, Claude) e ela usará o servidor MCP para formatar e injetar os flashcards com respostas e explicações de forma limpa no seu baralho.

---

## 📦 Configuração da IA (MCP Client)

### 1. Buildar o projeto localmente:
Abra a pasta do projeto no terminal e rode:
```bash
npm install
npx tsc
```

### 2. Adicionar nas configurações do seu cliente MCP:

Insira esta configuração no arquivo JSON de configurações MCP da sua IA (como o `claude_desktop_config.json` ou nas configurações de MCP do Cursor):

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
