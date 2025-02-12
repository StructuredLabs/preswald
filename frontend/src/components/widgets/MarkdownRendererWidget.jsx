import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { cn } from '@/lib/utils';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';

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
    default: 'bg-card',
    outline: 'border rounded-lg',
    ghost: 'bg-transparent',
  };

  const components = {
    // Style headings
    h1: ({ className, ...props }) => (
      <h1
        className={cn('scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl', className)}
        {...props}
      />
    ),
    h2: ({ className, ...props }) => (
      <h2
        className={cn(
          'scroll-m-20 pb-2 text-3xl font-semibold tracking-tight first:mt-0',
          className
        )}
        {...props}
      />
    ),
    h3: ({ className, ...props }) => (
      <h3
        className={cn('scroll-m-20 text-2xl font-semibold tracking-tight', className)}
        {...props}
      />
    ),
    // Style links
    a: ({ className, ...props }) => (
      <a
        className={cn('font-medium text-primary underline underline-offset-4', className)}
        {...props}
      />
    ),
    // Style code blocks
    pre: ({ className, ...props }) => (
      <pre
        className={cn(
          'mb-6 mt-6 overflow-x-auto rounded-lg',
          'bg-zinc-950 dark:bg-zinc-900',
          'border border-zinc-200 dark:border-zinc-800',
          'p-4 shadow-sm',
          className
        )}
        {...props}
      />
    ),
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      const lang = match ? match[1] : '';
      const isInline = inline || !lang;
      
      if (isInline) {
        return (
          <code
            className={cn(
              'relative rounded px-[0.3rem] py-[0.2rem] font-mono text-sm',
              'bg-zinc-100 dark:bg-zinc-800',
              'text-zinc-900 dark:text-zinc-100',
              'whitespace-normal',
              'inline-block',
              className
            )}
            {...props}
          >
            {children}
          </code>
        );
      }

      return (
        <div className="relative">
          {lang && (
            <div className="absolute right-2 top-2 z-10">
              <span className="rounded-md bg-zinc-700 px-2 py-1 text-xs font-medium text-zinc-200">
                {lang}
              </span>
            </div>
          )}
          <SyntaxHighlighter
            language={lang}
            style={oneDark}
            customStyle={{
              margin: 0,
              borderRadius: '0.5rem',
              background: 'rgb(24 24 27)',
            }}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      );
    },
    // Style blockquotes
    blockquote: ({ className, ...props }) => (
      <blockquote className={cn('mt-6 border-l-2 pl-6 italic', className)} {...props} />
    ),
    // Style lists
    ul: ({ className, ...props }) => (
      <ul className={cn('my-6 ml-6 list-disc [&>li]:mt-2', className)} {...props} />
    ),
    ol: ({ className, ...props }) => (
      <ol className={cn('my-6 ml-6 list-decimal [&>li]:mt-2', className)} {...props} />
    ),
    // Style tables
    table: ({ className, ...props }) => (
      <div className="my-6 w-full overflow-y-auto">
        <table className={cn('w-full', className)} {...props} />
      </div>
    ),
    th: ({ className, ...props }) => (
      <th
        className={cn(
          'border px-4 py-2 text-left font-bold [&[align=center]]:text-center [&[align=right]]:text-right',
          className
        )}
        {...props}
      />
    ),
    td: ({ className, ...props }) => (
      <td
        className={cn(
          'border px-4 py-2 text-left [&[align=center]]:text-center [&[align=right]]:text-right',
          className
        )}
        {...props}
      />
    ),
  };

  return (
    <Card
      className={cn(
        'w-full',
        variantStyles[variant],
        variant === 'ghost' && 'border-none shadow-none',
        className
      )}
    >
      <CardContent
        className={cn(
          'prose prose-sm md:prose-base lg:prose-lg dark:prose-invert max-w-none',
          'prose-headings:scroll-m-20',
          'prose-p:leading-7',
          'prose-li:marker:text-muted-foreground',
          'prose-pre:p-0',
          'prose-pre:bg-transparent',
          'prose-code:text-zinc-900 dark:prose-code:text-zinc-100',
          'prose-pre:shadow-lg',
          variant === 'ghost' ? 'p-0' : 'p-6'
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
