import { invokeAnki } from '../anki.js';

export async function getCollectionStatsHTML(args: { wholeCollection?: boolean }) {
  const result = await invokeAnki<string>('getCollectionStatsHTML', { wholeCollection: args.wholeCollection ?? true });
  return result; // Returns HTML string of stats
}

export async function getReviewsOfCards(args: { cards: number[] }) {
  // reviews is an object { "cardId": [ [reviewTime, reviewType, rating, interval, ease, timeTaken], ... ] }
  const result = await invokeAnki('getReviewsOfCards', { cards: args.cards });
  return result;
}
