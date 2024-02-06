// QueueFetch.js

export const fetchQueueData = async (setQueue) => {
  try {
    const response = await fetch('/api/queue');
    if (response.ok) {
      const data = await response.json();
      const formattedData = data.map(formatDates);
      setQueue(formattedData);
    } else {
      console.error('Error fetching data:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

const formatDates = (item) => {
  return {
    ...item,
    date_added: formatDate(item.date_added),
    date_started: item.date_started ? formatDate(item.date_started) : null,
    date_completed: item.date_completed ? formatDate(item.date_completed) : null,
  };
};

const formatDate = (isoDate) => {
  const date = new Date(isoDate);
  return date.toLocaleString();
};
