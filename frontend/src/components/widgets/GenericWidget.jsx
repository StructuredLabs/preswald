import React from 'react';

const GenericWidget = ({ id, value, mimetype = 'text/plain' }) => {
  const cleanMime = mimetype.split(';')[0].trim().toLowerCase();

  const renderContent = () => {
    if (!value) {
      return <div className="text-gray-500 italic">No content to display.</div>;
    }

    if (cleanMime.startsWith('image/')) {
      return (
        <img src={value} alt="rendered image" className="rounded-lg shadow max-w-full mx-auto" />
      );
    }

    if (cleanMime === 'text/html') {
      return <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: value }} />;
    }

    if (cleanMime === 'application/pdf') {
      return <iframe src={value} title="PDF viewer" className="w-full h-[600px] border rounded" />;
    }

    if (['text/plain', 'application/json', 'text/csv', 'text/markdown'].includes(cleanMime)) {
      return (
        <pre className="text-sm text-gray-800 whitespace-pre-wrap p-2 bg-gray-100 rounded">
          {value}
        </pre>
      );
    }

    return (
      <div className="text-sm text-gray-500 italic">
        Unsupported mimetype <code>{mimetype}</code>
      </div>
    );
  };

  return (
    <div
      id={id}
      className="border border-gray-200 rounded-md shadow-sm p-4 bg-white overflow-x-auto"
    >
      {renderContent()}
    </div>
  );
};

export default GenericWidget;
