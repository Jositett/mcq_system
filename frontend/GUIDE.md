# MCQ System Frontend Guide

This guide outlines a task-based roadmap to modernize and enhance the MCQ System frontend (React + Vite) using TailwindCSS v4+, Headless UI, Redux Toolkit, and Axios.

## Requirements

**Install Node.js dependencies:**

```bash
npm install
```

**package.json dependencies:**

```json
{
  "@headlessui/react": "^2.2.2",
  "@heroicons/react": "^2.2.0",
  "@reduxjs/toolkit": "^2.0.1",
  "autoprefixer": "^10.4.21",
  "axios": "^1.8.4",
  "chart.js": "^4.4.9",
  "human": "^0.1.5",
  "papaparse": "^5.4.1",
  "postcss": "^8.5.3",
  "react": "^19.1.0",
  "react-dom": "^19.1.0",
  "react-redux": "^9.1.0",
  "react-router-dom": "^7.5.1",
  "recharts": "^2.15.3",
  "vite": "^6.3.2"
}
```

**package.json devDependencies:**

```json
{
  "@babel/preset-env": "^7.26.9",
  "@babel/preset-react": "^7.26.3",
  "@tailwindcss/forms": "^0.5.10",
  "@tailwindcss/postcss": "^4.1.4",
  "@vitejs/plugin-react": "^4.4.0",
  "babel-jest": "^29.7.0",
  "eslint": "^8.40.0",
  "eslint-config-prettier": "^8.8.0",
  "eslint-plugin-react": "^7.32.0",
  "jest": "^29.7.0",
  "jest-environment-jsdom": "^29.7.0",
  "prettier": "^2.8.8",
  "tailwindcss": "^4.1.4"
}
```

## Task 1: Environment & Dependencies

- Ensure Node.js >=16 and npm/yarn installed.
- Initialize project with Vite (React template).
- Install core packages:
  - TailwindCSS v4+, PostCSS, Autoprefixer
  - Headless UI
  - Redux Toolkit, React Redux
  - Axios
  - Human.js (face recognition)
  - React Router v6
- Create a `.env` file with `VITE_API_URL` pointing to your backend API base URL.

## Task 2: TailwindCSS Configuration

- Create `tailwind.config.cjs`:
  - `content`: include `src/**/*.{js,jsx}`
  - `darkMode`: `'class'`
- Import Tailwind directives in `index.css`:

  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```

- Setup PostCSS if needed.

## Task 3: Project Structure

``` txt
src/
  ├─ components/
  ├─ pages/
  ├─ store/
  │    ├ authSlice.js
  │    ├ themeSlice.js
  │    ├ testSlice.js
  │    └ attendanceSlice.js
  ├─ services/
  ├─ hooks/
  ├─ utils/
  └─ App.jsx
```  

- Organize by feature and concern.

## API Endpoints Reference

- **POST /v1/auth/login**: Request `{ username: string, password: string }` → Response `{ access_token: string, refresh_token: string, token_type: string }`.
- **POST /v1/auth/refresh**: Request `{ refresh_token: string }` → Response `{ access_token: string, refresh_token: string }`.
- **POST /v1/auth/logout**: No body, invalidates refresh token.

- **GET /v1/users**: Response `[{ id, username, role, created_at }]`.
- **GET /v1/users/{id}`**: Response user detail.
- **POST /v1/users**: Request `{ username: string, password: string, role: string }`.
- **PUT /v1/users/{id}`**: Request fields to update.
- **DELETE /v1/users/{id}`**: No body.

- **GET /v1/tests**: Response `[{ id, title, description, created_at }]`.
- **GET /v1/tests/{id}`**: Response test details including questions.
- **POST /v1/tests**: Request `{ title: string, description: string, questions: object[] }`.
- **PUT /v1/tests/{id}`**: Request updated test fields.
- **DELETE /v1/tests/{id}`**.
- **POST /v1/tests/{test_id}/submit**: Request `{ answers: Record<number, string> }` → Response `{ score: number, details: object }`.

- **GET /v1/attendance**: Response `[{ id, test_id, user_id, status, timestamp }]`.
- **POST /v1/attendance**: Request `{ test_id: number, user_id: number, status: string }`.

- **POST /v1/files/upload**: Form-data key `file` → Response `{ filename: string, url: string }`.
- **GET /v1/files/{filename}`**: Download file.

## Task 4: Redux Toolkit & Store

- Create `store/index.js` and configure:

  ```js
  import { configureStore } from '@reduxjs/toolkit';
  import authReducer from './authSlice';
  import themeReducer from './themeSlice';
  // ... other slices

  export const store = configureStore({
    reducer: { auth: authReducer, theme: themeReducer, /*...*/ }
  });
  ```

- Wrap `<App />` with `<Provider store={store}>`.

## Task 5: Theme & Dark Mode

- Implement `themeSlice` with `dark`/`light` state and toggle action.
- Persist theme in `localStorage` and apply `className='dark'` on `<html>`.
- Add a toggle button in Navbar to dispatch theme change.

## Task 6: Axios API Service

- Create `services/api.js`:

  ```js
  import axios from 'axios';
  const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });
  api.interceptors.request.use(config => {/* add auth token */});
  api.interceptors.response.use(null, async err => {/* handle refresh token */});
  export default api;
  ```

- Define endpoint modules: `auth.js`, `test.js`, `attendance.js`.

## Task 7: Component & Page Migration

- **Navbar**: use Headless UI `Menu` for user menu and theme switcher.
- **Login Page**: form with Tailwind inputs, dispatch `login` action, handle errors.
- **RequireAuth**: HOC or component using `useSelector(auth)` to guard routes.
- **Dashboard**: responsive grid of cards linking to Test & Attendance.
- **FaceUpload**: migrate to Tailwind layout, integrate `Human.js` hook for capture.
- **Test Page** & **Attendance Page**: build UI with tables, forms, and charts.

## Task 8: Routing & Guards

- Configure React Router v6 in `App.jsx`:

  ```jsx
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route element={<RequireAuth />}> {/* protected routes */}
      <Route path="/dashboard" element={<Dashboard />} />
      {/* ... */}
    </Route>
  </Routes>
  ```

## Task 9: Headless UI & Accessibility

- Use Headless UI components (`Dialog`, `Disclosure`, `Menu`) for modals and menus.
- Ensure aria attributes and keyboard navigation.

## Task 10: Responsive Design

- Utilize Tailwind responsive utilities (`sm:`, `md:`, `lg:`, etc.).
- Test on mobile, tablet, desktop breakpoints.

## Task 11: Testing & Quality

- Setup Jest and React Testing Library.
- Write unit tests for slices and critical components.
- Add end-to-end tests with Cypress or Playwright (optional).

## Task 12: Build & Deployment

- Configure Vite build script and environment variables.
- Add CI workflow (GitHub Actions): lint, type-check (if TS), tests, build.
- Deploy static site (Netlify/Vercel) with appropriate environment variables.

## Future Enhancements

- Add PWA support.
- Integrate analytics (Google Analytics, Sentry).
- Implement code splitting and performance optimizations.
