import React from 'react';
import AdminUsers from '../components/AdminUsers';
import AdminStats from '../components/AdminStats';
import AdminBulkActions from './AdminBulkActions';
import AdminAttendanceReview from '../components/AdminAttendanceReview';
import { Tab } from '@headlessui/react';

export default function AdminDashboard({ user }) {
  const token = localStorage.getItem('access_token');
  return (
    <div className="flex flex-col items-center mt-8">
      <div className="bg-white rounded shadow p-6 min-w-[320px] mb-4 w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-2">Welcome, {user?.full_name || user?.username || 'Admin'}!</h1>
        <div className="text-gray-600 mb-2">Role: {user?.role}</div>
      </div>
      <Tab.Group>
        <Tab.List className="flex space-x-2 bg-gray-100 rounded px-2 py-1 mb-4">
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Users</Tab>
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Bulk Actions</Tab>
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Attendance Review</Tab>
        </Tab.List>
        <Tab.Panels className="w-full max-w-2xl">
          <Tab.Panel>
            {/* AdminStats and AdminUsers components go here */}
            <div className="mb-4"><AdminStats token={token} /></div>
            <AdminUsers token={token} />
          </Tab.Panel>
          <Tab.Panel>
            {/* AdminBulkActions component goes here */}
            <AdminBulkActions token={token} />
          </Tab.Panel>
          <Tab.Panel>
            {/* AdminAttendanceReview component goes here */}
            <AdminAttendanceReview token={token} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
