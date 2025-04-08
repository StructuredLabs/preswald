import ReactJsonView from '@microlink/react-json-view';
import { CopyIcon } from '@radix-ui/react-icons';

import { useId, useMemo } from 'react';

import { Card, CardTitle } from '@/components/ui/card';

const JsonViewerWidget = ({ src, title, expanded }) => {
  const componentId = useId();

  const parsedSrc = useMemo(() => {
    try {
      return JSON.parse(JSON.stringify(src));
    } catch (err) {
      return {
        error: 'Invalid src provided, make sure src is list, dict or valid json string',
      };
    }
  }, [src]);

  function handleCopy() {
    const clipboardButton = document.getElementById(componentId);
    window.navigator.clipboard.writeText(JSON.stringify(parsedSrc));

    if (!clipboardButton) {
      return;
    }
    clipboardButton.classList.add('text-green-600');
    setTimeout(() => clipboardButton.classList.remove('text-green-600'), 2000);
  }

  return (
    <Card className="mb-4 p-2 overflow-hidden flex flex-col justify-center gap-4">
      <CardTitle>{title}</CardTitle>

      <div className="relative">
        <button onClick={handleCopy} className="json-clipboard-button" id={componentId}>
          <CopyIcon />
        </button>

        <ReactJsonView
          theme="monokai"
          style={{ padding: '10px', borderRadius: '5px' }}
          name={null}
          src={src}
          collapsed={!expanded}
          displayArrayKey={false}
          displayDataTypes={false}
          displayObjectSize={false}
          enableClipboard={false}
        />
      </div>
    </Card>
  );
};

export default JsonViewerWidget;
