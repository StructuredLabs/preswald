import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createChatCompletion,
  getSelectedProvider,
  setSelectedProvider,
  setApiKey,
  setSelectedModel,
  getSelectedModel,
  hasApiKey,
} from '../llm';

// Mock sessionStorage
const mockStorage = {};
const sessionStorageMock = {
  getItem: vi.fn((key) => mockStorage[key] || null),
  setItem: vi.fn((key, value) => {
    mockStorage[key] = value;
  }),
  removeItem: vi.fn((key) => {
    delete mockStorage[key];
  }),
  clear: vi.fn(() => {
    Object.keys(mockStorage).forEach((key) => delete mockStorage[key]);
  }),
};
Object.defineProperty(globalThis, 'sessionStorage', { value: sessionStorageMock });

const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('Integration: provider switching workflow', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
    mockFetch.mockReset();
  });

  it('should switch from OpenAI to MiniMax and back', async () => {
    // Start with OpenAI
    expect(getSelectedProvider()).toBe('openai');
    setApiKey('openai', 'sk-openai-key');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'OpenAI response' } }],
      }),
    });

    let result = await createChatCompletion(
      [{ role: 'user', content: 'test' }],
      'src',
      null
    );
    expect(result.content).toBe('OpenAI response');
    expect(mockFetch.mock.calls[0][0]).toContain('openai.com');

    // Switch to MiniMax
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-minimax-key');
    expect(getSelectedProvider()).toBe('minimax');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'MiniMax response' } }],
      }),
    });

    result = await createChatCompletion(
      [{ role: 'user', content: 'test' }],
      'src',
      null
    );
    expect(result.content).toBe('MiniMax response');
    expect(mockFetch.mock.calls[1][0]).toContain('minimax.io');

    // Switch back to OpenAI - key should still be there
    setSelectedProvider('openai');
    expect(hasApiKey('openai')).toBe(true);

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'Back to OpenAI' } }],
      }),
    });

    result = await createChatCompletion(
      [{ role: 'user', content: 'test' }],
      'src',
      null
    );
    expect(result.content).toBe('Back to OpenAI');
    expect(mockFetch.mock.calls[2][0]).toContain('openai.com');
  });

  it('should handle multi-turn conversation with MiniMax', async () => {
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-key');

    const systemContext = 'You are a data analyst for the iris dataset.';
    const messages = [
      { role: 'user', content: 'What columns are available?' },
    ];

    // First turn
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [
          {
            message: {
              role: 'assistant',
              content: 'The dataset has: sepal_length, sepal_width, petal_length, petal_width, species.',
            },
          },
        ],
      }),
    });

    const reply1 = await createChatCompletion(messages, 'iris', systemContext);
    expect(reply1.role).toBe('assistant');

    // Second turn
    messages.push(reply1);
    messages.push({ role: 'user', content: 'Show me the average sepal_length by species.' });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [
          {
            message: {
              role: 'assistant',
              content: 'The average sepal length by species is:\n- setosa: 5.01\n- versicolor: 5.94\n- virginica: 6.59',
            },
          },
        ],
      }),
    });

    const reply2 = await createChatCompletion(messages, 'iris', systemContext);
    expect(reply2.content).toContain('setosa');

    // Verify system context was prepended each time
    const body1 = JSON.parse(mockFetch.mock.calls[0][1].body);
    const body2 = JSON.parse(mockFetch.mock.calls[1][1].body);
    expect(body1.messages[0].role).toBe('system');
    expect(body2.messages[0].role).toBe('system');
    expect(body2.messages.length).toBe(4); // system + user + assistant + user
  });

  it('should use correct model after model change', async () => {
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-key');

    // Use default model first
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'default model' } }],
      }),
    });

    await createChatCompletion([{ role: 'user', content: 'hi' }], 'src', null);
    let body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.model).toBe('MiniMax-M3');

    // Switch model
    setSelectedModel('minimax', 'MiniMax-M2.7-highspeed');
    expect(getSelectedModel('minimax')).toBe('MiniMax-M2.7-highspeed');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'highspeed model' } }],
      }),
    });

    await createChatCompletion([{ role: 'user', content: 'hi' }], 'src', null);
    body = JSON.parse(mockFetch.mock.calls[1][1].body);
    expect(body.model).toBe('MiniMax-M2.7-highspeed');
  });
});
