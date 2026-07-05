import { invokeAnki } from '../anki.js';

export async function createDeck(args: { deck: string }) {
  const result = await invokeAnki('createDeck', { deck: args.deck });
  return `Deck '${args.deck}' created with ID: ${result}`;
}

export async function getDeckNames() {
  const decks = await invokeAnki<string[]>('deckNames');
  return decks;
}

export async function deleteDecks(args: { decks: string[]; cardsToo: boolean }) {
  await invokeAnki('deleteDecks', { decks: args.decks, cardsToo: args.cardsToo });
  return `Decks deleted: ${args.decks.join(', ')}`;
}
