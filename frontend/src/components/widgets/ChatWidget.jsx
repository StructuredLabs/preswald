import React, { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { cn } from '@/lib/utils';

const ChatWidget = ({
  label,
  placeholder,
  id = 'chat',
  className,
  error,
  disabled = false,
  required = false,
  size = 'default', // "sm", "default", "lg"
  variant = 'default', // "default", "ghost"
  onChange,
  value = [], // Add value prop to receive chat history
}) => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState(value);

  useEffect(() => {
    setChatHistory(Array.isArray(value) ? value : []);
  }, [value]);

  const handleChange = (e) => {
    const newValue = e.target.value;
    console.log('[ChatWidget] Change event:', {
      id,
      oldValue: message,
      newValue: newValue,
      timestamp: new Date().toISOString(),
    });

    try {
      setMessage(newValue);
      console.log('[ChatWidget] State updated successfully:', {
        id,
        value: newValue,
      });
    } catch (error) {
      console.error('[ChatWidget] Error updating state:', {
        id,
        error: error.message,
      });
    }
  };

  const handleSend = () => {
    if (!message.trim()) return;

    const newMessage = {
      role: 'user',
      content: message,
    };

    const updatedChatHistory = [...chatHistory, newMessage];
    setChatHistory(updatedChatHistory);
    setMessage('');

    try {
      onChange?.(updatedChatHistory);
      console.log('[ChatWidget] Message sent successfully:', {
        id,
        message: newMessage,
      });
    } catch (error) {
      console.error('[ChatWidget] Error sending message:', {
        id,
        error: error.message,
      });
    }
  };

  // Size variants
  const sizeVariants = {
    sm: 'inputfield-size-sm',
    default: 'inputfield-size-default',
    lg: 'inputfield-size-lg',
  };

  return (
    <div className={cn('chatwidget-container', className)}>
      {label && (
        <Label
          htmlFor={id}
          className={cn(
            'chatwidget-label',
            error && 'chatwidget-error',
            disabled && 'chatwidget-disabled'
          )}
        >
          {label}
          {required && <span className="chatwidget-required">*</span>}
        </Label>
      )}
      <div className="chatwidget-history">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`chatwidget-message ${msg.role}`}>
            <span>{msg.content}</span>
          </div>
        ))}
      </div>
      <textarea
        id={id}
        name={id}
        value={message}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          sizeVariants[size],
          variant === 'ghost' && 'chatwidget-variant-ghost',
          error && 'chatwidget-error-border'
        )}
        aria-invalid={error ? 'true' : undefined}
        required={required}
      />
      <Button onClick={handleSend} disabled={disabled || !message.trim()}>
        Send
      </Button>
      {error && <p className="chatwidget-error-message">{error}</p>}
    </div>
  );
};

export default ChatWidget;
