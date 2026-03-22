import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { createChatCompletion, getSelectedProvider, setSelectedProvider, setApiKey, hasApiKey, getSelectedModel, setSelectedModel } from '@/services/llm';

describe('LLM Service integration', () => {
  beforeEach(() => { sessionStorage.clear(); });
  afterEach(() => { vi.restoreAllMocks(); });

  it('full flow: switch, key, model, call', async () => {
    expect(getSelectedProvider()).toBe('openai');
    setSelectedProvider('minimax');
    setApiKey('minimax', 'eyJ-int');
    expect(hasApiKey('minimax')).toBe(true);
    setSelectedModel('minimax', 'MiniMax-M2.5-highspeed');
    const f = vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: () => Promise.resolve({ choices: [{ message: { role: 'assistant', content: 'ok' } }] }) });
    const r = await createChatCompletion([{ role: 'user', content: 'hi' }]);
    expect(r).toEqual({ role: 'assistant', content: 'ok' });
    const [url, opts] = f.mock.calls[0];
    expect(url).toBe('https://api.minimax.io/v1/chat/completions');
    expect(opts.headers.Authorization).toBe('Bearer eyJ-int');
    expect(JSON.parse(opts.body).model).toBe('MiniMax-M2.5-highspeed');
  });

  it('provider switch preserves state', async () => {
    setApiKey('openai', 'sk'); setApiKey('minimax', 'ey');
    setSelectedModel('openai', 'gpt-4'); setSelectedModel('minimax', 'MiniMax-M2.7-highspeed');
    const f = vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: () => Promise.resolve({ choices: [{ message: { role: 'assistant', content: 'ok' } }] }) });
    setSelectedProvider('openai');
    await createChatCompletion([{ role: 'user', content: 'q1' }]);
    expect(JSON.parse(f.mock.calls[0][1].body).model).toBe('gpt-4');
    setSelectedProvider('minimax');
    await createChatCompletion([{ role: 'user', content: 'q2' }]);
    expect(JSON.parse(f.mock.calls[1][1].body).model).toBe('MiniMax-M2.7-highspeed');
    setSelectedProvider('openai');
    await createChatCompletion([{ role: 'user', content: 'q3' }]);
    expect(JSON.parse(f.mock.calls[2][1].body).model).toBe('gpt-4');
  });

  it('backward-compat re-export', async () => {
    const m = await import('@/services/openai');
    expect(typeof m.createChatCompletion).toBe('function');
  });
});
