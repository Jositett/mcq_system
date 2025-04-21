import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { testApi } from '../api';

// Async thunks for test operations
export const fetchTests = createAsyncThunk(
  'tests/fetchTests',
  async (_, { rejectWithValue }) => {
    try {
      const response = await testApi.getTests();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch tests' });
    }
  }
);

export const fetchInstructorTests = createAsyncThunk(
  'tests/fetchInstructorTests',
  async (instructorId, { rejectWithValue }) => {
    try {
      const response = await testApi.getInstructorTests(instructorId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch instructor tests' });
    }
  }
);

export const fetchTestById = createAsyncThunk(
  'tests/fetchTestById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await testApi.getTest(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to fetch test' });
    }
  }
);

export const createTest = createAsyncThunk(
  'tests/createTest',
  async (testData, { rejectWithValue }) => {
    try {
      const response = await testApi.createTest(testData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to create test' });
    }
  }
);

export const updateTest = createAsyncThunk(
  'tests/updateTest',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await testApi.updateTest(id, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to update test' });
    }
  }
);

export const deleteTest = createAsyncThunk(
  'tests/deleteTest',
  async (id, { rejectWithValue }) => {
    try {
      await testApi.deleteTest(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to delete test' });
    }
  }
);

export const submitTestAnswers = createAsyncThunk(
  'tests/submitTestAnswers',
  async ({ id, answers }, { rejectWithValue }) => {
    try {
      const response = await testApi.submitTest(id, answers);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: 'Failed to submit test answers' });
    }
  }
);

const initialState = {
  tests: [],
  currentTest: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
  testResults: null,
};

const testSlice = createSlice({
  name: 'tests',
  initialState,
  reducers: {
    clearCurrentTest: (state) => {
      state.currentTest = null;
    },
    clearTestError: (state) => {
      state.error = null;
    },
    clearTestResults: (state) => {
      state.testResults = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch All Tests
      .addCase(fetchTests.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTests.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.tests = action.payload;
      })
      .addCase(fetchTests.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to fetch tests';
      })
      
      // Fetch Instructor Tests
      .addCase(fetchInstructorTests.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchInstructorTests.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.tests = action.payload;
      })
      .addCase(fetchInstructorTests.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to fetch instructor tests';
      })
      
      // Fetch Test by ID
      .addCase(fetchTestById.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTestById.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.currentTest = action.payload;
      })
      .addCase(fetchTestById.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to fetch test';
      })
      
      // Create Test
      .addCase(createTest.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(createTest.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.tests.push(action.payload);
      })
      .addCase(createTest.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to create test';
      })
      
      // Update Test
      .addCase(updateTest.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(updateTest.fulfilled, (state, action) => {
        state.status = 'succeeded';
        const index = state.tests.findIndex(test => test.id === action.payload.id);
        if (index !== -1) {
          state.tests[index] = action.payload;
        }
        if (state.currentTest && state.currentTest.id === action.payload.id) {
          state.currentTest = action.payload;
        }
      })
      .addCase(updateTest.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to update test';
      })
      
      // Delete Test
      .addCase(deleteTest.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(deleteTest.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.tests = state.tests.filter(test => test.id !== action.payload);
        if (state.currentTest && state.currentTest.id === action.payload) {
          state.currentTest = null;
        }
      })
      .addCase(deleteTest.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to delete test';
      })
      
      // Submit Test Answers
      .addCase(submitTestAnswers.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(submitTestAnswers.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.testResults = action.payload;
      })
      .addCase(submitTestAnswers.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload?.message || 'Failed to submit test answers';
      });
  },
});

export const { clearCurrentTest, clearTestError, clearTestResults } = testSlice.actions;

export default testSlice.reducer;
