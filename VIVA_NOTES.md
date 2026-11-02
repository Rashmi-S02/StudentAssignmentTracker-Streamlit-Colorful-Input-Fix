# TaskTrack — easy viva notes

## 1. Technologies used
- **Frontend:** Streamlit and Python
- **Backend:** Node.js with Express.js
- **Database:** MongoDB
- **Database library:** Mongoose
- **Frontend-to-backend communication:** Python `requests`
- **PDF report:** ReportLab

## 2. How the connection works
1. A student clicks a button in Streamlit `app.py`.
2. `api_client.py` sends an HTTP request to the Express backend at `http://127.0.0.1:5000`.
3. `backend/server.js` validates the session token and reads or updates MongoDB using Mongoose.
4. Express returns JSON, and Streamlit shows the result.

Streamlit does not connect directly to MongoDB.

## 3. API count
There are **17 backend endpoints** in `backend/server.js`:
- 2 server checks: `GET /` and `GET /api/health`
- 5 authentication/profile endpoints: register, login, get profile, update profile, logout
- 10 assignment endpoints: list, statistics, upcoming filter, search, delete all completed, get one, create, edit, update status, delete one

The Streamlit UI calls the main 9 endpoints needed for the normal student workflow.

## 4. HTTP methods
- **GET:** retrieve data
- **POST:** register, sign in, create an assignment
- **PUT:** update full assignment or profile details
- **PATCH:** update only assignment status
- **DELETE:** delete one or more assignments

## 5. Secure login
- Passwords are stored as salted scrypt hashes, not plain text.
- After login, the backend returns a random session token.
- The database stores the token hash, not the raw token.
- Assignment APIs require authentication and only return assignments belonging to the logged-in student.

## 6. Five dashboard features
- **Progress ring:** `(completed assignments / total assignments) × 100`; zero assignments means 0%.
- **Deadline reminders:** compare incomplete assignment due dates with today's date to identify overdue, due today, and due tomorrow.
- **Performance charts:** count assignments by status and priority.
- **Calendar:** group assignments by due date and let the student click a date to inspect them.
- **PDF report:** ReportLab creates a downloadable summary of the student's assignments.

## 7. What to show in the code
- `backend/server.js`: all 17 API endpoints
- `backend/models/User.js`: student fields and password hash
- `backend/models/Assignment.js`: assignment fields, priority, status, due date, owner
- `backend/middleware/auth.js`: checks the session token and student identity
- `streamlit_app/app.py`: dashboard design, login form, pages and UI actions
- `streamlit_app/api_client.py`: sends requests to the backend
- `streamlit_app/helpers.py`: progress, deadline logic and PDF report

## 8. Three-minute demonstration
1. Register and sign in.
2. Add an assignment.
3. Show the record in MongoDB Compass.
4. Mark an assignment Completed and show the progress/chart update.
5. Show reminders and overdue assignments.
6. Click a date in the calendar and download the PDF.
7. Explain one GET, POST, PUT, PATCH, and DELETE route in `server.js`.
