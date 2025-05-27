import React, { useState, useEffect } from 'react';
import WeekView from './components/WeekView';
import { TasksProvider } from './context/Tasks';
import LoginForm from './authorization/LoginForm';
import { logout } from './authorization/LoginProvider';
import ProfileIcon from './components/ProfileIcon';
import ArrowButton from './buttons/ArrowButton';
import StatsPage from './components/Stats';
import AssistantChat from './components/AssistantChat'; // 🔹 Импортируем чат
import './App.css';

const App = () => {
  const [sessionId, setSessionId] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [showAssistant, setShowAssistant] = useState(false); // 🔹 состояние чата

  useEffect(() => {
    const onPopState = () => setCurrentPath(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const formatMonth = (date) => {
    const options = { month: 'long', year: 'numeric' };
    let formattedDate = new Intl.DateTimeFormat('ru-RU', options).format(date);
    return formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
  };

  const handlePrevWeek = () => {
    setSelectedDate(prevDate => {
      const newDate = new Date(prevDate);
      newDate.setDate(prevDate.getDate() - 7);
      return newDate;
    });
  };

  const handleNextWeek = () => {
    setSelectedDate(prevDate => {
      const newDate = new Date(prevDate);
      newDate.setDate(prevDate.getDate() + 7);
      return newDate;
    });
  };

  const handleLogout = async () => {
    await logout();
    setSessionId(null);
    window.history.pushState({}, '', '/');
    setCurrentPath('/');
  };

  const goToStats = () => {
    window.history.pushState({}, '', '/stats');
    setCurrentPath('/stats');
  };

  if (currentPath === '/stats') {
    return (
      <TasksProvider>
        <div className="app">
          <ProfileIcon onLogout={handleLogout} goToStats={goToStats} />
          <StatsPage />
        </div>
      </TasksProvider>
    );
  }

  return (
    <TasksProvider>
      <div className="app">
        {sessionId ? (
          <>
            <div className="header">
              <ArrowButton onClick={handlePrevWeek} />
              <h1>{formatMonth(selectedDate)}</h1>
              <ArrowButton onClick={handleNextWeek} isReversed={true} />
              <ProfileIcon onLogout={handleLogout} goToStats={goToStats} />
            </div>

            <WeekView selectedDate={selectedDate} />

            {/* 🔹 Кнопка ассистента */}
            <button
              className="assistant-button"
              onClick={() => setShowAssistant(true)}
            >
              🤖 Ассистент
            </button>

            {/* 🔹 Компонент ассистента */}
            {showAssistant && <AssistantChat onClose={() => setShowAssistant(false)} />}
          </>
        ) : (
          <LoginForm setSessionId={setSessionId} />
        )}
      </div>
    </TasksProvider>
  );
};

export default App;
