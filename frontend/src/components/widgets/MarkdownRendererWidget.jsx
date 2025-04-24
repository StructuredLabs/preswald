import { Link2Icon } from 'lucide-react';
import remarkGfm from 'remark-gfm';
import remarkSlug from 'remark-slug';

import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';

import { cn } from '@/lib/utils';

const MarkdownRendererWidget = ({ markdown, value, error, className }) => {
  const content = markdown || value || '';
  const [targetId, setTargetId] = useState('');

  // Handle URL hash navigation on mount
  useEffect(() => {
    // Set scroll padding for all anchor navigation
    document.documentElement.style.scrollPaddingTop = '50px';

    if (window.location.hash) {
      const hash = window.location.hash.substring(1);
      setTargetId(hash);

      // Add a small delay to ensure the headings are rendered
      setTimeout(() => {
        const element = document.getElementById(hash);
        if (element) {
          element.scrollIntoView();
          window.scrollBy(0, -50);
        }
      }, 300);
    }
  }, []);

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>Error: {error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardContent className="prose max-w-none prose-pre:p-0 prose-pre:bg-transparent prose-pre:m-0 prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-foreground prose-code:before:content-none prose-code:after:content-none prose-headings:mt-2 prose-headings:mb-2 prose-p:my-0 prose-p:mb-0.5">
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkSlug]}
          components={{
            h1: createHeadingComponent('h1', targetId),
            h2: createHeadingComponent('h2', targetId),
            h3: createHeadingComponent('h3', targetId),
            h4: createHeadingComponent('h4', targetId),
            h5: createHeadingComponent('h5', targetId),
            h6: createHeadingComponent('h6', targetId),
            code({ node, inline, className, children, ...props }) {
              // Only apply syntax highlighting for code blocks with language
              const match = /language-(\w+)/.exec(className || '');
              if (!inline && match) {
                return (
                  <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                );
              }

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

// Helper function to create heading components
function createHeadingComponent(level, targetId) {
  return function HeadingComponent({ node, children, ...props }) {
    const id = props.id || '';
    const isTarget = id === targetId;

    const copyToClipboard = () => {
      const url = `${window.location.origin}${window.location.pathname}#${id}`;
      navigator.clipboard
        .writeText(url)
        .then(() => {
          console.log('Link copied to clipboard');
        })
        .catch((err) => {
          console.error('Could not copy text: ', err);
        });
    };

    const handleHeadingClick = () => {
      copyToClipboard();
      // Update URL and scroll to the element
      window.location.hash = id;
    };

    return React.createElement(
      level,
      {
        className: cn(
          'group relative hover:cursor-pointer scroll-mt-[50px]',
          isTarget && 'bg-muted/30'
        ),
        id: id,
        onClick: handleHeadingClick,
      },
      <>
        <a
          href={`#${id}`}
          className="opacity-0 group-hover:opacity-100 hover:opacity-100 absolute -left-6 top-1/2 -translate-y-1/2 flex items-center justify-center text-muted-foreground no-underline transition-opacity duration-150"
          aria-label={`Link to this heading`}
          onClick={copyToClipboard}
        >
          <Link2Icon className="h-4 w-4" />
        </a>
        {children}
      </>
    );
  };
}

export default MarkdownRendererWidget;
