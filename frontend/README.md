# MCQ System Frontend

A React-based frontend for the MCQ Test & Attendance System, supporting both light and dark themes, fully modernized with TailwindCSS v4+ and Headless UI.

## Features

- Modern, responsive UI (TailwindCSS v4+)
- JWT authentication (login/register)
- Student dashboard: face upload (with face-api.js), attendance check-in, attendance history
- Instructor/admin dashboards
- Dark/Light mode toggle (Tailwind's dark mode, persistent)
- Accessible modals, dropdowns, etc. (Headless UI)
- State management with Redux Toolkit
- Error boundaries and improved user feedback

## Quickstart

1. Install dependencies:

   ```sh
   npm install
   ```

2. Start the dev server:

   ```sh
   npm run dev
   ```

3. Configure backend API URL and CORS as needed in `.env` or config files.

---

## User Profile & Registration Fields

The following fields are present in the registration and profile forms:

- Full Name
- Email
- Phone
- Department
- Bio
- Gender (dropdown: only `male`, `female`, `other` allowed)
- Profile Picture (optional)

### Gender Field Validation

The gender dropdown only allows selecting:

- Male
- Female
- Other

Attempting to submit any other value will result in a validation error.

## Tech Stack

- React (with Vite)
- TailwindCSS v4+ for all UI styling and theming
- Headless UI for accessible, unstyled components
- face-api.js for face recognition
- axios for HTTP requests
- Redux Toolkit for state management
- Vite for build and dev server
- Jest & React Testing Library for testing
