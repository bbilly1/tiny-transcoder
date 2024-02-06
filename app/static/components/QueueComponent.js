import React, { useEffect } from 'react';
import './QueueComponent.css';
import { fetchProgressData } from './ProgressFetch';
import { fetchQueueData } from './QueueFetch';
import QueueItem from './QueueItem';
import QueueControlComponent from './QueueControlComponent';


const QueueComponent = ({ queue, setQueue, setProgress }) => {

  useEffect(() => {
    runFetch();
  }, []);  

  const runFetch = () => {
    fetchQueueData(setQueue);
  }

  const handleRunQueue = async () => {
    try {
      const response = await fetch(`/api/manage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setProgress({
          message: 'Queue started',
        });
        runFetch();
        fetchProgressData(setProgress, setQueue);
      } else {
        console.error('Failed to delete item');
      }
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  }

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`/api/queue/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setQueue(prevQueue => prevQueue.filter(item => item.id !== id));
      } else {
        console.error('Failed to delete item');
      }
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  const handleRunSingle = async (itemId) => {
    try {
      const response = await fetch(`/api/queue/${itemId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'run' }),
      });

      if (response.ok) {
        console.log(`Item ${itemId} is running`);
        runFetch();
        fetchProgressData(setProgress, setQueue);
      } else {
        console.error(`Failed to run item ${itemId}`);
      }
    } catch (error) {
      console.error(`Error running item ${itemId}:`, error);
    }
  };

  const handlePauseResume = async (itemId, currentState) => {
    let action;
    if (currentState === 'pending') {
      action = 'pause';
    } else if (currentState === 'pause') {
      action = 'pending';
    } else {
      console.error(`Invalid state: ${currentState}`);
      return;
    }

    try {
      const response = await fetch(`/api/queue/${itemId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      });

      if (response.ok) {
        const updatedQueue = queue.map(item => {
          if (item.id === itemId) {
            return { ...item, state: action === 'pause' ? 'pause' : 'pending' };
          }
          return item;
        });
  
        setQueue(updatedQueue);
      } else {
        console.error(`Failed to ${action} item ${itemId}`);
      }
    } catch (error) {
      console.error(`Error ${action} item ${itemId}:`, error);
    }
  };

  return (
    <div>
      <h1>Queue</h1>
      <QueueControlComponent 
        queue={queue}
        setQueue={setQueue}
        runFetch={runFetch}
        handleRunQueue={handleRunQueue}
      />

      {queue.length === 0 ? (
        <p className='error spacer'>Queue empty</p>
      ) : (
        <div className="grid-container">
          {queue.map((item) => (
            <QueueItem
              key={item.id}
              item={item}
              onDelete={handleDelete}
              onRunSingle={handleRunSingle}
              onPauseResume={handlePauseResume}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default QueueComponent;
