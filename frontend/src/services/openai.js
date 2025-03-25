const createChatCompletion = async (messages, sourceId, sourceContext) => {
  const apiKey = sessionStorage.getItem('openai_api_key');
  if (!apiKey) {
    throw new Error('API key not found');
  }

  // Prepare messages array with system context if provided
  let formattedMessages = messages.map(({ role, content }) => ({ role, content }));

  // Add system context as the first message if available
  if (sourceContext) {
    formattedMessages.unshift({ role: 'system', content: sourceContext });
  }

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: formattedMessages,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Failed to get response from OpenAI');
    }

    const data = await response.json();
    return data.choices[0].message;
  } catch (error) {
    console.error('Error calling OpenAI API:', error);
    throw error;
  }
};
export { createChatCompletion };
