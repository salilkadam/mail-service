import React, { useState } from 'react';
import {
    Box,
    Paper,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
    Chip,
    FormControlLabel,
    Switch,
    Divider,
} from '@mui/material';
import { Send, Add, Delete } from '@mui/icons-material';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { EmailRequest, EmailStatus } from '../types';
import { mailApi } from '../services/api';

// Validation schema
const emailSchema = yup.object({
    to: yup.array().of(yup.string().email('Invalid email')).min(1, 'At least one recipient is required'),
    cc: yup.array().of(yup.string().email('Invalid email')).optional(),
    bcc: yup.array().of(yup.string().email('Invalid email')).optional(),
    subject: yup.string().required('Subject is required').min(1, 'Subject cannot be empty'),
    body: yup.string().required('Body is required').min(1, 'Body cannot be empty'),
    is_html: yup.boolean().optional(),
});

interface EmailFormProps {
    onEmailSent?: (response: any) => void;
}

const EmailForm: React.FC<EmailFormProps> = ({ onEmailSent }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const {
        control,
        handleSubmit,
        formState: { errors },
        reset,
        watch,
    } = useForm<EmailRequest>({
        resolver: yupResolver(emailSchema),
        defaultValues: {
            to: [''],
            cc: [],
            bcc: [],
            subject: '',
            body: '',
            is_html: false,
        },
    });

    const {
        fields: toFields,
        append: appendTo,
        remove: removeTo,
    } = useFieldArray({
        control,
        name: 'to',
    });

    const {
        fields: ccFields,
        append: appendCc,
        remove: removeCc,
    } = useFieldArray({
        control,
        name: 'cc',
    });

    const {
        fields: bccFields,
        append: appendBcc,
        remove: removeBcc,
    } = useFieldArray({
        control,
        name: 'bcc',
    });

    const isHtml = watch('is_html');

    const onSubmit = async (data: EmailRequest) => {
        setIsLoading(true);
        setMessage(null);

        try {
            // Filter out empty email addresses
            const filteredData = {
                ...data,
                to: data.to.filter(email => email.trim() !== ''),
                cc: data.cc?.filter(email => email.trim() !== '') || [],
                bcc: data.bcc?.filter(email => email.trim() !== '') || [],
            };

            const response = await mailApi.sendEmail(filteredData);

            if (response.status === EmailStatus.SENT) {
                setMessage({ type: 'success', text: 'Email sent successfully!' });
                reset();
                if (onEmailSent) {
                    onEmailSent(response);
                }
            } else {
                setMessage({ type: 'error', text: `Failed to send email: ${response.error_message}` });
            }
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Failed to send email';
            setMessage({ type: 'error', text: errorMessage });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
            <Typography variant="h4" component="h1" gutterBottom align="center">
                Send Email
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" align="center" gutterBottom>
                From: info@bionicaisolutions.com
            </Typography>

            {message && (
                <Alert severity={message.type} sx={{ mb: 2 }}>
                    {message.text}
                </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
                {/* Recipients */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Recipients (To)
                    </Typography>
                    {toFields.map((field, index) => (
                        <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                            <Controller
                                name={`to.${index}`}
                                control={control}
                                render={({ field }) => (
                                    <TextField
                                        {...field}
                                        fullWidth
                                        type="email"
                                        placeholder="recipient@example.com"
                                        error={!!errors.to?.[index]}
                                        helperText={errors.to?.[index]?.message}
                                    />
                                )}
                            />
                            {toFields.length > 1 && (
                                <Button
                                    variant="outlined"
                                    color="error"
                                    onClick={() => removeTo(index)}
                                    startIcon={<Delete />}
                                >
                                    Remove
                                </Button>
                            )}
                        </Box>
                    ))}
                    <Button
                        variant="outlined"
                        onClick={() => appendTo('')}
                        startIcon={<Add />}
                        sx={{ mt: 1 }}
                    >
                        Add Recipient
                    </Button>
                </Box>

                {/* CC Recipients */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        CC (Optional)
                    </Typography>
                    {ccFields.map((field, index) => (
                        <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                            <Controller
                                name={`cc.${index}`}
                                control={control}
                                render={({ field }) => (
                                    <TextField
                                        {...field}
                                        fullWidth
                                        type="email"
                                        placeholder="cc@example.com"
                                        error={!!errors.cc?.[index]}
                                        helperText={errors.cc?.[index]?.message}
                                    />
                                )}
                            />
                            <Button
                                variant="outlined"
                                color="error"
                                onClick={() => removeCc(index)}
                                startIcon={<Delete />}
                            >
                                Remove
                            </Button>
                        </Box>
                    ))}
                    <Button
                        variant="outlined"
                        onClick={() => appendCc('')}
                        startIcon={<Add />}
                        sx={{ mt: 1 }}
                    >
                        Add CC
                    </Button>
                </Box>

                {/* BCC Recipients */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        BCC (Optional)
                    </Typography>
                    {bccFields.map((field, index) => (
                        <Box key={field.id} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                            <Controller
                                name={`bcc.${index}`}
                                control={control}
                                render={({ field }) => (
                                    <TextField
                                        {...field}
                                        fullWidth
                                        type="email"
                                        placeholder="bcc@example.com"
                                        error={!!errors.bcc?.[index]}
                                        helperText={errors.bcc?.[index]?.message}
                                    />
                                )}
                            />
                            <Button
                                variant="outlined"
                                color="error"
                                onClick={() => removeBcc(index)}
                                startIcon={<Delete />}
                            >
                                Remove
                            </Button>
                        </Box>
                    ))}
                    <Button
                        variant="outlined"
                        onClick={() => appendBcc('')}
                        startIcon={<Add />}
                        sx={{ mt: 1 }}
                    >
                        Add BCC
                    </Button>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Subject */}
                <Controller
                    name="subject"
                    control={control}
                    render={({ field }) => (
                        <TextField
                            {...field}
                            fullWidth
                            label="Subject"
                            error={!!errors.subject}
                            helperText={errors.subject?.message}
                            sx={{ mb: 3 }}
                        />
                    )}
                />

                {/* HTML Toggle */}
                <Controller
                    name="is_html"
                    control={control}
                    render={({ field }) => (
                        <FormControlLabel
                            control={<Switch {...field} checked={field.value} />}
                            label="HTML Content"
                            sx={{ mb: 2 }}
                        />
                    )}
                />

                {/* Body */}
                <Controller
                    name="body"
                    control={control}
                    render={({ field }) => (
                        <TextField
                            {...field}
                            fullWidth
                            multiline
                            rows={isHtml ? 10 : 6}
                            label={isHtml ? "HTML Body" : "Message Body"}
                            error={!!errors.body}
                            helperText={errors.body?.message}
                            sx={{ mb: 3 }}
                        />
                    )}
                />

                {/* Submit Button */}
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                    <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        startIcon={isLoading ? <CircularProgress size={20} /> : <Send />}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Sending...' : 'Send Email'}
                    </Button>
                    <Button
                        type="button"
                        variant="outlined"
                        size="large"
                        onClick={() => reset()}
                        disabled={isLoading}
                    >
                        Clear Form
                    </Button>
                </Box>
            </Box>
        </Paper>
    );
};

export default EmailForm;
