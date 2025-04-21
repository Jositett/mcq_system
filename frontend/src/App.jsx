import React, { useMemo, useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline, IconButton, AppBar, Toolbar, Typography, Button, useMediaQuery } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { getTheme } from './theme';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import RequireAuth from './pages/RequireAuth';
import LandingPage from './pages/LandingPage';
import { setAuthToken } from './api';
import { ToastProvider, useToast } from './components/ToastContext';

function AppContent() {
  const showToast = useToast();
  // Theme
  const getInitialMode = () => {
    const saved = localStorage.getItem('themeMode');
    return saved === 'dark' ? 'dark' : 'light';
  };
  const [mode, setMode] = useState(getInitialMode);
  useEffect(() => { localStorage.setItem('themeMode', mode); }, [mode]);
  const theme = useMemo(() => getTheme(mode), [mode]);

  // Auth
  const getInitialAuth = () => {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    if (token) setAuthToken(token);
    return { token, user: user ? JSON.parse(user) : null };
  };
  const [auth, setAuth] = useState(getInitialAuth);

  const handleLogin = (token, userData) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setAuth({ token, user: userData });
    setAuthToken(token);
    showToast('Login successful!', 'success');
  };
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setAuth({ token: null, user: null });
    setAuthToken(null);
    showToast('Logged out.', 'info');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar position="static" color="default" elevation={1}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              <Button component={Link} to="/" color="inherit">MCQ System</Button>
            </Typography>
            {auth.user ? (
              <>
                <Typography sx={{ mr: 2 }}>{auth.user.full_name || auth.user.username}</Typography>
                <Button color="inherit" onClick={handleLogout}>Logout</Button>
              </>
            ) : (
              <>
                <Button component={Link} to="/login" color="inherit">Login</Button>
                <Button component={Link} to="/register" color="inherit">Register</Button>
              </>
            )}
            <IconButton onClick={() => setMode(mode === 'light' ? 'dark' : 'light')} color="inherit" sx={{ ml: 1 }}>
              {mode === 'light' ? <Brightness4Icon /> : <Brightness7Icon />}
            </IconButton>
          </Toolbar>
        </AppBar>
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register onRegister={() => showToast('Registration successful! Please log in.', 'success')} />} />
          <Route
            path="/"
            element={
              auth.user ? (
                <RequireAuth user={auth.user}>
                  {auth.user?.role === 'student' && <Dashboard user={auth.user} />}
                  {auth.user?.role === 'instructor' && <InstructorDashboard user={auth.user} />}
                  {auth.user?.role === 'admin' && <AdminDashboard user={auth.user} />}
                  {!['student', 'instructor', 'admin'].includes(auth.user?.role) && (
                    <LandingPage />
                  )}
                </RequireAuth>
              ) : (
                <LandingPage />
              )
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App;
