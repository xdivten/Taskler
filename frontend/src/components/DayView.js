// DayView.js
import React, { useState } from 'react';
import './DayView.css';
import TaskList from './TaskList';

const DayView = ({ dayInfo }) => {
  const [completedTasks, setCompletedTasks] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);

  const handleTasksUpdate = (completed, total) => {
    setCompletedTasks(completed);
    setTotalTasks(total);
  };

  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;


  return (
    <div className="day-view">
      <div className={`day-header ${dayInfo.isCurrentDay ? 'current-day' : ''}`}>
        <span className="day-date">{dayInfo.shortDate}</span>
        <span className="day-name">{dayInfo.dayName}</span>
        {/* Прогресс бар */}
        <div className="progress-bar">
          <div className="progress" style={{ width: `${progress}%` }}></div>
        </div>
      </div>
      <div className="tasks">
        <TaskList
          dayInfo={dayInfo}
          taskListType="week"
          onTasksUpdate={handleTasksUpdate}
        />
      </div>
    </div>
  );
};

export default DayView;