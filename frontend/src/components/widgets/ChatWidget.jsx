'use client';

import { Bot, Loader2, Send, Settings, User } from 'lucide-react';

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
  const placeholder = 'Type your message here...';
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const [inputValue, setInputValue] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const hasApiKey = useMemo(() => !!sessionStorage.getItem('openai_api_key'), []);

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
      sessionStorage.setItem('openai_api_key', apiKey.trim());
      setShowSettings(false);
      window.location.reload(); // Refresh to update hasApiKey state
    }
  };

  return (
    <Card
      className={cn(
        'flex flex-col w-full border border-border/60 rounded-lg bg-background overflow-hidden',
        'h-[100dvh] sm:h-[600px]',
        className
      )}
    >
      <div className="flex items-center justify-between px-3 sm:px-4 h-12 border-b">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'h-2 w-2 rounded-full animate-pulse',
              hasApiKey ? 'bg-emerald-500' : 'bg-amber-500'
            )}
          />
          <p className="text-xs sm:text-sm text-muted-foreground">
            {hasApiKey ? 'Online' : 'API Key Required'}
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 rounded-full"
          onClick={() => setShowSettings(!showSettings)}
        >
          <Settings className="h-4 w-4 text-muted-foreground" />
        </Button>
      </div>

      {showSettings && (
        <div className="border-b bg-muted/40">
          <div className="px-3 sm:px-4 py-3">
            <form onSubmit={handleApiKeySubmit} className="space-y-3">
              <div className="space-y-2">
                <h3 className="text-sm font-medium">OpenAI API Key</h3>
                <Input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="flex-1 transition-colors text-sm h-8"
                />
                <p className="text-xs text-muted-foreground/80">
                  Your API key will be stored in your browser's session storage.
                </p>
              </div>
              <div className="flex justify-end">
                <Button type="submit" disabled={!apiKey.trim()} size="sm" className="h-8">
                  Save Key
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div
        className="flex-1 overflow-y-auto px-3 sm:px-4 py-4 scroll-smooth"
        ref={chatContainerRef}
      >
        <div className="space-y-4">
          {!hasApiKey && !showSettings ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
              <Bot className="h-10 w-10 text-muted-foreground/30" />
              <div className="space-y-1">
                <h3 className="text-sm font-medium text-muted-foreground">API Key Required</h3>
                <p className="text-xs text-muted-foreground/70">
                  Please set your OpenAI API key to start chatting
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSettings(true)}
                  className="mt-2 h-8"
                >
                  Open Settings
                </Button>
              </div>
            </div>
          ) : (
            <>
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
                      'flex items-end gap-2 max-w-[85%] sm:max-w-[75%]',
                      message.role === 'user' && 'flex-row-reverse'
                    )}
                  >
                    {message.role === 'user' ? (
                      <User className="h-5 w-5 flex-shrink-0 text-muted-foreground/50" />
                    ) : (
                      <Bot className="h-5 w-5 flex-shrink-0 text-muted-foreground/50" />
                    )}
                    <div
                      className={cn(
                        'rounded-2xl px-3 py-2 text-sm ring-1 ring-inset break-words',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground ring-primary/10 rounded-tr-sm'
                          : 'bg-muted/50 text-foreground ring-border/50 rounded-tl-sm'
                      )}
                    >
                      <p className="whitespace-pre-wrap break-words leading-relaxed">
                        {message.content}
                      </p>
                      <span className="text-[0.65rem] opacity-50 mt-1 block">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground/70">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  <span className="text-xs">AI is typing...</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mx-3 sm:mx-4 mb-3 p-2 text-xs text-destructive bg-destructive/5 rounded-md border border-destructive/10">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-3 sm:p-4 border-t bg-muted/40">
        <div className="flex items-center gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={hasApiKey ? placeholder : 'Please set API key first...'}
            className="flex-1 transition-colors text-sm h-8 bg-background"
            autoComplete="off"
            spellCheck="true"
            maxLength={1000}
            disabled={!hasApiKey}
          />
          <Button
            type="submit"
            size="icon"
            className={cn(
              'h-8 w-8 rounded-md bg-primary text-primary-foreground transition-colors inline-flex items-center justify-center',
              !hasApiKey && 'opacity-50'
            )}
            disabled={!inputValue.trim() || isLoading || !hasApiKey}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default ChatWidget;
