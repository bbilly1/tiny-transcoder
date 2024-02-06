// ProgressMessage.js
import React, { useEffect, useState } from 'react';
import './ProgressMessage.css';
import { fetchProgressData } from './ProgressFetch';

const ProgressMessage = ({ progress, setProgress, setQueue }) => {
  const [eta, setETA] = useState(null);
  const [expectedFinishTime, setExpectedFinishTime] = useState(null);
  const [estimatedFinalSize, setEstimatedFinalSize] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      await fetchProgressData(setProgress, setQueue);
    };

    fetchData();

    return () => {
      clearTimeout(fetchData);
    };
  }, [setQueue]);

  useEffect(() => {
    if (progress && progress.percent > 0.03 && progress.speed !== undefined && progress.percent !== undefined && progress.duration !== undefined && progress.transcode_size !== undefined && progress.source_size !== undefined) {
      const calculatedETA = (progress.duration * (1 - progress.percent)) / progress.speed;
      setETA(calculatedETA);
  
      const nowInSeconds = Date.now() / 1000;
      const etaInSeconds = nowInSeconds + calculatedETA;
      setExpectedFinishTime(new Date(etaInSeconds * 1000));
  
      const estimatedFinalSize = (progress.transcode_size / progress.percent);
      setEstimatedFinalSize(estimatedFinalSize);
    } else {
      setETA(null);
      setExpectedFinishTime(null);
      setEstimatedFinalSize(null);
    }
  }, [progress]);

  const isInitialMessage = progress && progress.message === 'Queue started';

  return isInitialMessage ? (
    <div>
      <h2>Progress Message</h2>
      <div>
        <p>{progress.message}</p>
      </div>
    </div>
  ) : progress ? (
    <div className='spacer'>
      <div>
        <p className='boxed-content'>{progress.name}<br></br>
          {eta !== null && progress.percent > 0.03 && (
            <>
              <span>ETA: {formatETA(eta)} at {expectedFinishTime.toLocaleTimeString()}</span>
              <span> - Final Size: {formatSize(estimatedFinalSize)}</span>
            </>
          )}
        </p>
        <div className="progress-bar">
          <div className='progress-text'>
            <span>{(progress.percent * 100).toFixed(1)}% | {progress.fps}fps | {progress.speed}x speed</span>
          </div>
          <div
            className="progress-fill"
            style={{ width: `${progress.percent * 100}%` }}
          />
        </div>
      </div>
    </div>
  ) : null;
};

const formatETA = (etaInSeconds) => {
  const hours = Math.floor(etaInSeconds / 3600);
  const minutes = Math.floor((etaInSeconds % 3600) / 60);
  const seconds = Math.floor(etaInSeconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`;
  } else {
    return `${minutes}m ${seconds}s`;
  }
};

const formatSize = (sizeInBytes) => {
  const kilobytes = sizeInBytes / 1024;
  const megabytes = kilobytes / 1024;
  const gigabytes = megabytes / 1024;

  if (gigabytes >= 1) {
    return `${gigabytes.toFixed(2)} GB`;
  } else if (megabytes >= 1) {
    return `${megabytes.toFixed(2)} MB`;
  } else {
    return `${kilobytes.toFixed(2)} KB`;
  }
};

export default ProgressMessage;
