import Editor from '@monaco-editor/react';
import { ChevronLeftIcon, ChevronRightIcon, PlayIcon } from '@radix-ui/react-icons';

import React, { useEffect, useState } from 'react';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const ROWS_PER_PAGE = 10;

const editorOptions = {
  minimap: { enabled: false },
  fontSize: 14,
  lineNumbers: 'on',
  folding: false,
  lineDecorationsWidth: 12,
  lineNumbersMinChars: 2,
  renderLineHighlight: 'none',
  overviewRulerBorder: false,
  hideCursorInOverviewRuler: true,
  overviewRulerLanes: 0,
  glyphMargin: false,
  scrollbar: {
    vertical: 'hidden',
    horizontal: 'hidden',
  },
  scrollBeyondLastLine: false,
  wordWrap: 'on',
  padding: { top: 8, bottom: 8 },
  suggest: {
    showKeywords: false,
  },
  quickSuggestions: false,
  parameterHints: {
    enabled: false,
  },
  codeLens: false,
  contextmenu: false,
  links: false,
  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
};

export default function PlaygroundWidget({
  label = 'SQL Playground',
  value,
  onChange,
  source,
  id,
  error,
  data = null,
}) {
  const [query, setQuery] = useState();
  const [currentPage, setCurrentPage] = useState(1);

  // Process the data to get column definitions and row data
  const columnDefs = data?.columnDefs || [];
  const rowData = data?.rowData || [];

  // Calculate pagination
  const totalPages = Math.ceil(rowData.length / ROWS_PER_PAGE);
  const startIndex = (currentPage - 1) * ROWS_PER_PAGE;
  const endIndex = startIndex + ROWS_PER_PAGE;
  const currentRows = rowData.slice(startIndex, endIndex);

  function handleQueryRun() {
    onChange?.(query);
    setCurrentPage(1); // Reset to first page on new query
  }

  useEffect(() => {
    setQuery(value);
  }, [value]);

  return (
    <div className="border rounded-md border-gray-200">
      <Card className="w-full border-0 shadow-none">
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle>{label}</CardTitle>
            </div>
            <Button onClick={handleQueryRun} size="sm" className="bg-primary hover:bg-primary/90">
              <PlayIcon className="mr-2 h-4 w-4" />
              Run Query
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-0 p-0">
          <div className="border-y bg-white">
            <Editor
              height="120px"
              defaultLanguage="sql"
              value={query}
              onChange={setQuery}
              theme="vs"
              options={editorOptions}
              loading=""
            />
          </div>

          {error ? (
            <div className="p-6">
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </div>
          ) : (
            <div>
              <div className="overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="border-b border-gray-200">
                      {columnDefs.map((col) => (
                        <TableHead key={col.field} className="font-semibold bg-white">
                          {col.headerName}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {currentRows.map((row, i) => (
                      <TableRow key={i} className="border-b border-gray-200 last:border-0">
                        {columnDefs.map((col) => (
                          <TableCell key={col.field}>{row[col.field] ?? 'null'}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                    {rowData.length === 0 && (
                      <TableRow>
                        <TableCell
                          colSpan={columnDefs.length || 1}
                          className="h-24 text-center text-muted-foreground"
                        >
                          No results
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 bg-white">
                  <p className="text-sm text-muted-foreground">
                    Showing {startIndex + 1}-{Math.min(endIndex, rowData.length)} of{' '}
                    {rowData.length} results
                  </p>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeftIcon className="h-4 w-4" />
                    </Button>
                    <div className="text-sm text-muted-foreground">
                      Page {currentPage} of {totalPages}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                      disabled={currentPage === totalPages}
                    >
                      <ChevronRightIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
