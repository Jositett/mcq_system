import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { updateUserProfile } from "../features/authSlice";
import { userApi } from "../api";

export default function Profile() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phone: "",
    department: "",
    bio: "",
    gender: ""
  });
  const [profileImage, setProfileImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });
  
  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFormData({
        fullName: user.fullName || user.full_name || "",
        email: user.email || "",
        phone: user.phone || "",
        department: user.department || "",
        bio: user.bio || "",
        gender: user.gender || ""
      });
      
      if (user.profile_picture) {
        setPreviewUrl(user.profile_picture);
      }
    }
  }, [user]);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfileImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ type: "", text: "" });
    
    try {
      const formDataToSend = new FormData();
      // Map fields to API snake_case
      if (formData.fullName) formDataToSend.append("full_name", formData.fullName);
      if (formData.email) formDataToSend.append("email", formData.email);
      if (formData.phone) formDataToSend.append("phone", formData.phone);
      if (formData.department) formDataToSend.append("department", formData.department);
      if (formData.bio) formDataToSend.append("bio", formData.bio);
      if (formData.gender) formDataToSend.append("gender", formData.gender);
      // Append profile image
      if (profileImage) {
        formDataToSend.append("profile_picture", profileImage);
      }
      const response = await userApi.updateProfile(formDataToSend);
      
      if (response.data) {
        // Update Redux store with new user data
        dispatch(updateUserProfile(response.data));
        if (response.data.profile_picture) {
          setPreviewUrl(response.data.profile_picture);
        }
        setMessage({ 
          type: "success", 
          text: "Profile updated successfully!"
        });
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      setMessage({ 
        type: "error", 
        text: error.response?.data?.message || "Failed to update profile. Please try again."
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto my-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md transition-colors duration-200">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">Profile Management</h2>
      
      {message.text && (
        <div className={`mb-4 p-3 rounded ${message.type === "success" ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200" : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200"}`}>
          {message.text}
        </div>
      )}
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* Profile Image Section */}
        <div className="w-full md:w-1/3 flex flex-col items-center">
          <div className="relative w-48 h-48 mb-4 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
            {previewUrl ? (
              <img 
                src={previewUrl} 
                alt="Profile" 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="text-gray-400 dark:text-gray-500 text-5xl font-light">
                {user?.fullName?.charAt(0) || user?.full_name?.charAt(0) || user?.email?.charAt(0) || "?"}
              </div>
            )}
          </div>
          
          <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors duration-200 text-center">
            <span>Change Profile Picture</span>
            <input 
              type="file" 
              accept="image/*" 
              className="hidden" 
              onChange={handleImageChange}
            />
          </label>
        </div>
        
        {/* Profile Form Section */}
        <div className="w-full md:w-2/3">
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-200"
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-200"
                  disabled
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Email cannot be changed</p>
              </div>
              
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-200"
                />
              </div>
              
              <div>
                <label htmlFor="department" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Department
                </label>
                <input
                  type="text"
                  id="department"
                  name="department"
                  value={formData.department}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-200"
                />
              </div>
              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Gender
                </label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-200"
                >
                  <option value="">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
            </div>
            
            <div className="mb-4">
              <label htmlFor="bio" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Bio
              </label>
              <textarea
                id="bio"
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                rows="4"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors duration-200"
              ></textarea>
            </div>
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors duration-200 flex items-center"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : "Save Changes"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
