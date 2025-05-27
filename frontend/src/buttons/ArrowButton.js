import React from "react";
import './ArrowButton.css';

function ArrowButton({ onClick, isReversed }) {
    const handleClick = () => {
        onClick();
    };

    return (
        <button
            className="arrow-button"
            onClick={handleClick}
        >
            {/* Условный рендеринг SVG в зависимости от направления */}
            {isReversed ? (
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 20"><path d="M7.293 4.707 14.586 12l-7.293 7.293 1.414 1.414L17.414 12 8.707 3.293 7.293 4.707z" stroke="#142ED8" stroke-width="0.1" /></svg>
            ) : (
                <svg xmlns="http://www.w3.org/2000/svg"  width="40" height="40" viewBox="0 0 24 20">
                    <path d="M16.707 19.293 9.414 12l7.293-7.293-1.414-1.414L6.586 12l8.707 8.707 1.414-1.414z" stroke="#142ED8" stroke-width="0.1" />
                </svg>
            )}
        </button>
    );
}

export default ArrowButton;