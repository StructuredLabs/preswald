import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';
import './components.css';
// Import your main App component
import './styles.css';

// Import Tailwind CSS

// Mount the root App component to the DOM
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

if ('serviceWorker' in navigator) {
  navigator.serviceWorker
    .register('./sw.js', { scope: './' })
    .then((registration) => {
      console.log('Service worker registered:', registration.scope);
    })
    .catch((error) => {
      console.log('Service worker registration failed:', error);
    });
}
