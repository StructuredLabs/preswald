import React, { useEffect, useState } from 'react';

const TableOfContents = () => {
  const [headers, setHeaders] = useState([]);

  useEffect(() => {
    const contentArea = document.querySelector('.dashboard-container');
    if (!contentArea) return;

    // Get all h1, h2, and h3 elements
    const headerElements = contentArea.querySelectorAll('h1, h2, h3');
    const headerList = Array.from(headerElements).map((header) => {
      if (!header.id) {
        header.id = header.textContent.replace(/\s+/g, '-').toLowerCase();
      }
      return {
        id: header.id,
        text: header.textContent,
        level: header.tagName.toLowerCase(),
      };
    });

    setHeaders(headerList);
  }, []);

  const handleClick = (id) => {
    const element = document.getElementById(id);
    if (element) {
      // Scroll to the header
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="p-4">
      <ul className="space-y-1">
        {headers.map((header) => (
          <li
            key={header.id}
            title={header.text}
            className={`${
              header.level === 'h1' ? 'ml-0 font-semibold' : header.level === 'h2' ? 'ml-2' : 'ml-4'
            } text-sm truncate cursor-pointer hover:text-primary py-1`}
            onClick={() => handleClick(header.id)}
          >
            {header.text}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TableOfContents;
