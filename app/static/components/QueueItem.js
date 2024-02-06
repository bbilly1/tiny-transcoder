import React, { useState } from 'react';

const formatDate = (dateString) => {
  const dateObject = new Date(dateString);
  const currentDate = new Date();

  const isSameDay =
    dateObject.getDate() === currentDate.getDate() &&
    dateObject.getMonth() === currentDate.getMonth() &&
    dateObject.getFullYear() === currentDate.getFullYear();

  const options = isSameDay
    ? { hour: 'numeric', minute: 'numeric', second: 'numeric' }
    : { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };

  const formattedDate = dateObject.toLocaleString(undefined, options);
  return formattedDate;
};

const formatDuration = (durationInSeconds) => {
  const hours = Math.floor(durationInSeconds / 3600);
  const minutes = Math.floor((durationInSeconds % 3600) / 60);
  const seconds = durationInSeconds % 60;

  let formattedDuration = '';

  if (hours > 0) {
    formattedDuration += `${hours}h `;
  }

  if (minutes > 0 || hours > 0) {
    formattedDuration += `${minutes}m `;
  }

  formattedDuration += `${seconds}s`;

  return formattedDuration.trim();
};

const QueueItem = ({ item, onDelete, onRunSingle, onPauseResume }) => {
  const [isConfirming, setIsConfirming] = useState(false);

  const handleDeleteClick = () => {
    setIsConfirming(true);
  };

  const handleConfirmDelete = () => {
    onDelete(item.id);
  };

  const handleCancelDelete = () => {
    setIsConfirming(false);
  };

  const calculateReductionPercentage = () => {
    if (item.dest_size && item.source_size) {
      const sourceSize = parseFloat(item.source_size);
      const destSize = parseFloat(item.dest_size);
      const reductionPercentage = ((sourceSize - destSize) / sourceSize) * 100;
      const className = sourceSize < destSize ? 'error' : '';

      return <span className={className}>{`-${Math.abs(reductionPercentage).toFixed(2)}%`}</span>;
    }
    return null;
  };

  return (
    <div className={`grid-item ${item.state}`}>
      <p className='smaller'>ID: {item.id}</p>
      <h2>{item.source_name}</h2>
      <p>
        <span className='highlight'>{item.duration}</span>s |
        <span className='highlight'> {item.source_size}</span>MB {item.dest_size &&
          <>
            to <span className='highlight'>{item.dest_size}</span>MB
            ({calculateReductionPercentage()})
          </>
        }
      </p>
      <p>State: {item.state}</p>
      <p>Added: {formatDate(item.date_added)}</p>
      <p>
        {item.date_started && <span>Processing: {formatDate(item.date_started)}</span>}
        {item.date_completed && <span> - {formatDate(item.date_completed)}</span>}
        {item.date_started && item.date_completed && (
          <span> | {formatDuration((new Date(item.date_completed) - new Date(item.date_started)) / 1000)}</span>
        )}
      </p>
      <div className='button-group'>
      {!isConfirming && <button onClick={handleDeleteClick}>Delete</button>}
        {!isConfirming && item.state !== 'completed' && item.state !== 'transcoding' && (
          <button onClick={() => onRunSingle(item.id)}>Run</button>
        )}
        {!isConfirming && item.state === 'pending' && (
          <button onClick={() => onPauseResume(item.id, item.state)}>Pause</button>
        )}
        {!isConfirming && item.state === 'pause' && (
          <button onClick={() => onPauseResume(item.id, item.state)}>Resume</button>
        )}
        {isConfirming && (
          <>
            <button className='error' onClick={handleConfirmDelete}>Confirm</button>
            <button onClick={handleCancelDelete}>Cancel</button>
          </>
        )}
      </div>
    </div>
  );
};

export default QueueItem;
