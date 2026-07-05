---
name: kyura-anki-power-tools
description: "Automatically use this when working with Anki flashcards, spaced repetition, or study materials. Triggers on: creating flashcards, generating cards from PDFs/images/notes, Anki deck management, review analytics, card quality audits, cloze deletions, study planning, bulk card generation, or any mention of Anki, flashcards, spaced repetition, SRS, or memorization. Also trigger when user uploads study material (PDFs, images of textbook pages, handwritten notes, exam questions) and wants to turn it into reviewable cards. Use proactively when user is studying and could benefit from Anki integration — even if they don't mention Anki explicitly."
---

# Anki Power Tools (Diretrizes de Alta Fidelidade)

Esta skill define as regras rígidas para gerenciar, criar e auditar flashcards de alta qualidade no Anki do usuário através do servidor MCP `anki-server`. Ela garante que qualquer agente de IA crie cartões visualmente impecáveis, estruturados pedagogicamente e com imagens extraídas nativamente sem erros.

## Pré-requisitos
- Aplicativo desktop do Anki aberto.
- Add-on **AnkiConnect** ativo (código `2055492159` rodando na porta 8765).

---

## Ferramentas MCP Disponíveis

| Ferramenta | Descrição |
|---|---|
| `anki_get_deck_names` | Lista todos os baralhos disponíveis. |
| `anki_create_deck` | Cria um novo baralho (suporta sub-baralhos com a sintaxe `Pai::Filho`). |
| `anki_delete_decks` | Exclui baralhos (com opção de manter ou apagar os cartões). |
| `anki_add_note` | Cria uma nova nota/cartão no Anki. |
| `anki_find_notes` | Pesquisa notas usando a sintaxe de busca do Anki. |
| `anki_get_notes_info` | Retorna o conteúdo e metadados completos de notas pelos IDs. |
| `anki_update_note_fields` | Atualiza os campos de um cartão existente. |
| `anki_get_reviews_of_cards` | Retorna o histórico de revisões de cartões. |
| `anki_get_collection_stats` | Retorna estatísticas gerais da coleção (em HTML). |
| `anki_store_media_file` | Salva um arquivo de mídia (imagem, áudio) no Anki do usuário. |
| `anki_parse_pdf` | Processa um PDF local, extrai textos e imagens nativas de forma coordenada. |

---

## Regra de Ouro: Tratamento de Imagens e Diagramas

> [!IMPORTANT]
> **NUNCA tire prints de tela ou faça cortes (crops) rústicos de páginas de PDF.** Isso resulta em imagens borradas, tortas ou que vazam textos das perguntas vizinhas.
>
> **Sempre use extração nativa de mídia:**
> 1. Chame a ferramenta `anki_parse_pdf` para ler o arquivo PDF. Ela extrai os objetos de imagens originais direto da árvore do PDF e os salva diretamente na pasta `collection.media` do Anki, retornando os nomes dos arquivos salvos e suas posições verticais (coordenadas `y`).
> 2. Mapeie os elementos pelo Y: Ordene os blocos de texto e as imagens extraídas pela coordenada `y`. Se uma imagem está na mesma faixa ou logo abaixo de uma questão, ela pertence obrigatoriamente a essa questão.

---

## Estrutura Visual dos Cards (Fidelidade Estética)

Todos os cartões criados pelo modelo **`Básico`** (campos `Frente` e `Verso`) devem seguir uma formatação HTML profissional e limpa:

### Campo: Frente (Front)
- **Cabeçalho em Negrito:** Indique a origem ou número da questão no topo (ex: `<b>01 - (Enem - 2024)</b>`).
- **Espaçamento Adequado:** Deixe uma quebra de linha dupla (`<br><br>`) entre o enunciado e as alternativas.
- **Imagem Centralizada:** Se houver diagrama, insira-o abaixo do enunciado usando `<br><br><img src="nome_da_imagem.png">`.
- **Alternativas Alinhadas:** Use tags `<br>` simples para separar alternativas e mantê-las legíveis.

