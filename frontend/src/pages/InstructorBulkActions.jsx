import React from 'react';
import InstructorBulkStudentUpload from '../components/InstructorBulkStudentUpload';

export default function InstructorBulkActions() {
  return (
    <div className="mt-8 flex flex-col items-center w-full max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 w-full transition-colors duration-200">
        <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Bulk Actions</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Use the form below to upload students to your batches in bulk. Download the provided template to prepare your data.
        </p>
        
        <InstructorBulkStudentUpload />
      </div>
    </div>
  );
}
