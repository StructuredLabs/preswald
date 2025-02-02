import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import React, { useEffect, useState } from 'react';

import { Badge } from "@/components/ui/badge";
import { ChevronDown } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { websocket } from '@/utils/websocket';

function MetadataView({ metadata, type }) {
  if (!metadata || metadata.error) {
    return (
      <div className="text-sm text-destructive">
        {metadata?.error || 'No metadata available'}
      </div>
    );
  }

  switch (type.toLowerCase()) {
    case 'postgresql':
      return (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div className="text-sm">
              <span className="font-medium">Database:</span> {metadata.database_name}
            </div>
            <div className="text-sm">
              <span className="font-medium">Total Tables:</span> {metadata.total_tables}
            </div>
          </div>
          <div>
            <div className="font-medium text-sm mb-2">Schemas:</div>
            {Object.entries(metadata.schemas).map(([schema, tables]) => (
              <div key={schema} className="mb-4">
                <div className="text-sm font-medium text-muted-foreground mb-2">{schema}</div>
                <div className="space-y-2">
                  {Object.entries(tables).map(([table, info]) => (
                    <Collapsible key={table}>
                      <CollapsibleTrigger className="flex items-center text-sm text-primary hover:text-primary/90 cursor-pointer">
                        <ChevronDown className="h-4 w-4 shrink-0 transition-transform duration-200" />
                        <span className="ml-2">{table} ({info.columns.length} columns)</span>
                      </CollapsibleTrigger>
                      <CollapsibleContent className="ml-6 mt-2">
                        {info.columns.map((col) => (
                          <div key={col.name} className="text-sm py-1">
                            <span className="text-muted-foreground">{col.name}</span>
                            <span className="text-muted-foreground/60 ml-1">({col.type})</span>
                          </div>
                        ))}
                      </CollapsibleContent>
                    </Collapsible>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      );

    case 'csv':
      return (
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-2">
            <div className="text-sm">
              <span className="font-medium">File Size:</span> {metadata.file_size}
            </div>
            <div className="text-sm">
              <span className="font-medium">Total Rows:</span> {metadata.total_rows}
            </div>
            <div className="text-sm">
              <span className="font-medium">Total Columns:</span> {metadata.total_columns}
            </div>
          </div>
          <div>
            <div className="font-medium text-sm mb-2">Columns:</div>
            <div className="space-y-2">
              {metadata.columns.map((col) => (
                <Collapsible key={col.name}>
                  <CollapsibleTrigger className="flex items-center text-sm text-primary hover:text-primary/90 cursor-pointer">
                    <ChevronDown className="h-4 w-4 shrink-0 transition-transform duration-200" />
                    <span className="ml-2">{col.name} ({col.type})</span>
                  </CollapsibleTrigger>
                  <CollapsibleContent className="ml-6 mt-2">
                    <div className="text-muted-foreground">Sample Values:</div>
                    <div className="text-muted-foreground/60 space-y-1">
                      {col.sample_values.map((val, i) => (
                        <div key={i}>{String(val)}</div>
                      ))}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              ))}
            </div>
          </div>
        </div>
      );

    default:
      return (
        <div className="text-sm text-muted-foreground">
          No metadata display configured for this connection type
        </div>
      );
  }
}

function ConnectionCard({ connection }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusVariant = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'configured':
        return 'default';
      default:
        return 'secondary';
    }
  };

  const getConnectionIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'postgresql':
        return '🐘';
      case 'mysql':
        return '🐬';
      case 'csv':
        return '📄';
      case 'parquet':
        return '📦';
      case 'json':
        return '🔗';
      default:
        return '🔌';
    }
  };

  return (
    <Card>
      <CardHeader className="p-4">
        <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
          <CollapsibleTrigger className="flex w-full items-center justify-between">
            <div className="flex items-center">
              <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center mr-4">
                <span className="text-lg" role="img" aria-label={connection.type}>
                  {getConnectionIcon(connection.type)}
                </span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold">
                    {connection.name}
                  </h3>
                  <Badge variant={getStatusVariant(connection.status)}>
                    {connection.status}
                  </Badge>
                </div>
                <div className="mt-1 space-y-1">
                  <p className="text-sm text-muted-foreground">
                    Type: {connection.type}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {connection.details}
                  </p>
                </div>
              </div>
            </div>
            <ChevronDown
              className={cn(
                "h-4 w-4 shrink-0 transition-transform duration-200",
                isExpanded && "rotate-180"
              )}
            />
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-4">
            <CardContent className="p-0">
              <div className="text-sm font-medium mb-2">Metadata</div>
              <MetadataView metadata={connection.metadata} type={connection.type} />
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </CardHeader>
    </Card>
  );
}

function Connections() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConnections = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/connections');
        if (!response.ok) {
          throw new Error('Failed to fetch connections');
        }
        const data = await response.json();
        setConnections(data.connections || []);
      } catch (error) {
        console.error('Error fetching connections:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchConnections();

    const unsubscribe = websocket.subscribe((message) => {
      if (message.type === 'connections_update') {
        setConnections(message.connections || []);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  if (loading) {
    return (
      <div className="p-4 space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader className="p-4">
              <div className="flex items-center">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="ml-4 space-y-2">
                  <Skeleton className="h-4 w-[200px]" />
                  <Skeleton className="h-4 w-[150px]" />
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <Card className="border-destructive">
          <CardContent className="p-6 text-center text-destructive">
            Error: {error}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">Connections</h1>
      <div className="space-y-4">
        {connections.map((connection, index) => (
          <ConnectionCard key={`${connection.name}-${index}`} connection={connection} />
        ))}
        {connections.length === 0 && (
          <Card>
            <CardContent className="p-6 text-center text-muted-foreground">
              No connections found. Add connections in your preswald.toml file to get started.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default Connections;