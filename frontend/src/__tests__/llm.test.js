import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { LLM_PROVIDERS, DEFAULT_PROVIDER, createChatCompletion, getSelectedProvider, setSelectedProvider, getProviderConfig, getApiKey, setApiKey, hasApiKey, getSelectedModel, setSelectedModel, clampTemperature } from '@/services/llm';

describe('LLM Service', () => {
  beforeEach(() => { sessionStorage.clear(); });

  describe('LLM_PROVIDERS', () => {
    it('includes OpenAI provider', () => { expect(LLM_PROVIDERS.openai).toBeDefined(); expect(LLM_PROVIDERS.openai.name).toBe('OpenAI'); });
    it('includes MiniMax provider', () => { expect(LLM_PROVIDERS.minimax).toBeDefined(); expect(LLM_PROVIDERS.minimax.name).toBe('MiniMax'); expect(LLM_PROVIDERS.minimax.baseUrl).toBe('https://api.minimax.io/v1/chat/completions'); });
    it('MiniMax lists M3 and M2.7 models', () => { const m = LLM_PROVIDERS.minimax.models; expect(m).toContain('MiniMax-M3'); expect(m).toContain('MiniMax-M2.7'); expect(m).toContain('MiniMax-M2.7-highspeed'); });
    it('MiniMax defaults to M3', () => { expect(LLM_PROVIDERS.minimax.defaultModel).toBe('MiniMax-M3'); });
    it('each provider has required fields', () => { Object.values(LLM_PROVIDERS).forEach((cfg) => { expect(cfg.name).toBeTruthy(); expect(cfg.baseUrl).toBeTruthy(); expect(cfg.defaultModel).toBeTruthy(); expect(cfg.models.length).toBeGreaterThan(0); expect(cfg.apiKeyStorageKey).toBeTruthy(); }); });
  });

  describe('provider selection', () => {
    it('defaults to openai', () => { expect(getSelectedProvider()).toBe('openai'); });
    it('switches to minimax', () => { setSelectedProvider('minimax'); expect(getSelectedProvider()).toBe('minimax'); });
    it('DEFAULT_PROVIDER is openai', () => { expect(DEFAULT_PROVIDER).toBe('openai'); });
  });

  describe('getProviderConfig', () => {
    it('returns openai config', () => { expect(getProviderConfig('openai').name).toBe('OpenAI'); });
    it('returns minimax config', () => { const c = getProviderConfig('minimax'); expect(c.name).toBe('MiniMax'); expect(c.baseUrl).toContain('minimax.io'); });
    it('falls back for unknown', () => { expect(getProviderConfig('x').name).toBe('OpenAI'); });
  });

  describe('API key management', () => {
    it('getApiKey empty when unset', () => { expect(getApiKey('openai')).toBe(''); });
    it('round-trips openai key', () => { setApiKey('openai', 'sk-test'); expect(getApiKey('openai')).toBe('sk-test'); });
    it('round-trips minimax key', () => { setApiKey('minimax', 'eyJt'); expect(getApiKey('minimax')).toBe('eyJt'); });
    it('keys are isolated', () => { setApiKey('openai', 'sk'); setApiKey('minimax', 'ey'); expect(getApiKey('openai')).toBe('sk'); expect(getApiKey('minimax')).toBe('ey'); });
    it('hasApiKey false when unset', () => { expect(hasApiKey('minimax')).toBe(false); });
    it('hasApiKey true after set', () => { setApiKey('minimax', 'k'); expect(hasApiKey('minimax')).toBe(true); });
  });

  describe('model selection', () => {
    it('defaults to provider model', () => { expect(getSelectedModel('openai')).toBe('gpt-3.5-turbo'); expect(getSelectedModel('minimax')).toBe('MiniMax-M3'); });
    it('persists model', () => { setSelectedModel('minimax', 'MiniMax-M2.7-highspeed'); expect(getSelectedModel('minimax')).toBe('MiniMax-M2.7-highspeed'); });
    it('models are isolated', () => { setSelectedModel('openai', 'gpt-4'); setSelectedModel('minimax', 'MiniMax-M2.7-highspeed'); expect(getSelectedModel('openai')).toBe('gpt-4'); expect(getSelectedModel('minimax')).toBe('MiniMax-M2.7-highspeed'); });
  });

  describe('clampTemperature', () => {
    it('clamps minimax to [0,1]', () => { expect(clampTemperature('minimax', -0.5)).toBe(0); expect(clampTemperature('minimax', 0)).toBe(0); expect(clampTemperature('minimax', 0.7)).toBe(0.7); expect(clampTemperature('minimax', 1)).toBe(1); expect(clampTemperature('minimax', 2)).toBe(1); });
    it('passes through for openai', () => { expect(clampTemperature('openai', 1.5)).toBe(1.5); });
  });

  describe('createChatCompletion', () => {
    afterEach(() => { vi.restoreAllMocks(); });
    it('throws without key', async () => { await expect(createChatCompletion([{role:'user',content:'hi'}])).rejects.toThrow(/API key not found/); });
    it('calls OpenAI endpoint', async () => { setApiKey('openai','sk-t'); setSelectedProvider('openai'); const f = vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:true,json:()=>Promise.resolve({choices:[{message:{role:'assistant',content:'hi'}}]})}); await createChatCompletion([{role:'user',content:'hello'}]); expect(f).toHaveBeenCalledWith('https://api.openai.com/v1/chat/completions',expect.objectContaining({method:'POST'})); });
    it('calls MiniMax endpoint', async () => { setApiKey('minimax','eyJ'); setSelectedProvider('minimax'); const f = vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:true,json:()=>Promise.resolve({choices:[{message:{role:'assistant',content:'hi'}}]})}); await createChatCompletion([{role:'user',content:'hello'}]); expect(f).toHaveBeenCalledWith('https://api.minimax.io/v1/chat/completions',expect.objectContaining({method:'POST'})); const b = JSON.parse(f.mock.calls[0][1].body); expect(b.model).toBe('MiniMax-M3'); });
    it('uses selected model', async () => { setApiKey('minimax','eyJ'); setSelectedProvider('minimax'); setSelectedModel('minimax','MiniMax-M2.7-highspeed'); const f = vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:true,json:()=>Promise.resolve({choices:[{message:{role:'assistant',content:'ok'}}]})}); await createChatCompletion([{role:'user',content:'t'}]); expect(JSON.parse(f.mock.calls[0][1].body).model).toBe('MiniMax-M2.7-highspeed'); });
    it('prepends system context', async () => { setApiKey('openai','sk'); setSelectedProvider('openai'); const f = vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:true,json:()=>Promise.resolve({choices:[{message:{role:'assistant',content:'ok'}}]})}); await createChatCompletion([{role:'user',content:'hi'}],'s','ctx'); const b = JSON.parse(f.mock.calls[0][1].body); expect(b.messages[0]).toEqual({role:'system',content:'ctx'}); });
    it('propagates error', async () => { setApiKey('minimax','k'); setSelectedProvider('minimax'); vi.spyOn(globalThis,'fetch').mockResolvedValue({ok:false,json:()=>Promise.resolve({error:{message:'bad key'}})}); await expect(createChatCompletion([{role:'user',content:'t'}])).rejects.toThrow('bad key'); });
    it('handles network error', async () => { setApiKey('openai','sk'); setSelectedProvider('openai'); vi.spyOn(globalThis,'fetch').mockRejectedValue(new Error('net')); await expect(createChatCompletion([{role:'user',content:'t'}])).rejects.toThrow('net'); });
  });
});
