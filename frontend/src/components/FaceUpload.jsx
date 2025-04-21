import React, { useRef, useState } from 'react';
import Human from 'human';
import { faceApi } from '../api';

export default function FaceUpload({ onSuccess }) {
  const fileInput = useRef();
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
    // Use the embedding vector from the first face
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
      
      // Send embedding to backend using our API service
      await faceApi.uploadEmbedding({
        embedding,
        created_at: new Date().toISOString().slice(0,10)
      });
      
      setStatus('Face embedding uploaded successfully!');
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error('Face upload error:', err);
      setError(err.message || 'Failed to process image');
    } finally {
      setLoading(false);
      fileInput.current.value = '';
    }
  }

  return (
    <div className="flex flex-col items-center mt-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 w-full max-w-md transition-colors duration-200">
        <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Upload Face Image</h2>
        
        {status && (
          <div className="mb-4 p-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100 rounded-md flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            {status}
          </div>
        )}
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 rounded-md flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}
        
        {previewUrl && (
          <div className="mb-4 flex justify-center">
            <div className="relative w-32 h-32 rounded-full overflow-hidden border-2 border-blue-500 dark:border-blue-400">
              <img 
                src={previewUrl} 
                alt="Face preview" 
                className="w-full h-full object-cover"
                onLoad={() => URL.revokeObjectURL(previewUrl)}
              />
            </div>
          </div>
        )}
        
        <div className="flex justify-center">
          <label className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200">
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
                Select Image
              </>
            )}
            <input 
              type="file" 
              accept="image/*" 
              hidden 
              ref={fileInput} 
              onChange={handleFileChange} 
              disabled={loading} 
            />
          </label>
        </div>
        
        <div className="mt-4 text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 p-3 rounded-md">
          <p className="font-medium mb-1">Important:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Only one face per image</li>
            <li>Face should be clearly visible</li>
            <li>Embedding is extracted client-side for privacy</li>
            <li>Photos of photos may be rejected</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
