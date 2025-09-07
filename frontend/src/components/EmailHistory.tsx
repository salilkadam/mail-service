import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Alert,
    CircularProgress,
    Pagination,
} from '@mui/material';
import { Visibility, Refresh } from '@mui/icons-material';
import { EmailHistory as EmailHistoryType, EmailStatus } from '../types';
import { mailApi } from '../services/api';

interface EmailHistoryProps {
    refreshTrigger?: number;
}

const EmailHistory: React.FC<EmailHistoryProps> = ({ refreshTrigger }) => {
    const [emails, setEmails] = useState<EmailHistoryType[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedEmail, setSelectedEmail] = useState<EmailHistoryType | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const itemsPerPage = 10;

    const fetchEmailHistory = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const history = await mailApi.getEmailHistory(100); // Get more items for pagination
            setEmails(history);
            setTotalPages(Math.ceil(history.length / itemsPerPage));
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to fetch email history');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchEmailHistory();
    }, [refreshTrigger]);

    const getStatusColor = (status: EmailStatus) => {
        switch (status) {
            case EmailStatus.SENT:
                return 'success';
            case EmailStatus.DELIVERED:
                return 'info';
            case EmailStatus.FAILED:
                return 'error';
            case EmailStatus.PENDING:
                return 'warning';
            default:
                return 'default';
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString();
    };

    const handleViewEmail = async (messageId: string) => {
        try {
            const email = await mailApi.getEmailById(messageId);
            setSelectedEmail(email);
            setIsDialogOpen(true);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to fetch email details');
        }
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
        setSelectedEmail(null);
    };

    const paginatedEmails = emails.slice((page - 1) * itemsPerPage, page * itemsPerPage);

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Email History
                </Typography>
                <IconButton onClick={fetchEmailHistory} disabled={isLoading}>
                    <Refresh />
                </IconButton>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Status</TableCell>
                                    <TableCell>To</TableCell>
                                    <TableCell>Subject</TableCell>
                                    <TableCell>Sent At</TableCell>
                                    <TableCell>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {paginatedEmails.map((email) => (
                                    <TableRow key={email.message_id}>
                                        <TableCell>
                                            <Chip
                                                label={email.status}
                                                color={getStatusColor(email.status) as any}
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            {email.to.join(', ')}
                                            {email.cc && email.cc.length > 0 && (
                                                <Typography variant="caption" display="block" color="text.secondary">
                                                    CC: {email.cc.join(', ')}
                                                </Typography>
                                            )}
                                            {email.bcc && email.bcc.length > 0 && (
                                                <Typography variant="caption" display="block" color="text.secondary">
                                                    BCC: {email.bcc.join(', ')}
                                                </Typography>
                                            )}
                                        </TableCell>
                                        <TableCell>{email.subject}</TableCell>
                                        <TableCell>
                                            {email.sent_at ? formatDate(email.sent_at) : 'Not sent'}
                                        </TableCell>
                                        <TableCell>
                                            <IconButton
                                                onClick={() => handleViewEmail(email.message_id)}
                                                size="small"
                                            >
                                                <Visibility />
                                            </IconButton>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>

                    {totalPages > 1 && (
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                            <Pagination
                                count={totalPages}
                                page={page}
                                onChange={(_, newPage) => setPage(newPage)}
                                color="primary"
                            />
                        </Box>
                    )}

                    {emails.length === 0 && (
                        <Typography variant="body1" color="text.secondary" align="center" sx={{ p: 3 }}>
                            No emails found. Send your first email to see it here!
                        </Typography>
                    )}
                </>
            )}

            {/* Email Details Dialog */}
            <Dialog
                open={isDialogOpen}
                onClose={handleCloseDialog}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>Email Details</DialogTitle>
                <DialogContent>
                    {selectedEmail && (
                        <Box>
                            <Typography variant="h6" gutterBottom>
                                Message ID: {selectedEmail.message_id}
                            </Typography>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Status:
                                </Typography>
                                <Chip
                                    label={selectedEmail.status}
                                    color={getStatusColor(selectedEmail.status) as any}
                                    size="small"
                                />
                            </Box>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    To:
                                </Typography>
                                <Typography variant="body2">{selectedEmail.to.join(', ')}</Typography>
                            </Box>

                            {selectedEmail.cc && selectedEmail.cc.length > 0 && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        CC:
                                    </Typography>
                                    <Typography variant="body2">{selectedEmail.cc.join(', ')}</Typography>
                                </Box>
                            )}

                            {selectedEmail.bcc && selectedEmail.bcc.length > 0 && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        BCC:
                                    </Typography>
                                    <Typography variant="body2">{selectedEmail.bcc.join(', ')}</Typography>
                                </Box>
                            )}

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Subject:
                                </Typography>
                                <Typography variant="body2">{selectedEmail.subject}</Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Content Type:
                                </Typography>
                                <Typography variant="body2">
                                    {selectedEmail.is_html ? 'HTML' : 'Plain Text'}
                                </Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Body:
                                </Typography>
                                <Box
                                    sx={{
                                        p: 2,
                                        border: '1px solid #e0e0e0',
                                        borderRadius: 1,
                                        bgcolor: '#f5f5f5',
                                        maxHeight: 300,
                                        overflow: 'auto',
                                    }}
                                >
                                    {selectedEmail.is_html ? (
                                        <div dangerouslySetInnerHTML={{ __html: selectedEmail.body }} />
                                    ) : (
                                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                            {selectedEmail.body}
                                        </Typography>
                                    )}
                                </Box>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Created At:
                                </Typography>
                                <Typography variant="body2">{formatDate(selectedEmail.created_at)}</Typography>
                            </Box>

                            {selectedEmail.sent_at && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        Sent At:
                                    </Typography>
                                    <Typography variant="body2">{formatDate(selectedEmail.sent_at)}</Typography>
                                </Box>
                            )}

                            {selectedEmail.error_message && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        Error Message:
                                    </Typography>
                                    <Alert severity="error" sx={{ mt: 1 }}>
                                        {selectedEmail.error_message}
                                    </Alert>
                                </Box>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Close</Button>
                </DialogActions>
            </Dialog>
        </Paper>
    );
};

export default EmailHistory;
