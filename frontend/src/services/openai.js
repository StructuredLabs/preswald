const createChatCompletion = async (messages, source, systemContext = null) => {
  // For demo/development, you might want to use a hardcoded API key
  const apiKey = process.env.REACT_APP_OPENAI_API_KEY;

  if (!apiKey) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      role: 'assistant',
      content: `I can see you're asking about the ${source} dataset. To provide a proper analysis, I'll need an API key to access OpenAI's services. The data contains ${systemContext ? 'information about your data' : 'no additional context'}.`,
    };
  }

  try {
    // Prepare messages array with system context if provided
    let formattedMessages = messages.map(({ role, content }) => ({ role, content }));

    // Add system context as the first message if available
    if (systemContext) {
      formattedMessages = [{ role: 'system', content: systemContext }, ...formattedMessages];
    }

    // Add a specific instruction about using DuckDB data if source is provided
    if (source && !systemContext) {
      formattedMessages.unshift({
        role: 'system',
        content: `You are analyzing data from a DuckDB source named "${source}". Please provide insights based on this context.`,
      });
    }

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
