import React, { useState } from 'react';

const QueueForm = ({ onFormSubmit }) => {
  const [path, setPath] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('/api/queue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path }),
      });

      if (response.status === 400) {
        const data = await response.json();
        setError(`${data.message || 'N/A'})`);
      }

      if (response.ok) {
        const data = await response.json();
        setPath('');
        onFormSubmit(data);
        setError(null);
      }

    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div className='button-group'>
      <form className='add-form' onSubmit={handleSubmit}>
        <label>
          <input
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder='path to folder or file...'
          />
        </label>
        <button type="submit">Add</button>
      </form>
      {error && (
        <div className="error">
          {error}
        </div>
      )}
    </div>
  );
};

export default QueueForm;
