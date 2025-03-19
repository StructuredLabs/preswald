const createChatCompletion = async (messages, source, systemContext = null) => {
  // For demo/development, you might want to use a hardcoded API key
  // const apiKey = process.env.REACT_APP_OPENAI_API_KEY;
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY;

  // Prepare messages array with system context if provided
  let formattedMessages = messages.map(({ role, content }) => ({ role, content }));

  // Add system context as the first message if available
  if (systemContext) {
    formattedMessages.unshift({ role: 'system', content: systemContext });
  }

  if (!apiKey) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      role: 'assistant',
      content: `I can see you're asking about the ${source || 'data'} dataset. ${
        systemContext ? systemContext : "I don't have detailed information about this dataset."
      } To provide a proper analysis with AI capabilities, an OpenAI API key would be needed.`,
    };
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
