import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  LLM_PROVIDERS,
  DEFAULT_PROVIDER,
  createChatCompletion,
  getSelectedProvider,
  setSelectedProvider,
  getProviderConfig,
  getApiKey,
  setApiKey,
  hasApiKey,
  getSelectedModel,
  setSelectedModel,
  clampTemperature,
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

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('LLM_PROVIDERS', () => {
  it('should contain openai provider', () => {
    expect(LLM_PROVIDERS.openai).toBeDefined();
    expect(LLM_PROVIDERS.openai.name).toBe('OpenAI');
    expect(LLM_PROVIDERS.openai.baseUrl).toContain('api.openai.com');
    expect(LLM_PROVIDERS.openai.defaultModel).toBe('gpt-3.5-turbo');
    expect(LLM_PROVIDERS.openai.models.length).toBeGreaterThan(0);
  });

  it('should contain minimax provider', () => {
    expect(LLM_PROVIDERS.minimax).toBeDefined();
    expect(LLM_PROVIDERS.minimax.name).toBe('MiniMax');
    expect(LLM_PROVIDERS.minimax.baseUrl).toContain('api.minimax.io');
    expect(LLM_PROVIDERS.minimax.defaultModel).toBe('MiniMax-M2.7');
    expect(LLM_PROVIDERS.minimax.models).toContain('MiniMax-M2.7');
    expect(LLM_PROVIDERS.minimax.models).toContain('MiniMax-M2.7-highspeed');
    expect(LLM_PROVIDERS.minimax.models).toContain('MiniMax-M2.5');
    expect(LLM_PROVIDERS.minimax.models).toContain('MiniMax-M2.5-highspeed');
  });

  it('should have separate API key storage keys per provider', () => {
    expect(LLM_PROVIDERS.openai.apiKeyStorageKey).toBe('openai_api_key');
    expect(LLM_PROVIDERS.minimax.apiKeyStorageKey).toBe('minimax_api_key');
    expect(LLM_PROVIDERS.openai.apiKeyStorageKey).not.toBe(
      LLM_PROVIDERS.minimax.apiKeyStorageKey
    );
  });

  it('should have unique placeholder for each provider', () => {
    expect(LLM_PROVIDERS.openai.apiKeyPlaceholder).toBe('sk-...');
    expect(LLM_PROVIDERS.minimax.apiKeyPlaceholder).toBe('eyJ...');
  });
});

describe('DEFAULT_PROVIDER', () => {
  it('should be openai', () => {
    expect(DEFAULT_PROVIDER).toBe('openai');
  });
});

describe('getSelectedProvider / setSelectedProvider', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
  });

  it('should return default provider when nothing is set', () => {
    expect(getSelectedProvider()).toBe('openai');
  });

  it('should return the provider after setting it', () => {
    setSelectedProvider('minimax');
    expect(sessionStorageMock.setItem).toHaveBeenCalledWith('llm_provider', 'minimax');
    expect(getSelectedProvider()).toBe('minimax');
  });
});

describe('getProviderConfig', () => {
  it('should return config for valid provider', () => {
    expect(getProviderConfig('openai').name).toBe('OpenAI');
    expect(getProviderConfig('minimax').name).toBe('MiniMax');
  });

  it('should fall back to default for unknown provider', () => {
    expect(getProviderConfig('unknown').name).toBe('OpenAI');
  });
});

describe('getApiKey / setApiKey / hasApiKey', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
  });

  it('should return empty string when no key set', () => {
    expect(getApiKey('openai')).toBe('');
    expect(getApiKey('minimax')).toBe('');
  });

  it('should store and retrieve API key per provider', () => {
    setApiKey('openai', 'sk-test123');
    expect(sessionStorageMock.setItem).toHaveBeenCalledWith('openai_api_key', 'sk-test123');
    expect(getApiKey('openai')).toBe('sk-test123');
  });

  it('should store minimax key independently', () => {
    setApiKey('minimax', 'eyJtest');
    expect(sessionStorageMock.setItem).toHaveBeenCalledWith('minimax_api_key', 'eyJtest');
    expect(getApiKey('minimax')).toBe('eyJtest');
  });

  it('hasApiKey should return false when no key set', () => {
    expect(hasApiKey('openai')).toBe(false);
  });

  it('hasApiKey should return true when key is set', () => {
    setApiKey('openai', 'sk-test');
    expect(hasApiKey('openai')).toBe(true);
  });
});

