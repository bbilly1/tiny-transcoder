import React, { useState } from 'react';
import './DeleteQueueButton.css';

const DeleteQueueButton = ({runFetch, setIsDeleteVisible}) => {
  const [filter, setFilter] = useState('all');

  const handleDelete = async () => {
    let url = '/api/queue';
    if (filter !== 'all') {
      url += `?filter=${filter}`;
    }

    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        runFetch();
        setIsDeleteVisible(false);
      } else {
        console.error('Failed to delete queue');
      }
    } catch (error) {
      console.error('Error deleting queue:', error);
    }
  };

  return (
    <div className='delete-select'>
      <select
        id="deleteFilter"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      >
        <option value="all">All</option>
        <option value="pending">Pending</option>
        <option value="pause">Paused</option>
        <option value="completed">Completed</option>
      </select>
      <button className='error' onClick={handleDelete}>Delete {filter}</button>
    </div>
  );
};

export default DeleteQueueButton;
