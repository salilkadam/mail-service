// API service for communicating with the backend

import axios, { AxiosResponse } from 'axios';
import { EmailRequest, EmailResponse, EmailHistory, HealthCheck, ApiError } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response) {
            // Server responded with error status
            console.error('API Error:', error.response.data);
        } else if (error.request) {
            // Request was made but no response received
            console.error('Network Error:', error.message);
        } else {
            // Something else happened
            console.error('Error:', error.message);
        }
        return Promise.reject(error);
    }
);

export const mailApi = {
    // Send email
    sendEmail: async (emailRequest: EmailRequest): Promise<EmailResponse> => {
        const response: AxiosResponse<EmailResponse> = await api.post('/send', emailRequest);
        return response.data;
    },

    // Get email history
    getEmailHistory: async (limit: number = 50): Promise<EmailHistory[]> => {
        const response: AxiosResponse<EmailHistory[]> = await api.get(`/history?limit=${limit}`);
        return response.data;
    },

    // Get email by ID
    getEmailById: async (messageId: string): Promise<EmailHistory> => {
        const response: AxiosResponse<EmailHistory> = await api.get(`/history/${messageId}`);
        return response.data;
    },

    // Health check
    getHealthCheck: async (): Promise<HealthCheck> => {
        const response: AxiosResponse<HealthCheck> = await api.get('/health');
        return response.data;
    },
};

export default api;
