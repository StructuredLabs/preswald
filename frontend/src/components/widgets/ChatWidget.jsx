'use client';

import { Bot, Loader2, Send, User } from 'lucide-react';

import { useEffect, useMemo, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

import { cn } from '@/lib/utils';
import { createChatCompletion } from '@/services/openai';

const ChatWidget = ({
  sourceId = null,
  sourceData = null,
  value = { messages: [] },
  onChange,
  className,
}) => {
  const messages = useMemo(() => value?.messages || [], [value?.messages]);
  const label = 'Chat Assistant';
  const placeholder = 'Type your message here...';
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const [inputValue, setInputValue] = useState('');
  const [showApiInput, setShowApiInput] = useState(() => {
    // Check if API key exists in sessionStorage on component mount
    return !sessionStorage.getItem('openai_api_key');
  });
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Add this state to store the processed context
  const [sourceContext, setSourceContext] = useState(null);
  const [contextLoaded, setContextLoaded] = useState(false);

  // Process the source context only once when the component mounts or source changes
  useEffect(() => {
    // Original getSourceContext function (as fallback)
    const getSourceContext = async () => {
      if (!sourceId) return null;
      try {
        // Make API call to fetch source context data
        const response = await fetch(`/api/sources/${sourceId}/context`);
        if (!response.ok) {
          throw new Error('Failed to fetch source context');
        }
        const data = await response.json();
        return data;
      } catch (error) {
        console.error('Error getting dataframe context:', error);
        return null;
      }
    };
    const loadSourceContext = async () => {
      if (!sourceId || contextLoaded) return;

      try {
        // Use the sourceData if provided directly from DuckDB
        if (sourceData) {
          const context = formatSourceContext(sourceId, sourceData);
          setSourceContext(context);
        } else {
          const context = await getSourceContext();
          setSourceContext(context);
        }
      } catch (error) {
        console.error('Error loading source context:', error);
      } finally {
        setContextLoaded(true);
      }
    };

    loadSourceContext();
  }, [sourceId, sourceData, contextLoaded]);

  // Format the source data into a context string
  const formatSourceContext = (sourceName, data) => {
    if (!sourceName || !data || !Array.isArray(data) || data.length === 0) return null;

    try {
      // Create a summary of the data
      const rowCount = data.length;
      const sampleData = data.slice(0, 5);
      const columns = Object.keys(sampleData[0] || {});

      // Format the context as a system prompt
      return `You are an AI assistant specialized in data analysis and insights. You have been provided with the following dataset:

      Dataset Information:
      - Source Name: ${sourceName}
      - Number of Records: ${rowCount}
      - Available Columns: ${columns.join(', ')}
      
      Sample Data Preview:
      ${JSON.stringify(sampleData, null, 2)}
      
      Your responsibilities:
      1. Analyze the data structure and relationships
      2. Provide detailed insights based on the available information
      3. Answer questions specifically referencing this dataset
      4. Highlight any patterns or anomalies you observe
      5. Make data-driven recommendations when appropriate
      
      Please ensure your responses are:
      - Accurate and based on the provided data
      - Clear and well-structured
      - Include specific examples from the dataset when relevant
      - Highlight any assumptions or limitations in your analysis
      
      When answering questions, always reference specific data points to support your conclusions.`;
    } catch (error) {
      console.error('Error formatting source context:', error);
      return null;
    }
  };

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      const scrollContainer = chatContainerRef.current;
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Update the handleSubmit function to use the cached context
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    setError(null);

    const newMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    const newMessages = [...messages, newMessage];
    onChange?.({ messages: newMessages });
    setInputValue('');

    setIsLoading(true);
    try {
      const response = await createChatCompletion(newMessages, sourceId, sourceContext);
      const assistantMessage = {
        ...response,
        timestamp: new Date().toISOString(),
      };
      onChange?.({ messages: [...newMessages, assistantMessage] });
    } catch (err) {
      setError(err.message || 'An error occurred');
      console.error('Failed to get AI response:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Add this function to handle API key submission
  const handleApiKeySubmit = (e) => {
    e.preventDefault();
    if (apiKey.trim()) {
      setShowApiInput(false);
      sessionStorage.setItem('openai_api_key', apiKey.trim());
    }
  };

  return (
    <Card className={cn(`flex flex-col rounded-md shadow-md h-[600px] w-full`, className)}>
      {showApiInput ? (
        <div className="p-4 border-b">
          <form onSubmit={handleApiKeySubmit} className="space-y-4">
            <div className="space-y-2">
              <h3 className="font-semibold">Enter your OpenAI API Key</h3>
              <Input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="flex-1"
              />
            </div>
            <Button type="submit" disabled={!apiKey.trim()}>
              Save API Key
            </Button>
          </form>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center space-x-2">
              <div>
                <h3 className="font-semibold">{label}</h3>
                <p className="text-sm text-green-500 flex items-center gap-1">
                  <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></span>
                  Online
                </p>
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4" ref={chatContainerRef}>
            <div className="space-y-4">
              <div className="text-xs text-gray-500">Messages count: {messages.length}</div>

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={cn(
                    'flex w-full',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'flex items-end space-x-2 max-w-[80%]',
                      message.role === 'user' && 'flex-row-reverse space-x-reverse ml-auto'
                    )}
                  >
                    {message.role === 'user' ? (
                      <User className="h-6 w-6 flex-shrink-0" />
                    ) : (
                      <Bot className="h-6 w-6 flex-shrink-0" />
                    )}
                    <div
                      className={cn(
                        'rounded-lg p-4 shadow-sm break-words min-w-[60px] max-w-full',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground rounded-tr-none'
                          : 'bg-secondary text-secondary-foreground rounded-tl-none'
                      )}
                    >
                      <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">
                        {message.content}
                      </p>
                      <span className="text-xs opacity-70 mt-2 block">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>AI is typing...</span>
                </div>
              )}
            </div>
          </div>
          {error && (
            <div className="bg-destructive/15 text-destructive text-sm p-3 mx-4 mb-2 rounded">
              Error: {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="p-4 border-t">
            <div className="flex items-center gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={placeholder}
                className="flex-1 rounded-lg border-2 border-gray-200 px-4 py-2 focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all duration-200"
                autoComplete="off"
                spellCheck="true"
                maxLength={1000}
              />
              <Button
                type="submit"
                size="icon"
                className="bg-primary p-3 hover:bg-primary/90 transition-transform duration-200 rounded-md shadow-sm hover:scale-110"
                disabled={!inputValue.trim() || isLoading}
              >
                <Send className="h-5 w-5 text-primary-foreground" />
              </Button>
            </div>
          </form>
        </>
      )}
    </Card>
  );
};

export default ChatWidget;
