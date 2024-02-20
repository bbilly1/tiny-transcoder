// state.js
import React, { createContext, useState, useContext } from 'react';

const QueueContext = createContext();

export const QueueProvider = ({ children }) => {
  const [queue, setQueue] = useState([]);
  const [progress, setProgress] = useState(null);

  return (
    <QueueContext.Provider value={{ queue, setQueue, progress, setProgress }}>
      {children}
    </QueueContext.Provider>
  );
};

export const useQueue = () => useContext(QueueContext);
