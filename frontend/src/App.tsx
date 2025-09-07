import React, { useState } from 'react';
import {
    ThemeProvider,
    createTheme,
    CssBaseline,
    Container,
    AppBar,
    Toolbar,
    Typography,
    Tabs,
    Tab,
    Box,
} from '@mui/material';
import { Email, History, Health } from '@mui/icons-material';
import EmailForm from './components/EmailForm';
import EmailHistory from './components/EmailHistory';
import HealthStatus from './components/HealthStatus';

// Create theme
const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
    },
});

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
}

function App() {
    const [tabValue, setTabValue] = useState(0);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    const handleEmailSent = () => {
        setRefreshTrigger(prev => prev + 1);
        setTabValue(1); // Switch to history tab
    };

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppBar position="static">
                <Toolbar>
                    <Email sx={{ mr: 2 }} />
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Mail Service
                    </Typography>
                    <Typography variant="body2">
                        From: info@bionicaisolutions.com
                    </Typography>
                </Toolbar>
            </AppBar>

            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="mail service tabs">
                        <Tab icon={<Email />} label="Send Email" />
                        <Tab icon={<History />} label="Email History" />
                        <Tab icon={<Health />} label="Health Status" />
                    </Tabs>
                </Box>

                <TabPanel value={tabValue} index={0}>
                    <EmailForm onEmailSent={handleEmailSent} />
                </TabPanel>

                <TabPanel value={tabValue} index={1}>
                    <EmailHistory refreshTrigger={refreshTrigger} />
                </TabPanel>

                <TabPanel value={tabValue} index={2}>
                    <HealthStatus />
                </TabPanel>
            </Container>
        </ThemeProvider>
    );
}

export default App;
