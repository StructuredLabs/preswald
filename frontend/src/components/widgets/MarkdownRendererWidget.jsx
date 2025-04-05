import remarkGfm from 'remark-gfm';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const MarkdownRendererWidget = ({ markdown, value, error, className }) => {
  const content = markdown || value || '';

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Error: {error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardContent
        className="prose max-w-none 
        prose-pre:p-0
        prose-pre:bg-transparent
        prose-pre:m-0
        prose-code:bg-muted 
        prose-code:px-1.5 
        prose-code:py-0.5 
        prose-code:rounded 
        prose-code:text-foreground 
        prose-code:before:content-none 
        prose-code:after:content-none"
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ node, inline, className, children, ...props }) {
              // Only apply syntax highlighting if:
              // 1. It's not inline (i.e., it's a code fence block)
              // 2. It has a language specified
              const match = /language-(\w+)/.exec(className || '');
              if (!inline && match) {
                const language = match[1];
                return (
                  <SyntaxHighlighter style={oneDark} language={language} PreTag="div" {...props}>
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                );
              }

              // For all other cases (inline code or code blocks without language),
              // just return regular code element
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </CardContent>
    </Card>
  );
};

export default MarkdownRendererWidget;
