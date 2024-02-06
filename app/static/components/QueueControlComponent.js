import React, {useState} from "react";
import './QueueControlComponent.css';
import QueueForm from "./QueueForm";
import DeleteQueueButton from "./DeleteQueueButton";

const QueueControlComponent = ({queue, setQueue, runFetch, handleRunQueue}) => {

  const [isAddFormVisible, setIsAddFormVisible] = useState(false);
  const [isDeleteVisible, setIsDeleteVisible] = useState(false);

  const handleToggleForm = () => {
    if (isDeleteVisible) setIsDeleteVisible(false);
    setIsAddFormVisible((prev) => !prev);
  };

  const handleToggleDelete = () => {
    if (isAddFormVisible) setIsAddFormVisible(false);
    setIsDeleteVisible((prev) => !prev);
  }

  const handleFormSubmit = (newItems) => {
    setQueue(queue.concat(newItems));
  };

  return (
    <>
      <div className="queue-control-wrap">
        <img
          src='/static/img/tt-icon-add.svg'
          alt='add to queue icon'
          title='Add to Queue'
          onClick={handleToggleForm}
          className={isAddFormVisible ? 'active' : ''}
        />
        {queue.length > 0 && (
          <>
            <img
              src='/static/img/tt-icon-play.svg'
              alt="start queue"
              title="Start Queue"
              onClick={handleRunQueue}
            />
            <img
              src='/static/img/tt-icon-delete.svg'
              alt='delete queue'
              title='Delete Queue'
              onClick={handleToggleDelete}
              className={isDeleteVisible ? 'active' : ''}
            />
          </>
        )}
      </div>
      <div>
        {isAddFormVisible && <QueueForm onFormSubmit={handleFormSubmit}/>}
        {isDeleteVisible && <DeleteQueueButton runFetch={runFetch} setIsDeleteVisible={setIsDeleteVisible}/>}
      </div>
    </>
  )
};

export default QueueControlComponent
