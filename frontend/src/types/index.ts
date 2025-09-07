// Type definitions for the mail service

export interface EmailRequest {
    to: string[];
    cc?: string[];
    bcc?: string[];
    subject: string;
    body: string;
    is_html?: boolean;
    attachments?: string[];
}

export interface EmailResponse {
    message_id: string;
    status: EmailStatus;
    to: string[];
    subject: string;
    sent_at?: string;
    error_message?: string;
}

export interface EmailHistory {
    message_id: string;
    status: EmailStatus;
    to: string[];
    cc?: string[];
    bcc?: string[];
    subject: string;
    body: string;
    is_html: boolean;
    sent_at?: string;
    error_message?: string;
    created_at: string;
}

export enum EmailStatus {
    PENDING = 'pending',
    SENT = 'sent',
    FAILED = 'failed',
    DELIVERED = 'delivered'
}

export interface HealthCheck {
    status: string;
    version: string;
    timestamp: string;
    kube_mail_connection: boolean;
}

export interface ApiError {
    detail: string;
}
