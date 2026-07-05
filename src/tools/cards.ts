import { invokeAnki } from '../anki.js';

export async function addNote(args: { deckName: string; modelName: string; fields: Record<string, string>; tags?: string[] }) {
  const result = await invokeAnki('addNote', {
    note: {
      deckName: args.deckName,
      modelName: args.modelName,
      fields: args.fields,
      tags: args.tags || [],
      options: {
        allowDuplicate: false,
      }
    }
  });
  return `Note added successfully with ID: ${result}`;
}

export async function findNotes(args: { query: string }) {
  const noteIds = await invokeAnki<number[]>('findNotes', { query: args.query });
  return noteIds;
}

export async function getNotesInfo(args: { notes: number[] }) {
  const notesInfo = await invokeAnki('notesInfo', { notes: args.notes });
  return notesInfo;
}

export async function updateNoteFields(args: { noteId: number; fields: Record<string, string> }) {
  const note = {
    id: args.noteId,
    fields: args.fields
  };
  await invokeAnki('updateNoteFields', { note });
  return `Note ${args.noteId} fields updated successfully.`;
}
