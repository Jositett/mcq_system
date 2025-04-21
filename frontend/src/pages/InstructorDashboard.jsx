import React from 'react';
import InstructorBatches from '../components/InstructorBatches';
import InstructorTests from '../components/InstructorTests';
import InstructorBulkActions from './InstructorBulkActions';
import InstructorAttendanceReview from '../components/InstructorAttendanceReview';
import { Tab } from '@headlessui/react';

export default function InstructorDashboard({ user }) {
  const token = localStorage.getItem('access_token');
  return (
    <div className="flex flex-col items-center mt-8">
      <div className="bg-white rounded shadow p-6 min-w-[320px] mb-4 w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-2">Welcome, {user?.full_name || user?.username || 'Instructor'}!</h1>
        <div className="text-gray-600 mb-2">Role: {user?.role}</div>
      </div>
      <Tab.Group>
        <Tab.List className="flex space-x-2 bg-gray-100 rounded px-2 py-1 mb-4">
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Batches</Tab>
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Tests</Tab>
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Bulk Actions</Tab>
          <Tab className={({ selected }) => selected ? 'bg-blue-600 text-white px-4 py-2 rounded' : 'px-4 py-2 rounded text-blue-600 hover:bg-blue-100'}>Attendance Review</Tab>
        </Tab.List>
        <Tab.Panels className="w-full max-w-2xl">
          <Tab.Panel>
            {/* InstructorBatches component goes here */}
            <InstructorBatches token={token} user={user} />
          </Tab.Panel>
          <Tab.Panel>
            {/* InstructorTests component goes here */}
            <InstructorTests token={token} user={user} />
          </Tab.Panel>
          <Tab.Panel>
            {/* InstructorBulkActions component goes here */}
            <InstructorBulkActions token={token} user={user} />
          </Tab.Panel>
          <Tab.Panel>
            {/* InstructorAttendanceReview component goes here */}
            <InstructorAttendanceReview token={token} instructorId={user?.id} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
