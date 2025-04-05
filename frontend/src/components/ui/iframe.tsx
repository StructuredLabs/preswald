import { useState, useId, useEffect } from "react";
import * as React from "react";

const Iframe = ({
  url = "",
  title = "Embedded Iframe",
  width = "100%",
  height = "500px",
}) => {
  const [error, setError] = useState<string | null>(null);
  const iframeId = useId();
  const iframeStyles = {
    width: width,
    height: height,
    border: "none",
  };

  useEffect(() => {
    // checking if the URL is accessible
    fetch(url, { method: "head", mode: "no-cors" }).catch(() => {
      setError(
        "This URL appears to be inaccessible. Please check if the website is online and the URL is correct.",
      );
    });
  }, [url]);

  function checkIfIframeIsLoaded() {
    const iframe = document.getElementById(iframeId) as HTMLIFrameElement;
    try {
      const contentWindow = iframe.contentWindow;
      const contentDocument = contentWindow?.document;
    } catch (error) {
      // trying to catch x-frame-options error
      if (error.message?.includes("Blocked a frame at")) {
        setError(
          "This website cannot be displayed in an iframe. It may be blocking embedding due to X-Frame-Options policy.",
        );
      }
    }
  }

  if (error) {
    return (
      <div className="w-full flex flex-col items-center justify-center p-4 text-center">
        <p className="text-red-500 font-medium">{error}</p>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 text-blue-500 hover:underline"
        >
          Open in new tab
        </a>
      </div>
    );
  }

  return (
    <iframe
      id={iframeId}
      src={url}
      title={title}
      style={iframeStyles}
      loading="lazy"
      allowFullScreen={true}
      sandbox="allow-scripts allow-same-origin"
      onLoad={checkIfIframeIsLoaded}
      onError={() => setError("Failed to load the iframe content.")}
    />
  );
};

export { Iframe };
