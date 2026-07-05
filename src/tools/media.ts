import { invokeAnki } from '../anki.js';

export async function storeMediaFile(args: { filename: string; data?: string; path?: string; url?: string }) {
  const result = await invokeAnki<string>('storeMediaFile', args);
  return `Media file '${args.filename}' stored successfully. Result: ${result}`;
}
