import React from 'react';
import { QueueProvider } from './providers/state';
import QueueComponent from './components/QueueComponent';
import ProgressMessage from './components/ProgressMessage';

function App() {
  return (
    <QueueProvider>
      <div>
        <ProgressMessage />
        <QueueComponent />
      </div>
    </QueueProvider>
  );
}

export default App;
