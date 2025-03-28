import React from 'react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const DownloadButtonWidget = ({ label, content, file_name, mime_type, size = 1.0 }) => {
  const handleDownload = () => {
    try {
      const byteCharacters = atob(content);
      const byteNumbers = new Array(byteCharacters.length)
        .fill()
        .map((_, i) => byteCharacters.charCodeAt(i));

      const blob = new Blob([new Uint8Array(byteNumbers)], { type: mime_type });
      const url = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = file_name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download the file.');
    }
  };

  return (
    <Card className="mb-4 p-4 rounded-2xl shadow-md" style={{ width: `${size * 100}%` }}>
      <Button onClick={handleDownload} className="w-full" variant="outline">
        {label}
      </Button>
    </Card>
  );
};

export default DownloadButtonWidget;
