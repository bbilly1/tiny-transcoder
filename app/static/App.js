import React, { useState } from 'react';
import QueueComponent from './components/QueueComponent';
import ProgressMessage from './components/ProgressMessage';

function App() {
  const [queue, setQueue] = useState([]);
  const [progress, setProgress] = useState(null);

  return (
    <div>
      <ProgressMessage progress={progress} setProgress={setProgress} setQueue={setQueue}/>
      <QueueComponent queue={queue} setQueue={setQueue} setProgress={setProgress}/>
    </div>
  );
}

export default App;
