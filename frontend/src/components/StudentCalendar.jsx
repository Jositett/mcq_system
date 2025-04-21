import React, { useState, useEffect } from "react";

export default function StudentCalendar({ attendance = [] }) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState([]);
  const [attendanceMap, setAttendanceMap] = useState({});
  
  // Format date to YYYY-MM-DD for consistent comparison
  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };
  
  // Get the status for a specific date
  const getStatusForDate = (dateString) => {
    return attendanceMap[dateString] || null;
  };
  
  // Navigate to previous month
  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };
  
  // Navigate to next month
  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };
  
  // Get month name
  const getMonthName = (date) => {
    return date.toLocaleString('default', { month: 'long' });
  };
  
  // Get day class based on attendance status
  const getDayClass = (day, status) => {
    if (!day.isCurrentMonth) {
      return 'text-gray-400 dark:text-gray-600';
    }
    
    if (day.isToday) {
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 font-semibold';
    }
    
    if (status) {
      switch(status.toLowerCase()) {
        case 'present':
          return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
        case 'absent':
          return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200';
        case 'late':
          return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200';
        case 'excused':
          return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200';
        default:
          return '';
      }
    }
    
    return '';
  };
  
  // Process attendance data
  useEffect(() => {
    const map = {};
    attendance.forEach(record => {
      const date = record.date || record.created_at;
      if (date) {
        const formattedDate = new Date(date).toISOString().split('T')[0];
        map[formattedDate] = record.status || 'present';
      }
    });
    setAttendanceMap(map);
  }, [attendance]);
  
  // Generate calendar days
  useEffect(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // First day of the month
    const firstDay = new Date(year, month, 1);
    // Last day of the month
    const lastDay = new Date(year, month + 1, 0);
    
    // Day of the week for the first day (0-6, where 0 is Sunday)
    const firstDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add days from previous month to fill the first week
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const day = prevMonthLastDay - i;
      days.push({
        date: new Date(year, month - 1, day),
        dayOfMonth: day,
        isCurrentMonth: false,
        isToday: false
      });
    }
    
    // Add days of current month
    const today = new Date();
    const todayFormatted = formatDate(today);
    
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      const dateFormatted = formatDate(date);
      
      days.push({
        date,
        dayOfMonth: day,
        isCurrentMonth: true,
        isToday: dateFormatted === todayFormatted
      });
    }
    
    // Add days from next month to complete the last week
    const remainingDays = 7 - (days.length % 7);
    if (remainingDays < 7) {
      for (let day = 1; day <= remainingDays; day++) {
        days.push({
          date: new Date(year, month + 1, day),
          dayOfMonth: day,
          isCurrentMonth: false,
          isToday: false
        });
      }
    }
    
    setCalendarDays(days);
  }, [currentDate]);
  
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  return (
    <div className="w-full bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
      {/* Calendar header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <button 
          onClick={prevMonth}
          className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
          aria-label="Previous month"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600 dark:text-gray-300" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </button>
        
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          {getMonthName(currentDate)} {currentDate.getFullYear()}
        </h2>
        
        <button 
          onClick={nextMonth}
          className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
          aria-label="Next month"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600 dark:text-gray-300" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
      
      {/* Calendar grid */}
      <div className="p-4">
        {/* Weekday headers */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {weekdays.map(day => (
            <div key={day} className="text-center text-sm font-medium text-gray-500 dark:text-gray-400">
              {day}
            </div>
          ))}
        </div>
        
        {/* Calendar days */}
        <div className="grid grid-cols-7 gap-1">
          {calendarDays.map((day, index) => {
            const dateString = formatDate(day.date);
            const status = getStatusForDate(dateString);
            const dayClass = getDayClass(day, status);
            
            return (
              <div 
                key={index} 
                className={`aspect-square flex flex-col items-center justify-center p-1 rounded-md text-sm ${dayClass} transition-colors duration-200`}
              >
                <span>{day.dayOfMonth}</span>
                {status && day.isCurrentMonth && (
                  <span className="text-xs mt-1">{status}</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Legend */}
      <div className="px-4 pb-4 pt-2">
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Legend:</div>
        <div className="flex flex-wrap gap-2">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-100 dark:bg-green-900 mr-1"></div>
            <span className="text-xs text-gray-600 dark:text-gray-300">Present</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-100 dark:bg-red-900 mr-1"></div>
            <span className="text-xs text-gray-600 dark:text-gray-300">Absent</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-yellow-100 dark:bg-yellow-900 mr-1"></div>
            <span className="text-xs text-gray-600 dark:text-gray-300">Late</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-100 dark:bg-blue-900 mr-1"></div>
            <span className="text-xs text-gray-600 dark:text-gray-300">Today</span>
          </div>
        </div>
      </div>
    </div>
  );
}
