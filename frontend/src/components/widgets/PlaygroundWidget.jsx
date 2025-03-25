import React, { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import TableViewerWidget from '@/components/widgets/TableViewerWidget';

export default function PlaygroundWidget({
  data = [],
  label = 'Table Viewer',
  value,
  onChange,
  source,
  id,
  error,
}) {
  const [query, setQuery] = useState();

  function handleQueryRun() {
    onChange?.(query);
  }

  useEffect(() => {
    setQuery(value);
  }, [value]);

  return (
    <div className="flex flex-col gap-2">
      <h1 className="text-xl font-semibold">{label}</h1>
      <h2>Source Used: {source ? source : 'All (By Default)'}</h2>
      <Input
        onChange={(e) => setQuery(e.target.value)}
        placeholder={'Please enter a query'}
        value={query}
        id={id}
        name={id}
        className="w-full min-w-full py-2 mt-4 rounded"
      />
      <Button
        onClick={handleQueryRun}
        className="ml-auto py-2 px-2 bg-black hover:bg-neutral-800 text-white rounded"
      >
        Run Query
      </Button>
      {error && <h3 className="text-red-500">{error}</h3>}
      <TableViewerWidget data={data} title="" />
    </div>
  );
}
