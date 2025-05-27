import React, { useState } from 'react';
import './ColorPicker.css';

function ColorPicker({color, onColorChange }) {
  const [selectedColor, setSelectedColor] = useState(color);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Предустановленные цвета
  const colorOptions = ['#FF5733', '#33FF57', '#3357FF', '#F1C40F', '#9B59B6', '#1ABC9C'];

  const handleButtonClick = () => {
    setIsModalOpen(true);
  };

  const handleColorSelect = (color) => {
    setSelectedColor(color);
    onColorChange(color); // Передаем выбранный цвет родительскому компоненту
    setIsModalOpen(false); // Закрываем окно после выбора цвета
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="color-picker">
      <button
        style={{ backgroundColor: selectedColor || '#ccc' }}
        onClick={handleButtonClick}
      >
      </button>

      {/* Модальное окно с выбором цвета */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="color-options">
              {colorOptions.map((color, index) => (
                <button
                  key={index}
                  style={{ backgroundColor: color }}
                  onClick={() => handleColorSelect(color)}
                  className="color-option"
                ></button>
              ))}
            </div>
            <div className="modal-actions">
              <button type="button" onClick={handleModalClose}>Закрыть</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ColorPicker;
