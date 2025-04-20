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

## See `/docs` or `/redoc` for full OpenAPI schema
