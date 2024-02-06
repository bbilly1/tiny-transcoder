// fetch progress

import { fetchQueueData } from "./QueueFetch";

export const fetchProgressData = async (setProgress, setQueue, timeout = 3000) => {
  try {
    const response = await fetch('/api/progress');
    if (response.ok) {
      let result;
      const text = await response.text();
      if (text) {
        result = JSON.parse(text);
      }

      if (result) {
        let newId = result.id;
        if (newId !== lastId) {
          lastId = newId;
          fetchQueueData(setQueue);
        }
        setTimeout(() => fetchProgressData(setProgress, setQueue, timeout), timeout);
      } else {
        fetchQueueData(setQueue);
      }

      setProgress(result);

      return result;
    } else {
      console.error('Failed to fetch progress data');
      return null;
    }
  } catch (error) {
    console.error('Error fetching progress data:', error);
    return null;
  }
};

let lastId;
