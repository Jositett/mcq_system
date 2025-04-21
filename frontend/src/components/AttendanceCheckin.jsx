import React, { useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { markAttendance } from '../features/attendanceSlice';
import { useToast } from './ToastContext';
import Human from 'human';

export default function AttendanceCheckin() {
  const dispatch = useDispatch();
  const showToast = useToast();
  const fileInput = useRef();
  
  // Get attendance state from Redux
  const { status: attendanceStatus, error: attendanceError } = useSelector(state => state.attendance);
  
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  const human = new Human();

  async function extractEmbedding(img) {
    // Configure Human for face detection and embedding
    human.configure({
      face: {
        enabled: true,
        detector: { return: true, rotation: false },
        description: { enabled: true },
        iris: { enabled: false },
        emotion: { enabled: false },
        antispoof: { enabled: true }
      }
    });
    
    // Run detection
    const result = await human.detect(img);
    if (!result.face || result.face.length === 0) throw new Error('No face detected');
    if (result.face.length > 1) throw new Error('Multiple faces detected. Please use an image with only one face.');
    
    // Check for anti-spoofing
    if (result.face[0].antispoof && result.face[0].antispoof.score < 0.5) {
      throw new Error('The image appears to be a photo of a photo or screen. Please use a real face image.');
    }
    
    return result.face[0].embedding.join(',');
  }

  async function handleFileChange(e) {
    setError('');
    setStatus('');
    setLoading(true);
    setPreviewUrl(null);
    
    const file = e.target.files[0];
    if (!file) return setLoading(false);
    
    // Create preview
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    
    try {
      const img = document.createElement('img');
      img.src = objectUrl;
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
      });
      
      const embedding = await extractEmbedding(img);
      
      // Dispatch the attendance action
      await dispatch(markAttendance({ embedding })).unwrap();
      
      setStatus('Attendance check-in successful!');
      showToast('Attendance marked successfully', 'success');
    } catch (err) {
      console.error('Attendance check-in error:', err);
      setError(err.message || 'Failed to process image');
      showToast(err.message || 'Failed to mark attendance', 'error');
    } finally {
      setLoading(false);
      fileInput.current.value = '';
    }
  }

  return (
    <div className="flex flex-col items-center">
      <div className="w-full">
        {status && (
          <div className="mb-4 p-3 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-100 rounded-md flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            {status}
          </div>
        )}
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-100 rounded-md flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}
        
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="w-full md:w-1/2">
            {previewUrl ? (
              <div className="relative rounded-lg overflow-hidden border-2 border-blue-500 dark:border-blue-400 aspect-video">
                <img 
                  src={previewUrl} 
                  alt="Face preview" 
                  className="w-full h-full object-cover"
                  onLoad={() => URL.revokeObjectURL(previewUrl)}
                />
              </div>
            ) : (
              <div className="bg-gray-100 dark:bg-gray-700 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 aspect-video flex flex-col items-center justify-center p-4 transition-colors duration-200">
                <svg className="h-12 w-12 text-gray-400 dark:text-gray-500 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center">Take a selfie or upload a face image</p>
              </div>
            )}
          </div>
          
          <div className="w-full md:w-1/2 flex flex-col gap-4">
            <label className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200">
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </>
              ) : (
                <>
                  <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Select Face Image
                </>
              )}
              <input 
                type="file" 
                accept="image/*" 
                hidden 
                ref={fileInput} 
                onChange={handleFileChange} 
                disabled={loading || attendanceStatus === 'loading'} 
              />
            </label>
            
            <div className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-3 rounded-md transition-colors duration-200">
              <p className="font-medium mb-1">Instructions:</p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Take a clear photo of your face</li>
                <li>Ensure good lighting for accurate recognition</li>
                <li>Your face should be clearly visible</li>
                <li>Attendance is processed securely on your device</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
