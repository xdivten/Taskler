import { fetchCSRFToken } from '../lib/scrf';

const COMMON_URL = process.env.REACT_APP_API_URL;

export const login = async (email, password) => {
    const response = await fetch(COMMON_URL + '/_allauth/browser/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await fetchCSRFToken(),
        },
        credentials: 'include',
    });

    if (response.status === 200) {
        return 'success_login';
    }

    const json_body = await response.json();

    if (response.status === 401) {
        if (Array.isArray(json_body.data.flows)) {
            for (const flow of json_body.data.flows) {
                if (flow.id === 'verify_email') {
                    return 'need_login_verifcation';
                }
            }
        }
    }

    if (response.status === 409) {
        return 'conflict';
    }

    if (!response.ok) {
        throw new Error('Ошибка авторизации');
    }
};

export const checkSession = async () => {
    const response = await fetch(COMMON_URL + '/_allauth/browser/v1/auth/session', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await fetchCSRFToken(),
        },
        credentials: 'include',
    });

    if (response.status === 200) {
        return 'success_login';
    }
    const json_body = await response.json();

    if (response.status === 401) {
        if (Array.isArray(json_body.data.flows)) {
            for (const flow of json_body.data.flows) {
                if (flow.id === 'verify_email') {
                    return 'need_login_verifcation';
                }
            }
            return 'need_login_or_registration';
        }
    }

    if (response.status === 410) {
        return 'need_clear_session';
    }

    if (!response.ok) {
        throw new Error('Ошибка авторизации');
    }
};

export const logout = async () => {
    const response = await fetch(COMMON_URL + '/_allauth/browser/v1/auth/session', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await fetchCSRFToken(),
        },
        credentials: 'include',
    });

    if (response.status === 401) {
        return 'success_logout';
    }
};

export const signup = async (email, password) => {
    const response = await fetch(COMMON_URL + '/_allauth/browser/v1/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await fetchCSRFToken(),
        },
        credentials: 'include',
    });

    if (response.status === 200) {
        return 'success_login';
    }

    const json_body = await response.json();

    if (response.status === 401) {
        if (Array.isArray(json_body.data.flows)) {
            for (const flow of json_body.data.flows) {
                if (flow.id === 'verify_email') {
                    return 'need_login_verifcation';
                }
            }
        }
    }

    if (response.status === 409) {
        return 'conflict';
    }

    if (!response.ok) {
        throw new Error('Ошибка авторизации');
    }
};

export const sendCode = async (code) => {
    const response = await fetch(COMMON_URL + '/_allauth/browser/v1/auth/email/verify', {
        method: 'POST',
        body: JSON.stringify({  key: code }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await fetchCSRFToken(),
        },
        credentials: 'include',
    });

    if (response.status === 200) {
        return 'success_login';
    }

    const json_body = await response.json();
    if (response.status === 400) {
        return 'wrong_code'
    }
    if (response.status === 401) {
        if (Array.isArray(json_body.data.flows)) {
            for (const flow of json_body.data.flows) {
                if (flow.id === 'verify_email') {
                    return 'need_login_verifcation';
                }
            }
        }
    }

    if (response.status === 409) {
        return 'conflict';
    }

    if (!response.ok) {
        throw new Error('Ошибка авторизации');
    }
};
