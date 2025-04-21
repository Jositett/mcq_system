# MCQ System Backend API Reference

## Authentication

### Register

- **POST** `/api/auth/register`
- **Body:** `{ username, email, full_name, role, password }`
- **Response:** Registered user info

### Login

- **POST** `/api/auth/login`
- **Body:** `{ username, password }`
- **Response:** `{ access_token, token_type }`

---

## Face Recognition (Hybrid: Embedding or Image)

### Upload Face Image

- **POST** `/api/face/upload`
- **Auth:** Student (JWT)
- **Body:**

  ```json
  {
    "image_data": "base64string",      // optional if embedding is provided
    "embedding": "comma,separated,128",// optional if image_data is provided
    "created_at": "YYYY-MM-DD"         // required
  }
  ```

- **Logic:**
  - If both `embedding` and `image_data` are provided, `embedding` is used.
  - If neither is valid, returns 400.
- **Response:** Face image record with embedding.

### Get My Face Images

- **GET** `/api/face/my-images`
- **Auth:** Student (JWT)
- **Response:** List of face images for current user

---

## Attendance

### Face Check-in

- **POST** `/api/attendance/face-checkin`
- **Auth:** Student (JWT)
- **Body:**

  ```json
  {
    "embedding": "comma,separated,128", // optional
    "image": "base64string"             // optional
  }
  ```

- **Logic:**
  - If both are provided, `embedding` is used.
  - Only one check-in allowed per day.
- **Response:** `{ success, message, attendance_id }`

### Standard Check-in

- **POST** `/api/attendance/check-in`
- **Auth:** Student (JWT)
- **Body:** `{ student_id, date, status }`
- **Response:** Check-in record

### Attendance History

- **GET** `/api/attendance/history/{student_id}`
- **Auth:** Student (JWT, self only)
- **Response:** List of attendance records

---

## Users (Admin Only)

### List Users

- **GET** `/api/users/`
- **Auth:** Admin (JWT)
- **Response:** List of users

### Get/Update/Delete User

- **GET/PUT/DELETE** `/api/users/{user_id}`
- **Auth:** Admin (JWT)
- **Response:** User info or confirmation

---

## Instructors

### Get Batches

- **GET** `/api/instructors/{instructor_id}/batches`
- **Auth:** Instructor (JWT, self only)
- **Response:** List of batches

### Get Tests

- **GET** `/api/instructors/{instructor_id}/tests`
- **Auth:** Instructor (JWT, self only)
- **Response:** List of tests

---

## Students

### Get Attendance

- **GET** `/api/students/{student_id}/attendance`
- **Auth:** Student (JWT, self only)
- **Response:** List of attendance records

### Get Tests (Students)

- **GET** `/api/students/{student_id}/tests`
- **Auth:** Student (JWT, self only)
- **Response:** List of tests

---

## Error Responses

- **400:** Bad request (invalid input, already checked in, multiple faces, etc)
- **401:** Unauthorized (invalid token)
- **403:** Forbidden (role or ownership violation)
- **404:** Not found
- **415:** Invalid image format

---

## Security Notes

- All endpoints (except `/api/auth/*`) require JWT auth.
- Role-based access enforced via `require_role` dependency.
- Only one face per image is allowed for training/check-in.
- Embedding must be a comma-separated string of 128 floats.
- Only students can upload/check-in their own face.
- Admins can manage all users. Instructors can only access their own data.

---

### Bulk Student Upload (Admin)

- **Endpoint:** `POST /api/batches/students/bulk`
- **Permissions:** Admin only (JWT required)
- **Request Body:**

  ```json
  {
    "students": [
      {
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "roll_number": "12345",
        "dob": "2000-01-01",
        "batch_name": "Batch A"
      },
      ...
    ]
  }
  ```

- **Response:**

  ```json
  {
    "results": [
      {
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "batch_name": "Batch A",
        "success": true,
        "error": null
      },
      {
        "full_name": "Jane Smith",
        "email": "janesmith@example.com",
        "batch_name": "Batch B",
        "success": false,
        "error": "User with this email already exists"
      }
    ]
  }
  ```

- **Notes:**
  - Each student is processed individually; errors are reported per row.
  - Batches are created if they do not exist.

---

### Bulk Student Upload (Instructor)

- **Endpoint:** `POST /api/instructors/{instructor_id}/batches/students/bulk`
- **Permissions:** Instructor only (JWT required, only for their own ID)
- **Request Body:** Same as admin endpoint above
- **Response:** Same as admin endpoint above
- **Notes:**
  - Instructors can only add students to batches they manage (by name).
  - Batches are created for the instructor if they do not exist.

---

### Bulk Question Upload (Admin)

- **Endpoint:** `POST /api/tests/questions/bulk`
- **Permissions:** Admin only (JWT required)
- **Request Body:**

  ```json
  {
    "questions": [
      {
        "test_name": "Midterm 1",
        "question_text": "What is 2+2?",
        "question_type": "mcq",
        "options": "[\"2\",\"3\",\"4\",\"5\"]",
        "correct_answer": "4"
      },
      ...
    ]
  }
  ```

- **Response:**

  ```json
  {
    "results": [
      {
        "question_text": "What is 2+2?",
        "test_name": "Midterm 1",
        "success": true,
        "error": null
      },
      {
        "question_text": "What is the capital of France?",
        "test_name": "Midterm 1",
        "success": false,
        "error": "Test not found. Please create the test first."
      }
    ]
  }
  ```

- **Notes:**
  - Each question is processed individually; errors are reported per row.
  - The referenced test must already exist.

---

### Bulk Question Upload (Instructor)

- **Endpoint:** `POST /api/instructors/{instructor_id}/tests/questions/bulk`
- **Permissions:** Instructor only (JWT required, only for their own ID)
- **Request Body:** Same as admin endpoint above
- **Response:** Same as admin endpoint above
- **Notes:**
  - Instructors can only add questions to tests they manage (by name).
  - The referenced test must already exist and be associated with the instructor.

---

## See `/docs` or `/redoc` for full OpenAPI schema
