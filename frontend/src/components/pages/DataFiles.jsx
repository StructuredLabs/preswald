import { TrashIcon } from '@heroicons/react/24/solid';

import React, { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';

const DataFiles = () => {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await fetch('/api/data/files');
      const data = await response.json();
      setFiles(data.files);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleDelete = async (filename) => {
    if (window.confirm(`Are you sure you want to delete ${filename}?`)) {
      try {
        await fetch(`/api/data/files/${filename}`, {
          method: 'DELETE',
        });
        fetchFiles();
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Data Files</h2>
      <div className="grid gap-4">
        {files.map((file) => (
          <div key={file.name} className="flex items-center justify-between p-4 border rounded">
            <span>{file.name}</span>
            <Button
              variant="destructive"
              size="icon"
              onClick={() => handleDelete(file.name)}
              className="h-8 w-8"
            >
              <TrashIcon className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DataFiles;
