import React, { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

import { comm } from '@/utils/websocket';

const DebugPanel = () => {
  const [visible, setVisible] = useState(false);
  const [debugState, setDebugState] = useState({});

  useEffect(() => {
    const unsubscribe = comm.subscribe((message) => {
      if (message.type === '__debug__') {
        console.log('[DebugPanel] Received debug state:', message);
        setDebugState(message.payload);
      }
    });

    comm.connect();

    return () => {
      unsubscribe();
    };
  }, []);

  const [openSections, setOpenSections] = useState({});

  const toggleSection = (key) => {
    setOpenSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Button onClick={() => setVisible(!visible)} className="mb-2">
        {visible ? 'Hide Debug' : 'Show Debug'}
      </Button>
      {visible && (
        <Card className="w-[400px] h-[500px] overflow-hidden shadow-lg border bg-white dark:bg-gray-900 text-sm">
          <ScrollArea className="p-4 h-full">
            {Object.entries(debugState).map(([key, value]) => (
              <div key={key} className="mb-2">
                <Button
                  onClick={() => toggleSection(key)}
                  className="w-full text-left font-semibold py-1 hover:underline"
                >
                  {openSections[key] ? '▾' : '▸'} {key}
                </Button>
                {openSections[key] && (
                  <pre className="ml-4 whitespace-pre-wrap text-xs">
                    {JSON.stringify(value, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </ScrollArea>
        </Card>
      )}
    </div>
  );
};

export default DebugPanel;
