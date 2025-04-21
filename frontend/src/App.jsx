import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import RequireAuth from './pages/RequireAuth';
import LandingPage from './pages/LandingPage';
import Profile from './pages/Profile';
import Notifications from './pages/Notifications';
import FaceCheckinPage from './pages/FaceCheckinPage';
import AdminBulkActions from './pages/AdminBulkActions';
import InstructorBulkActions from './pages/InstructorBulkActions';

// Components
import Navbar from './components/Navbar';
import { ToastProvider, useToast } from './components/ToastContext';

// Redux actions
import { fetchUserProfile } from './features/authSlice';

function AppContent() {
  const dispatch = useDispatch();
  const showToast = useToast();
  
  // Get auth state from Redux
  const { isAuthenticated, user, role } = useSelector(state => state.auth);
  
  // Get theme from Redux
  const { theme } = useSelector(state => state.theme);
  
  // Fetch user profile on app load if authenticated
  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchUserProfile())
        .unwrap()
        .catch(error => {
          showToast(error.message || 'Failed to load profile', 'error');
        });
    }
  }, [isAuthenticated, dispatch, showToast]);

  return (
    <Router>
      <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-200`}>
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} />
            <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />} />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
            <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
            <Route path="/notifications" element={<RequireAuth><Notifications /></RequireAuth>} />
            <Route path="/attendance/checkin" element={<RequireAuth><FaceCheckinPage /></RequireAuth>} />
            
            {/* Role-specific routes */}
            <Route path="/instructor/*" element={
              <RequireAuth allowedRoles={['instructor', 'admin']}>
                <Routes>
                  <Route path="/" element={<InstructorDashboard />} />
                  <Route path="/bulk" element={<InstructorBulkActions />} />
                </Routes>
              </RequireAuth>
            } />
            
            <Route path="/admin/*" element={
              <RequireAuth allowedRoles={['admin']}>
                <Routes>
                  <Route path="/" element={<AdminDashboard />} />
                  <Route path="/bulk" element={<AdminBulkActions />} />
                </Routes>
              </RequireAuth>
            } />
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </Router>
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
