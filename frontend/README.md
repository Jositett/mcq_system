# MCQ System Frontend

A React-based frontend for the MCQ Test & Attendance System, supporting both light and dark themes.

## Features

- JWT authentication (login/register)
- Student dashboard: face upload (with face-api.js), attendance check-in, attendance history
- Instructor/admin dashboards
- Light and dark mode toggle (theme persistence)

## Quickstart

1. Install dependencies:

   ```sh
   npm install
   # or
   yarn install
   ```

2. Start the dev server:

   ```sh
   npm run dev
   # or
   yarn dev
   ```

3. Configure backend API URL and CORS as needed in `.env` or config files.

---

## Tech Stack

- React (with Vite)
- MUI (Material UI) for UI and theming
- face-api.js for face recognition
- axios for HTTP requests
