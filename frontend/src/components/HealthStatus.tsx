import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip,
    IconButton,
    Alert,
    CircularProgress,
} from '@mui/material';
import { Refresh, CheckCircle, Error, Warning } from '@mui/icons-material';
import { HealthCheck } from '../types';
import { mailApi } from '../services/api';

const HealthStatus: React.FC = () => {
    const [health, setHealth] = useState<HealthCheck | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchHealthStatus = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const healthData = await mailApi.getHealthCheck();
            setHealth(healthData);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to fetch health status');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchHealthStatus();
    }, []);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'healthy':
                return <CheckCircle color="success" />;
            case 'degraded':
                return <Warning color="warning" />;
            case 'unhealthy':
                return <Error color="error" />;
            default:
                return <Error color="error" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy':
                return 'success';
            case 'degraded':
                return 'warning';
            case 'unhealthy':
                return 'error';
            default:
                return 'error';
        }
    };

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString();
    };

    return (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" component="h2">
                    Service Health
                </Typography>
                <IconButton onClick={fetchHealthStatus} disabled={isLoading}>
                    <Refresh />
                </IconButton>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                    <CircularProgress size={24} />
                </Box>
            ) : health ? (
                <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        {getStatusIcon(health.status)}
                        <Chip
                            label={health.status.toUpperCase()}
                            color={getStatusColor(health.status) as any}
                            size="medium"
                        />
                        <Typography variant="body2" color="text.secondary">
                            Version: {health.version}
                        </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" color="text.secondary">
                            kube-mail Connection:
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            {health.kube_mail_connection ? (
                                <CheckCircle color="success" fontSize="small" />
                            ) : (
                                <Error color="error" fontSize="small" />
                            )}
                            <Typography variant="body2">
                                {health.kube_mail_connection ? 'Connected' : 'Disconnected'}
                            </Typography>
                        </Box>
                    </Box>

                    <Box>
                        <Typography variant="subtitle2" color="text.secondary">
                            Last Checked:
                        </Typography>
                        <Typography variant="body2">
                            {formatTimestamp(health.timestamp)}
                        </Typography>
                    </Box>

                    {health.status === 'degraded' && (
                        <Alert severity="warning" sx={{ mt: 2 }}>
                            Service is running but kube-mail connection is not available. Emails may not be sent.
                        </Alert>
                    )}

                    {health.status === 'unhealthy' && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                            Service is not healthy. Please check the configuration and try again.
                        </Alert>
                    )}
                </Box>
            ) : (
                <Typography variant="body2" color="text.secondary">
                    No health data available
                </Typography>
            )}
        </Paper>
    );
};

export default HealthStatus;
