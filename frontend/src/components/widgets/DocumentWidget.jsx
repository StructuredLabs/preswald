import PropTypes from 'prop-types';

import { useEffect, useState } from 'react';

export default function DocumentWidget({ file_path, title, blob }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState({ hasError: false, message: '' });
  const [pdfUrl, setPdfUrl] = useState('');
  const isPDF = file_path?.toLowerCase().endsWith('.pdf');

  useEffect(() => {
    if (!blob) {
      setError({ hasError: true, message: 'No PDF data provided' });
      setLoading(false);
      return;
    }

    try {
      // Validate base64 string
      if (!/^[A-Za-z0-9+/=]+$/.test(blob)) {
        throw new Error('Invalid base64 data');
      }

      // Create a blob URL instead of using data URL directly
      const binaryString = atob(blob);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const pdfBlob = new Blob([bytes], {
        type: 'application/pdf',
      });

      // Validate PDF type
      if (!pdfBlob.type.startsWith('application/pdf')) {
        throw new Error('Invalid PDF format');
      }

      const url = URL.createObjectURL(pdfBlob);
      setPdfUrl(url);
      setLoading(false);

      // Clean up the blob URL when component unmounts
      return () => {
        URL.revokeObjectURL(url);
      };
    } catch (error) {
      console.error('Error creating PDF URL:', error);
      setError({
        hasError: true,
        message: `Failed to load PDF: ${error.message}`,
      });
      setLoading(false);
    }
  }, [blob]);

  if (!isPDF) {
    return (
      <div className="document-widget">
        <h1 className="text-lg font-medium">{title}</h1>
        <p className="text-sm text-muted-foreground">{file_path}</p>
      </div>
    );
  }

  return (
    <div className="document-widget">
      <div className="document-container w-full h-[800px] flex flex-col justify-center items-center border rounded-lg overflow-auto">
        {loading && (
          <div className="flex flex-col items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            <p className="text-sm text-muted-foreground">Loading PDF...</p>
          </div>
        )}
        {error.hasError ? (
          <div className="flex flex-col items-center justify-center gap-2">
            <p className="text-sm text-destructive">{error.message}</p>
          </div>
        ) : (
          <object
            data={pdfUrl}
            type="application/pdf"
            className="w-full h-full"
            aria-label={`PDF document: ${title}`}
          >
            <div className="flex flex-col items-center justify-center gap-2">
              <p className="text-sm text-destructive">
                Unable to display PDF. Please download the file instead.
              </p>
              <a
                href={pdfUrl}
                download={title || 'document.pdf'}
                className="text-sm text-primary hover:underline"
                rel="noopener noreferrer"
              >
                Download PDF
              </a>
            </div>
          </object>
        )}
      </div>
    </div>
  );
}

// Add prop types validation
DocumentWidget.propTypes = {
  file_path: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  blob: PropTypes.string,
};

DocumentWidget.defaultProps = {
  blob: null,
};
