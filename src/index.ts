import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { addNote, findNotes, getNotesInfo, updateNoteFields } from "./tools/cards.js";
import { createDeck, getDeckNames, deleteDecks } from "./tools/decks.js";
import { getCollectionStatsHTML, getReviewsOfCards } from "./tools/stats.js";
import { storeMediaFile } from "./tools/media.js";
import { parsePdf } from "./tools/pdf.js";



const server = new McpServer({
  name: "anki-mcp-server",
  version: "1.0.0"
});

// -- Cards Tools --

server.tool("anki_add_note",
  "Create a new card (note) in Anki.",
  {
    deckName: z.string().describe("Name of the deck"),
    modelName: z.string().describe("Name of the note type (e.g. 'Basic')"),
    fields: z.any().describe("Record of field names to content"),
    tags: z.array(z.string()).optional().describe("Optional list of tags"),
  },
  async (args) => {
    try {
      const result = await addNote(args as any);
      return { content: [{ type: "text", text: result }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool("anki_find_notes",
  "Search for notes using Anki search syntax (e.g. 'deck:Default tag:AI'). Returns a list of note IDs.",
  {
    query: z.string().describe("Anki search query string"),
  },
  async (args) => {
    try {
      const result = await findNotes(args);
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool("anki_get_notes_info",
  "Get the full content and details of notes given their IDs.",
  {
    notes: z.array(z.number()).describe("List of Note IDs"),
  },
  async (args) => {
    try {
      const result = await getNotesInfo(args);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool("anki_update_note_fields",
  "Update the content of existing note fields.",
  {
    noteId: z.number().describe("The ID of the note to update"),
    fields: z.any().describe("Record of field names to new content"),
  },
  async (args) => {
    try {
      const result = await updateNoteFields(args as any);
      return { content: [{ type: "text", text: result }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

// -- Decks Tools --

server.tool("anki_get_deck_names",
  "List all available decks in Anki.",
  {},
  async () => {
    try {
      const result = await getDeckNames();
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool("anki_create_deck",
  "Create a new deck.",
  {
    deck: z.string().describe("Name of the new deck"),
  },
  async (args) => {
    try {
      const result = await createDeck(args);
      return { content: [{ type: "text", text: result }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool("anki_delete_decks",
  "Delete decks and optionally their cards.",
  {
    decks: z.array(z.string()).describe("Names of decks to delete"),
    cardsToo: z.boolean().describe("If true, delete cards as well. If false, cards are moved to Default."),
  },
  async (args) => {
    try {
      const result = await deleteDecks(args);
      return { content: [{ type: "text", text: result }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

// -- Stats Tools --

server.tool("anki_get_collection_stats",
  "Get overall Anki collection statistics (returns HTML).",
  {
    wholeCollection: z.boolean().optional().describe("Whether to get stats for the whole collection or just the current deck"),
  },
  async (args) => {
    try {
      const result = await getCollectionStatsHTML(args);
      return { content: [{ type: "text", text: result }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

server.tool("anki_get_reviews_of_cards",
  "Get review history for specific cards.",
  {
    cards: z.array(z.number()).describe("List of Card IDs (not Note IDs)"),
  },
  async (args) => {
    try {
      const result = await getReviewsOfCards(args);
      return { content: [{ type: "text", text: JSON.stringify(result) }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

// -- Media Tools --

server.tool("anki_store_media_file",
  "Upload/store a media file (image, audio, etc.) in Anki's media collection. Pass either 'data' (base64), 'path' (local file path), or 'url' (web link).",
  {
    filename: z.string().describe("Filename to save in Anki media folder (e.g. 'image.png')"),
    data: z.string().optional().describe("Optional base64 encoded file data"),
    path: z.string().optional().describe("Optional absolute local path to file"),
    url: z.string().optional().describe("Optional URL to download the file from"),
  },
  async (args) => {
    try {
      const result = await storeMediaFile(args);
      return { content: [{ type: "text", text: result }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

// -- PDF tools --

server.tool("anki_parse_pdf",
  "Parse a PDF file, extract its text and images, automatically save the images to Anki's media collection, and return a structured JSON mapping text and image positions.",
  {
    pdfPath: z.string().describe("Absolute local path to the PDF file (e.g. 'C:/Users/.../document.pdf')"),
  },
  async (args) => {
    try {
      const result = await parsePdf(args);
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true };
    }
  }
);

// Start the server


async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Anki MCP Server running on stdio");
}

main().catch(console.error);
