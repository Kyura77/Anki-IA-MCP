import axios from 'axios';

const ANKI_CONNECT_URL = process.env.ANKI_CONNECT_URL || 'http://127.0.0.1:8765';

/**
 * Invokes an action on the local AnkiConnect API.
 * @param action The name of the AnkiConnect action (e.g., 'deckNames')
 * @param params The parameters for the action
 * @param version The AnkiConnect API version to use (default 6)
 * @returns The result of the action
 */
export async function invokeAnki<T = any>(action: string, params: Record<string, any> = {}, version: number = 6): Promise<T> {
  try {
    const response = await axios.post(ANKI_CONNECT_URL, {
      action,
      version,
      params,
    });

    const data = response.data;
    if (Object.prototype.hasOwnProperty.call(data, 'error') && data.error !== null) {
      throw new Error(`AnkiConnect Error: ${data.error}`);
    }

    return data.result as T;
  } catch (error: any) {
    if (error.code === 'ECONNREFUSED') {
      throw new Error(`Could not connect to AnkiConnect at ${ANKI_CONNECT_URL}. Is Anki open and AnkiConnect installed?`);
    }
    throw error;
  }
}