### Campo: Verso (Back)
- **Resposta Direta no Topo:** Comece sempre destacando a resposta correta em negrito (ex: `<b>Resposta Correta: C</b>`).
- **Linha Divisória Visual:** Insira uma linha horizontal para separar a resposta da explicação usando `<hr style="border: 0; border-top: 1px solid #ccc; margin: 15px 0;">`.
- **Resolução Explicada:** Use uma seção em negrito `<b>Resolução/Explicação:</b>` seguida de um texto conciso detalhando o raciocínio físico, matemático ou conceitual.
- **Fórmulas Destacadas:** Use formatação clara para fórmulas (ex: `Fórmula: <b>F = m · a</b>`) e marcadores para as variáveis:
  ```html
  • F = força (N)<br>
  • m = massa (kg)<br>
  ```

---

## Fluxo de Trabalho 1: PDF → Flashcards

Quando o usuário fornecer um PDF de estudos/exercícios:

1. **Leitura e Extração:**
   - Chame a ferramenta `anki_parse_pdf` fornecendo o caminho absoluto do PDF.
   - Analise o retorno contendo as páginas, textos e nomes das imagens com suas respectivas coordenadas `y`.

2. **Planejamento de Baralhos:**
   - Liste os baralhos existentes usando `anki_get_deck_names`.
   - Crie um baralho temático organizado hierarquicamente usando `::` (ex: `Física::Mecânica::Leis de Newton`). Se não existir, chame `anki_create_deck`.

3. **Mapeamento de Conteúdo:**
   - Para cada página do PDF, associe as imagens aos enunciados correspondentes baseando-se na proximidade das coordenadas de altura (`y`).
   - Resolva as questões e escreva as explicações detalhadas em português (pt-BR).

4. **Batch Note Creation:**
   - Insira os cartões usando a ferramenta `anki_add_note` respeitando as diretrizes de visual e HTML detalhadas acima.
   - Utilize o modelo `"Básico"` (campos `Frente` e `Verso`).
   - Adicione tags organizacionais de assunto (ex: `fisica`, `leis-de-newton`, `ensino-medio`).

5. **Relatório de Conclusão:**
   - Mostre ao usuário o número de cards criados, o nome do baralho e um exemplo de como ficou a estrutura visual da Frente e do Verso de um dos cards criados.

---

## Diretrizes de Qualidade do Cartão (Princípios Pedagógicos)

1. **Princípio da Informação Mínima:** Cada cartão deve testar apenas um conceito atômico. Nunca misture perguntas que exijam decoreba de listas no mesmo cartão.
2. **Contexto no Enunciado:** Adicione pequenas dicas de contexto entre parênteses no início do enunciado se a pergunta puder ser ambígua (ex: `(Mecânica/Atrito) ...`).
3. **Sem Listas Longas no Verso:** Se a resposta para uma pergunta for uma lista de 4 ou mais itens, divida-a em múltiplos cartões menores (um para cada item ou etapa).
4. **Interface Limpa:** Evite usar cores berrantes. Prefira tons neutros para dar ênfase (ex: `<span style="color: #e74c3c;"><b>Atenção:</b></span>`) e use formatação limpa.

---

## Tratamento de Erros e Exceções

- **Anki Fechado:** Se as ferramentas de MCP retornarem erro de conexão (porta 8765 recusada), instrua o usuário a abrir o programa do Anki no computador.
- **Model Incompatível:** Caso o modelo padrão `"Básico"` não esteja cadastrado no Anki do usuário, consulte os modelos instalados usando baralhos de teste ou pergunte ao usuário o nome do seu modelo padrão de perguntas e respostas (como `Basic` ou `Frente/Verso`).
- **Notas Duplicadas:** Se o Anki rejeitar uma nota por duplicidade, verifique se ela já existe e ofereça atualizar os campos usando `anki_update_note_fields` ao invés de duplicar.
