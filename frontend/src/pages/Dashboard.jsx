import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchAttendanceHistory, fetchAttendanceStats } from '../features/attendanceSlice';
import FaceUpload from '../components/FaceUpload';
import AttendanceCheckin from '../components/AttendanceCheckin';
import AttendanceHistory from '../components/AttendanceHistory';
import StudentCalendar from '../components/StudentCalendar';
import BirthdayNotifications from '../components/BirthdayNotifications';
import ResultAnalytics from '../components/ResultAnalytics';

export default function Dashboard() {
  const dispatch = useDispatch();
  
  // Get auth state from Redux
  const { user, role } = useSelector(state => state.auth);
  
  // Get attendance data from Redux
  const { history, stats } = useSelector(state => state.attendance);
  
  // Fetch attendance data when component mounts
  useEffect(() => {
    if (role === 'student') {
      dispatch(fetchAttendanceHistory());
      dispatch(fetchAttendanceStats());
    }
  }, [dispatch, role]);
  
  return (
    <div className="flex flex-col items-center py-8 px-4">
      {/* Welcome Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 min-w-[320px] mb-6 w-full max-w-3xl transition-colors duration-200">
        <h1 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">
          Welcome, {user?.full_name || user?.username || 'User'}!
        </h1>
        <div className="text-gray-600 dark:text-gray-300 mb-2">Role: {role}</div>
        
        {/* Quick Stats Summary */}
        {role === 'student' && stats && (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Attendance Rate</p>
              <p className="text-xl font-semibold text-blue-600 dark:text-blue-400">{stats.attendance_rate || 0}%</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/30 p-3 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Days Present</p>
              <p className="text-xl font-semibold text-green-600 dark:text-green-400">{stats.days_present || 0}</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/30 p-3 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400">Streak</p>
              <p className="text-xl font-semibold text-purple-600 dark:text-purple-400">{stats.current_streak || 0} days</p>
            </div>
          </div>
        )}
      </div>
      
      {/* Student Dashboard */}
      {role === 'student' && (
        <div className="w-full max-w-3xl space-y-6">
          {/* Face Upload Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Face Recognition</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Upload your face for attendance verification</p>
            </div>
            <div className="p-4">
              <FaceUpload />
            </div>
          </div>
          
          {/* Attendance Check-in Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Daily Check-in</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Mark your attendance for today</p>
            </div>
            <div className="p-4">
              <AttendanceCheckin />
            </div>
          </div>
          
          {/* Attendance History Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Attendance History</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">View your past attendance records</p>
            </div>
            <div className="p-4">
              <AttendanceHistory history={history} />
            </div>
          </div>
          
          {/* Calendar View */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Calendar View</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Monthly attendance overview</p>
            </div>
            <div className="p-4">
              <StudentCalendar attendance={history || []} />
            </div>
          </div>
          
          {/* Notifications */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Notifications</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Upcoming events and birthdays</p>
            </div>
            <div className="p-4">
              <BirthdayNotifications notifications={[]} />
            </div>
          </div>
          
          {/* Results Analytics */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Performance Analytics</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">View your test results and progress</p>
            </div>
            <div className="p-4">
              <ResultAnalytics data={[]} />
            </div>
          </div>
        </div>
      )}
      
      {/* Instructor Dashboard */}
      {role === 'instructor' && (
        <div className="w-full max-w-3xl">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors duration-200">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Instructor Dashboard</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Welcome to the instructor dashboard. Use the navigation to access your courses, tests, and student management.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link to="/instructor/tests" className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors duration-200">
                <h3 className="font-medium text-blue-700 dark:text-blue-300">Manage Tests</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Create and manage your tests</p>
              </Link>
              <Link to="/instructor/students" className="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/50 transition-colors duration-200">
                <h3 className="font-medium text-green-700 dark:text-green-300">Student Management</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">View and manage your students</p>
              </Link>
            </div>
          </div>
        </div>
      )}
      
      {/* Admin Dashboard */}
      {role === 'admin' && (
        <div className="w-full max-w-3xl">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6 transition-colors duration-200">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Admin Dashboard</h2>
            <p className="text-gray-600 dark:text-gray-300">
              Welcome to the admin dashboard. Use the navigation to access system management features.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link to="/admin/users" className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/50 transition-colors duration-200">
                <h3 className="font-medium text-purple-700 dark:text-purple-300">User Management</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Manage all users in the system</p>
              </Link>
              <Link to="/admin/courses" className="bg-indigo-50 dark:bg-indigo-900/30 p-4 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors duration-200">
                <h3 className="font-medium text-indigo-700 dark:text-indigo-300">Course Management</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Manage courses and batches</p>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
