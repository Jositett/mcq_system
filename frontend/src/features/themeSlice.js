import { createSlice } from '@reduxjs/toolkit';

// Check if the user has a theme preference stored in localStorage
const getInitialTheme = () => {
  if (typeof window !== 'undefined' && window.localStorage) {
    const storedTheme = window.localStorage.getItem('theme');
    if (storedTheme) {
      return storedTheme;
    }

    // Check for user's system preference
    const userMedia = window.matchMedia('(prefers-color-scheme: dark)');
    if (userMedia.matches) {
      return 'dark';
    }
  }

  // Default to light theme
  return 'light';
};

// Apply the theme class to the HTML element
const applyTheme = (theme) => {
  const root = window.document.documentElement;
  
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
  
  // Save theme to localStorage
  localStorage.setItem('theme', theme);
};

const initialState = {
  theme: getInitialTheme(),
};

// Apply the initial theme
if (typeof window !== 'undefined') {
  applyTheme(initialState.theme);
}

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    toggleTheme: (state) => {
      const newTheme = state.theme === 'light' ? 'dark' : 'light';
      state.theme = newTheme;
      applyTheme(newTheme);
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
      applyTheme(action.payload);
    },
  },
});

export const { toggleTheme, setTheme } = themeSlice.actions;

export default themeSlice.reducer;
