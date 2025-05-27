import React, { useState } from 'react';
import './AssistantChat.css';

const AssistantChat = ({ onClose }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Привет! Чем могу помочь?' }
  ]);
  const [response, setResponse] = useState(null);

  const handleSend = () => {
    if (!input.trim()) return;

    // Добавим сообщение пользователя
    const newMessage = { role: 'user', text: input };
    setMessages([...messages, newMessage]);
    setInput('');

    // Мок GPT-ответа
    const mockResponse = `✅ Задачи созданы для утренних рутин с понедельника на вторник:\n- Подъём в 7:00\n- Зарядка\n- Завтрак\n- Планирование дня`;
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'assistant', text: mockResponse }]);
      setResponse(mockResponse);
    }, 500);
  };

  const handleApply = () => {
    alert('Задачи успешно применены (мок).');
    onClose();
  };

  return (
    <div className="assistant-chat-overlay">
      <div className="assistant-chat-panel">
        <div className="assistant-chat-header">
          <h3>🤖 Ассистент</h3>
          <button className="assistant-close" onClick={onClose}>×</button>
        </div>

        <div className="assistant-chat-body">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`assistant-message ${msg.role}`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <div className="assistant-chat-input">
          <input
            type="text"
            placeholder="Введите запрос..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
          />
          <button onClick={handleSend}>Отправить</button>
        </div>

        {response && (
          <div className="assistant-chat-apply">
            <button onClick={handleApply}>Применить</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssistantChat;
