import remarkGfm from 'remark-gfm';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const MarkdownRendererWidget = ({ markdown, value, error, className, variant = 'default' }) => {
  const content = markdown || value || '';

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Error: {error}</AlertDescription>
      </Alert>
    );
  }

  const components = {
    h1: ({ className, ...props }) => (
      <h1 className={cn('text-4xl font-bold', className)} {...props} />
    ),
    h2: ({ className, ...props }) => (
      <h2 className={cn('text-2xl font-semibold', className)} {...props} />
    ),
    h3: ({ className, ...props }) => (
      <h3 className={cn('text-xl font-semibold', className)} {...props} />
    ),
    p: ({ className, ...props }) => <p className={cn('leading-7', className)} {...props} />,
    a: ({ className, ...props }) => (
      <a
        className={cn('text-primary hover:text-primary/80 underline underline-offset-4', className)}
        {...props}
      />
    ),
    pre: ({ className, ...props }) => <pre className={cn('rounded-lg', className)} {...props} />,
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      const lang = match ? match[1] : '';
      const isInline = inline || !lang;

      if (isInline) {
        return (
          <code
            className={cn('rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm', className)}
            {...props}
          >
            {children}
          </code>
        );
      }

      return (
        <div className="relative">
          {lang && (
            <div className="absolute right-3 top-2 z-20 text-xs text-muted-foreground">{lang}</div>
          )}
          <SyntaxHighlighter
            language={lang}
            style={oneDark}
            customStyle={{
              margin: 0,
              borderRadius: '0.5rem',
              background: 'rgb(24 24 27)',
              padding: '1rem',
              fontSize: '0.875rem',
            }}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      );
    },
    blockquote: ({ className, ...props }) => (
      <blockquote className={cn('border-l-2 border-border pl-6 italic', className)} {...props} />
    ),
    ul: ({ className, ...props }) => <ul className={cn('list-disc pl-6', className)} {...props} />,
    ol: ({ className, ...props }) => (
      <ol className={cn('list-decimal pl-6', className)} {...props} />
    ),
    table: ({ className, ...props }) => (
      <div className="overflow-x-auto">
        <table className={cn('w-full', className)} {...props} />
      </div>
    ),
    th: ({ className, ...props }) => (
      <th className={cn('border px-3 py-2 text-left font-semibold', className)} {...props} />
    ),
    td: ({ className, ...props }) => (
      <td className={cn('border px-3 py-2', className)} {...props} />
    ),
  };

  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardContent className={cn('prose prose-stone dark:prose-invert max-w-none')}>
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {content}
        </ReactMarkdown>
      </CardContent>
    </Card>
  );
};

export default MarkdownRendererWidget;
