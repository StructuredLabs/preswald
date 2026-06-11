/**
 * Multi-provider LLM service for Preswald chat.
 *
 * Supported providers:
 *   - OpenAI (default)
 *   - MiniMax (OpenAI-compatible API)
 */

const LLM_PROVIDERS = {
  openai: {
    name: 'OpenAI',
    baseUrl: 'https://api.openai.com/v1/chat/completions',
    defaultModel: 'gpt-3.5-turbo',
    models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4o-mini'],
    apiKeyPlaceholder: 'sk-...',
    apiKeyStorageKey: 'openai_api_key',
  },
  minimax: {
    name: 'MiniMax',
    baseUrl: 'https://api.minimax.io/v1/chat/completions',
    defaultModel: 'MiniMax-M3',
    models: ['MiniMax-M3', 'MiniMax-M2.7', 'MiniMax-M2.7-highspeed'],
    apiKeyPlaceholder: 'eyJ...',
    apiKeyStorageKey: 'minimax_api_key',
  },
};

const DEFAULT_PROVIDER = 'openai';

/**
 * Get the currently selected provider ID from session storage.
 */
const getSelectedProvider = () => {
  return sessionStorage.getItem('llm_provider') || DEFAULT_PROVIDER;
};

/**
 * Set the selected provider ID in session storage.
 */
const setSelectedProvider = (providerId) => {
  sessionStorage.setItem('llm_provider', providerId);
};

/**
 * Get the provider config for a given provider ID.
 */
const getProviderConfig = (providerId) => {
  return LLM_PROVIDERS[providerId] || LLM_PROVIDERS[DEFAULT_PROVIDER];
};

/**
 * Get the API key for the current (or specified) provider.
 */
const getApiKey = (providerId) => {
  const config = getProviderConfig(providerId || getSelectedProvider());
  return sessionStorage.getItem(config.apiKeyStorageKey) || '';
};

/**
 * Save the API key for a given provider.
 */
const setApiKey = (providerId, key) => {
  const config = getProviderConfig(providerId);
  sessionStorage.setItem(config.apiKeyStorageKey, key);
};

/**
 * Check whether an API key is configured for the current provider.
 */
const hasApiKey = (providerId) => {
  return !!getApiKey(providerId || getSelectedProvider());
};

/**
 * Get the selected model for the current provider, falling back to the default.
 */
const getSelectedModel = (providerId) => {
  const id = providerId || getSelectedProvider();
  return sessionStorage.getItem(`${id}_model`) || getProviderConfig(id).defaultModel;
};

/**
 * Save the selected model for a provider.
 */
const setSelectedModel = (providerId, model) => {
  sessionStorage.setItem(`${providerId}_model`, model);
};

/**
 * Clamp temperature for providers that require it.
 */
const clampTemperature = (providerId, temperature) => {
  if (providerId === 'minimax') {
    return Math.max(0, Math.min(1, temperature));
  }
  return temperature;
};

/**
 * Create a chat completion using the currently selected LLM provider.
 */
const createChatCompletion = async (messages, sourceId, sourceContext) => {
  const providerId = getSelectedProvider();
  const config = getProviderConfig(providerId);
  const apiKey = getApiKey(providerId);

  if (!apiKey) {
    throw new Error(`API key not found for ${config.name}. Please set your API key in settings.`);
  }

  let formattedMessages = messages.map(({ role, content }) => ({ role, content }));

  if (sourceContext) {
    formattedMessages.unshift({ role: 'system', content: sourceContext });
  }

  const model = getSelectedModel(providerId);
  const body = {
    model,
    messages: formattedMessages,
  };

  try {
    const response = await fetch(config.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || `Failed to get response from ${config.name}`);
    }

    const data = await response.json();
    return data.choices[0].message;
  } catch (error) {
    console.error(`Error calling ${config.name} API:`, error);
    throw error;
  }
};

export {
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
};
