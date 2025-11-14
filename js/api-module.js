/**
 * API Module - Handles HTTP requests to backend
 */

const APIModule = (() => {
    const baseURL = 'http://localhost:5000/api';

    const handleError = (error, endpoint) => {
        console.error(`[APIModule] Error on ${endpoint}:`, error);
        UIModule.showNotification(`API Error: ${error.message}`, 'error');
        throw error;
    };

    const get = async (endpoint) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            handleError(error, `GET ${endpoint}`);
        }
    };

    const post = async (endpoint, data = {}) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            handleError(error, `POST ${endpoint}`);
        }
    };

    const put = async (endpoint, data = {}) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            handleError(error, `PUT ${endpoint}`);
        }
    };

    const delete_ = async (endpoint) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            handleError(error, `DELETE ${endpoint}`);
        }
    };

    return {
        baseURL,
        get,
        post,
        put,
        delete: delete_
    };
})();
