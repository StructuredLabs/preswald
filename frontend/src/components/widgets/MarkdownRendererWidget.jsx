import remarkGfm from 'remark-gfm';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const MarkdownRendererWidget = ({
  markdown,
  value,
  error,
  className,
  variant = 'default', // default, outline, or ghost
}) => {
  const content = markdown || value || '';

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Error: {error}</AlertDescription>
      </Alert>
    );
  }

  const variantStyles = {
    default: 'markdown-card-variant-default',
    outline: 'markdown-card-variant-outline',
    ghost: 'markdown-card-variant-ghost',
  };

  const components = {
    h1: ({ className, ...props }) => (
      <h1 className={cn('markdown-heading-1', className)} {...props} />
    ),
    h2: ({ className, ...props }) => (
      <h2 className={cn('markdown-heading-2', className)} {...props} />
    ),
    h3: ({ className, ...props }) => (
      <h3 className={cn('markdown-heading-3', className)} {...props} />
    ),
    a: ({ className, ...props }) => <a className={cn('markdown-link', className)} {...props} />,
    pre: ({ className, ...props }) => (
      <pre className={cn('markdown-pre-wrapper', className)} {...props} />
    ),
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      const lang = match ? match[1] : '';
      const isInline = inline || !lang;

      if (isInline) {
        return (
          <code className={cn('markdown-inline-code', className)} {...props}>
            {children}
          </code>
        );
      }

      return (
        <div className="relative">
          {lang && <div className="markdown-code-lang">{lang}</div>}
          <SyntaxHighlighter
            language={lang}
            style={oneDark}
            customStyle={{ margin: 0, borderRadius: '0.5rem', background: 'rgb(24 24 27)' }}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      );
    },
    blockquote: ({ className, ...props }) => (
      <blockquote className={cn('markdown-blockquote', className)} {...props} />
    ),
    ul: ({ className, ...props }) => <ul className={cn('markdown-ul', className)} {...props} />,
    ol: ({ className, ...props }) => <ol className={cn('markdown-ol', className)} {...props} />,
    table: ({ className, ...props }) => (
      <div className="markdown-table-wrapper">
        <table className={cn('markdown-table', className)} {...props} />
      </div>
    ),
    th: ({ className, ...props }) => <th className={cn('markdown-th', className)} {...props} />,
    td: ({ className, ...props }) => <td className={cn('markdown-td', className)} {...props} />,
  };

  return (
    <Card className={cn('markdown-container', variantStyles[variant], className)}>
      <CardContent
        className={cn(
          'markdown-card-content markdown-headings markdown-paragraph markdown-list markdown-pre markdown-code',
          variant === 'ghost' ? 'p-0' : 'markdown-padding'
        )}
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
          {content}
        </ReactMarkdown>
      </CardContent>
    </Card>
  );
};

export default MarkdownRendererWidget;
