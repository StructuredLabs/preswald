import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent } from "@/components/ui/card";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { cn } from "@/lib/utils";
import remarkGfm from 'remark-gfm';

const MarkdownRendererWidget = ({ 
  markdown, 
  value, 
  error,
  className,
  variant = "default" // default, outline, or ghost
}) => {
  const content = markdown || value || '';

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Error: {error}
        </AlertDescription>
      </Alert>
    );
  }

  const variantStyles = {
    default: "bg-card",
    outline: "border rounded-lg",
    ghost: "bg-transparent"
  };

  const components = {
    // Style headings
    h1: ({ className, ...props }) => (
      <h1 className={cn("scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl", className)} {...props} />
    ),
    h2: ({ className, ...props }) => (
      <h2 className={cn("scroll-m-20 pb-2 text-3xl font-semibold tracking-tight first:mt-0", className)} {...props} />
    ),
    h3: ({ className, ...props }) => (
      <h3 className={cn("scroll-m-20 text-2xl font-semibold tracking-tight", className)} {...props} />
    ),
    // Style links
    a: ({ className, ...props }) => (
      <a className={cn("font-medium text-primary underline underline-offset-4", className)} {...props} />
    ),
    // Style code blocks
    code: ({ className, ...props }) => (
      <code className={cn("relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm", className)} {...props} />
    ),
    // Style blockquotes
    blockquote: ({ className, ...props }) => (
      <blockquote className={cn("mt-6 border-l-2 pl-6 italic", className)} {...props} />
    ),
    // Style lists
    ul: ({ className, ...props }) => (
      <ul className={cn("my-6 ml-6 list-disc [&>li]:mt-2", className)} {...props} />
    ),
    ol: ({ className, ...props }) => (
      <ol className={cn("my-6 ml-6 list-decimal [&>li]:mt-2", className)} {...props} />
    ),
    // Style tables
    table: ({ className, ...props }) => (
      <div className="my-6 w-full overflow-y-auto">
        <table className={cn("w-full", className)} {...props} />
      </div>
    ),
    th: ({ className, ...props }) => (
      <th className={cn("border px-4 py-2 text-left font-bold [&[align=center]]:text-center [&[align=right]]:text-right", className)} {...props} />
    ),
    td: ({ className, ...props }) => (
      <td className={cn("border px-4 py-2 text-left [&[align=center]]:text-center [&[align=right]]:text-right", className)} {...props} />
    ),
  };

  return (
    <Card className={cn(
      "w-full",
      variantStyles[variant],
      variant === "ghost" && "border-none shadow-none",
      className
    )}>
      <CardContent className={cn(
        "prose prose-sm md:prose-base lg:prose-lg dark:prose-invert max-w-none",
        "prose-headings:scroll-m-20",
        "prose-p:leading-7",
        "prose-li:marker:text-muted-foreground",
        variant === "ghost" ? "p-0" : "p-2"
      )}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </CardContent>
    </Card>
  );
};

export default MarkdownRendererWidget;
