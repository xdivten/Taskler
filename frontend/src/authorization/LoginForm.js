import React, { useState, useEffect } from 'react';
import { login, checkSession, signup, sendCode } from './LoginProvider';
import './LoginForm.css';

const LoginForm = ({ setSessionId }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [showVerificationModal, setShowVerificationModal] = useState(false);
    const [verificationCode, setVerificationCode] = useState('');

    const handleLoginProviderCode = async (code) => {
        if (code === 'success_login') {
            setSessionId("hello");
            return;
        }
        if (code === 'need_login_or_registration') {
            return;
        }
        if (code === 'need_login_verifcation') {
            setShowVerificationModal(true);
            return;
        }
        if (code === 'conflict') {
            await handleCheckSession();
            return;
        }
        if (code === 'need_clear_session') {
            return;
        }
        if (code === 'wrong_code') {
            alert('Неверный код!');
        }
    };

    const handleCheckSession = async () => {
        try {
            let result_code = await checkSession();
            await handleLoginProviderCode(result_code);
        } catch (error) {
            console.error('Ошибка авторизации:', error);
            alert('Ошибка входа.');
        }
    };

    useEffect(() => {
        handleCheckSession();
    }, []);

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            let result_code = await login(email, password);
            await handleLoginProviderCode(result_code);
        } catch (error) {
            console.error('Ошибка авторизации:', error);
            alert('Ошибка входа.');
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            alert('Пароли не совпадают!');
            return;
        }
        try {
            let result_code = await signup(email, password);
            await handleLoginProviderCode(result_code);
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            alert('Ошибка регистрации.');
        }
    };

    const handleVerificationSubmit = async (e) => {
        e.preventDefault();
        try {
            let result_code = await sendCode(verificationCode);
            await handleLoginProviderCode(result_code);
        } catch (error) {
            console.error('Ошибка подтверждения:', error);
            alert('Неправильный код подтверждения.');
        }
    };

    return (
        <div className="auth-container" >
            <header className="auth-header">
                <h1>Taskler</h1>
                <h3>Планнер-ежедневник для решения ваших задач</h3>
            </header>
            <main className="auth-main">
                {isRegistering ? (
                    <form onSubmit={handleRegister} className="auth-form">
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="auth-input"
                            required
                        />
                        <input
                            type="password"
                            placeholder="Пароль"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="auth-input"
                            required
                        />
                        <input
                            type="password"
                            placeholder="Подтвердите пароль"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="auth-input"
                            required
                        />
                        <button type="submit" className="auth-button">Зарегистрироваться</button>
                        <button
                            type="button"
                            onClick={() => setIsRegistering(false)}
                            className="auth-switch-button"
                        >
                            У меня уже есть аккаунт
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleLogin} className="auth-form">
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="auth-input"
                            required
                        />
                        <input
                            type="password"
                            placeholder="Пароль"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="auth-input"
                            required
                        />
                        <button type="submit" className="auth-button">Войти</button>
                        <button
                            type="button"
                            onClick={() => setIsRegistering(true)}
                            className="auth-switch-button"
                        >
                            Зарегистрироваться
                        </button>
                    </form>
                )}
            </main>
            {showVerificationModal && (
                <div className="auth-modal-overlay">
                    <div className="auth-modal">
                        <h2>Введите код подтверждения</h2>
                        <form onSubmit={handleVerificationSubmit} className="auth-modal-form">
                            <input
                                type="text"
                                placeholder="Код"
                                value={verificationCode}
                                onChange={(e) => setVerificationCode(e.target.value)}
                                className="auth-input"
                                required
                            />
                            <button type="submit" className="auth-button">Подтвердить</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoginForm;