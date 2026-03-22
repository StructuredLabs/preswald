import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatWidget from '@/components/widgets/ChatWidget';

vi.mock('@/services/llm', () => {
  const providers = {
    openai: { name: 'OpenAI', baseUrl: 'https://api.openai.com/v1/chat/completions', defaultModel: 'gpt-3.5-turbo', models: ['gpt-3.5-turbo', 'gpt-4'], apiKeyPlaceholder: 'sk-...', apiKeyStorageKey: 'openai_api_key' },
    minimax: { name: 'MiniMax', baseUrl: 'https://api.minimax.io/v1/chat/completions', defaultModel: 'MiniMax-M2.7', models: ['MiniMax-M2.7', 'MiniMax-M2.7-highspeed'], apiKeyPlaceholder: 'eyJ...', apiKeyStorageKey: 'minimax_api_key' },
  };
  let sp = 'openai', ak = {}, md = {};
  return {
    LLM_PROVIDERS: providers, DEFAULT_PROVIDER: 'openai',
    getSelectedProvider: () => sp, setSelectedProvider: (id) => { sp = id; },
    getProviderConfig: (id) => providers[id] || providers.openai,
    getApiKey: (id) => ak[id] || '', setApiKey: (id, k) => { ak[id] = k; },
    hasApiKey: (id) => !!ak[id],
    getSelectedModel: (id) => md[id] || providers[id]?.defaultModel || 'gpt-3.5-turbo',
    setSelectedModel: (id, m) => { md[id] = m; },
    clampTemperature: (id, t) => id === 'minimax' ? Math.max(0, Math.min(1, t)) : t,
    createChatCompletion: vi.fn().mockResolvedValue({ role: 'assistant', content: 'Hello!' }),
    _reset: () => { sp = 'openai'; ak = {}; md = {}; },
  };
});

import { _reset as resetLlm } from '@/services/llm';

describe('ChatWidget', () => {
  const props = { id: 'test-chat', value: { messages: [] }, onChange: vi.fn() };
  beforeEach(() => { vi.clearAllMocks(); resetLlm(); });

  it('renders with API key required state', () => { render(<ChatWidget {...props} />); expect(screen.getAllByText('API Key Required').length).toBeGreaterThanOrEqual(1); });
  it('shows settings on gear click', () => { render(<ChatWidget {...props} />); fireEvent.click(screen.getAllByRole('button')[0]); expect(screen.getByText('LLM Provider')).toBeInTheDocument(); expect(screen.getByText('Model')).toBeInTheDocument(); });
  it('displays OpenAI in provider select', () => { render(<ChatWidget {...props} />); fireEvent.click(screen.getAllByRole('button')[0]); expect(screen.getAllByText('OpenAI').length).toBeGreaterThanOrEqual(1); });
  it('disables input without key', () => { render(<ChatWidget {...props} />); expect(screen.getByPlaceholderText('Please set API key first...')).toBeDisabled(); });
  it('shows Open Settings button', () => { render(<ChatWidget {...props} />); expect(screen.getByText('Open Settings')).toBeInTheDocument(); });
  it('shows provider API key label', () => { render(<ChatWidget {...props} />); fireEvent.click(screen.getAllByRole('button')[0]); expect(screen.getByText('OpenAI API Key')).toBeInTheDocument(); });
  it('Save Key disabled when empty', () => { render(<ChatWidget {...props} />); fireEvent.click(screen.getAllByRole('button')[0]); expect(screen.getByText('Save Key').closest('button')).toBeDisabled(); });
  it('renders send button', () => { render(<ChatWidget {...props} />); expect(screen.getAllByRole('button').find(b => b.type === 'submit')).toBeDefined(); });
  it('applies custom className', () => { const { container } = render(<ChatWidget {...props} className="custom" />); expect(container.querySelector('#test-chat').className).toContain('custom'); });
});
