import React from 'react';
import './DayView.css';
import TaskList from './TaskList';



const FixedView = () => {

    return (
        <div className="fixed-view">
            {Array.from({ length: 3 }).map((_, index) => (
                <div className="fixed-column" key = {"fixed"+index}>
                    <div className="day-view">
                        <div className="tasks">
                            <TaskList
                                key = {"fixed"+index}
                                dayInfo = {undefined}
                                taskListType="fixed"
                                column_id={index}
                            />
                        </div>
                    </div>
                </div>))
            }
        </div >
    );
};

export default FixedView;