describe('getSelectedModel / setSelectedModel', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
  });

  it('should return default model when nothing set', () => {
    expect(getSelectedModel('openai')).toBe('gpt-3.5-turbo');
    expect(getSelectedModel('minimax')).toBe('MiniMax-M2.7');
  });

  it('should store and retrieve selected model', () => {
    setSelectedModel('minimax', 'MiniMax-M2.5');
    expect(sessionStorageMock.setItem).toHaveBeenCalledWith('minimax_model', 'MiniMax-M2.5');
    expect(getSelectedModel('minimax')).toBe('MiniMax-M2.5');
  });

  it('should keep models independent per provider', () => {
    setSelectedModel('openai', 'gpt-4');
    setSelectedModel('minimax', 'MiniMax-M2.7-highspeed');
    expect(getSelectedModel('openai')).toBe('gpt-4');
    expect(getSelectedModel('minimax')).toBe('MiniMax-M2.7-highspeed');
  });
});

describe('clampTemperature', () => {
  it('should clamp minimax temperature to [0, 1]', () => {
    expect(clampTemperature('minimax', 1.5)).toBe(1);
    expect(clampTemperature('minimax', -0.5)).toBe(0);
    expect(clampTemperature('minimax', 0.7)).toBe(0.7);
    expect(clampTemperature('minimax', 0)).toBe(0);
    expect(clampTemperature('minimax', 1)).toBe(1);
  });

  it('should not clamp openai temperature', () => {
    expect(clampTemperature('openai', 1.5)).toBe(1.5);
    expect(clampTemperature('openai', 2.0)).toBe(2.0);
  });
});

describe('createChatCompletion', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
    mockFetch.mockReset();
  });

  it('should throw when no API key is set', async () => {
    await expect(
      createChatCompletion([{ role: 'user', content: 'hello' }], 'src', null)
    ).rejects.toThrow('API key not found');
  });

  it('should call OpenAI endpoint with correct parameters', async () => {
    setApiKey('openai', 'sk-test');
    setSelectedProvider('openai');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'Hi!' } }],
      }),
    });

    const result = await createChatCompletion(
      [{ role: 'user', content: 'hello' }],
      'source1',
      null
    );

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toContain('api.openai.com');
    expect(options.headers.Authorization).toBe('Bearer sk-test');
    const body = JSON.parse(options.body);
    expect(body.model).toBe('gpt-3.5-turbo');
    expect(body.messages).toHaveLength(1);
    expect(result).toEqual({ role: 'assistant', content: 'Hi!' });
  });

  it('should call MiniMax endpoint when minimax is selected', async () => {
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-minimax-key');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'MiniMax reply' } }],
      }),
    });

    const result = await createChatCompletion(
      [{ role: 'user', content: 'hello' }],
      'source1',
      null
    );

    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [url, options] = mockFetch.mock.calls[0];
    expect(url).toContain('api.minimax.io');
    expect(options.headers.Authorization).toBe('Bearer eyJ-minimax-key');
    const body = JSON.parse(options.body);
    expect(body.model).toBe('MiniMax-M2.7');
    expect(result).toEqual({ role: 'assistant', content: 'MiniMax reply' });
  });

  it('should prepend system context as first message', async () => {
    setSelectedProvider('openai');
    setApiKey('openai', 'sk-test');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'response' } }],
      }),
    });

    await createChatCompletion(
      [{ role: 'user', content: 'tell me about the data' }],
      'src',
      'You are a data analyst.'
    );

    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.messages[0]).toEqual({ role: 'system', content: 'You are a data analyst.' });
    expect(body.messages[1]).toEqual({ role: 'user', content: 'tell me about the data' });
  });

  it('should use selected model when overridden', async () => {
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-key');
    setSelectedModel('minimax', 'MiniMax-M2.5-highspeed');

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        choices: [{ message: { role: 'assistant', content: 'fast' } }],
      }),
    });

    await createChatCompletion([{ role: 'user', content: 'hi' }], 'src', null);

    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.model).toBe('MiniMax-M2.5-highspeed');
  });

  it('should throw on API error response', async () => {
    setSelectedProvider('openai');
    setApiKey('openai', 'sk-bad');

    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        error: { message: 'Invalid API key' },
      }),
    });

    await expect(
      createChatCompletion([{ role: 'user', content: 'hi' }], 'src', null)
    ).rejects.toThrow('Invalid API key');
  });

  it('should throw with provider name on generic error', async () => {
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-key');

    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({}),
    });

    await expect(
      createChatCompletion([{ role: 'user', content: 'hi' }], 'src', null)
    ).rejects.toThrow('MiniMax');
  });
});
