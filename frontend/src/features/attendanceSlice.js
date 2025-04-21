import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { attendanceApi } from '../api';

// Async thunks for attendance operations
export const markAttendance = createAsyncThunk(
  'attendance/markAttendance',
  async (data, { rejectWithValue }) => {
    try {
      const response = await attendanceApi.markAttendance(data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to mark attendance' });
    }
  }
);

export const fetchAttendanceHistory = createAsyncThunk(
  'attendance/fetchHistory',
  async (params, { rejectWithValue }) => {
    try {
      const response = await attendanceApi.getAttendanceHistory(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch attendance history' });
    }
  }
);

export const fetchAttendanceStats = createAsyncThunk(
  'attendance/fetchStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await attendanceApi.getAttendanceStats();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch attendance stats' });
    }
  }
);

const initialState = {
  todayAttendance: null,
  history: [],
  stats: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
};

const attendanceSlice = createSlice({
  name: 'attendance',
  initialState,
  reducers: {
    clearAttendanceError: (state) => {
      state.error = null;
    },
    resetAttendanceState: (state) => {
      state.todayAttendance = null;
      state.status = 'idle';
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Mark Attendance
      .addCase(markAttendance.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(markAttendance.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.todayAttendance = action.payload;
      })
      .addCase(markAttendance.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to mark attendance';
      })
      
      // Fetch Attendance History
      .addCase(fetchAttendanceHistory.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchAttendanceHistory.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.history = action.payload;
      })
      .addCase(fetchAttendanceHistory.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to fetch attendance history';
      })
      
      // Fetch Attendance Stats
      .addCase(fetchAttendanceStats.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchAttendanceStats.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.stats = action.payload;
      })
      .addCase(fetchAttendanceStats.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to fetch attendance stats';
      });
  },
});

export const { clearAttendanceError, resetAttendanceState } = attendanceSlice.actions;

export default attendanceSlice.reducer;
