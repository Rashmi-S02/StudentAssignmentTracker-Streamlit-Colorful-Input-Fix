# TaskTrack — Colourful Student Assignment Tracker

A student-friendly, colourful Streamlit dashboard for a 15-mark college microproject. The dashboard uses a navy sidebar, pastel metric cards, a progress ring, reminders, upcoming and overdue assignments, performance charts, a clickable calendar, and PDF report download.

## Features

- Secure student registration and sign-in (no demo login)
- Passwords hashed on the Express backend; private assignments per student
- Add, edit, delete, and update assignment status
- Attractive dashboard with pastel cards and a student illustration
- Progress percentage and circular progress indicator
- Deadline reminders for overdue, due today, and due tomorrow
- Separate upcoming and overdue dashboard sections
- Performance charts by status and priority
- Clickable monthly assignment calendar
- Downloadable PDF report
- Student profile page
- All 17 backend endpoints remain in `backend/server.js` for the viva

## Folder structure

```text
StudentAssignmentTracker-Streamlit-Simple/
├── backend/
│   ├── server.js             # All 17 REST API endpoints
│   ├── models/
│   │   ├── User.js
│   │   └── Assignment.js
│   ├── middleware/auth.js
│   ├── .env.example
│   └── package.json
├── streamlit_app/
│   ├── app.py                # Pages, forms, dashboard and styling
│   ├── api_client.py         # Sends HTTP requests to Express
│   ├── helpers.py            # Progress, reminders and PDF report
│   ├── requirements.txt
│   └── assets/hero_student.png
├── README.md
└── VIVA_NOTES.md
```

## Run in VS Code on Windows

**Use Python 3.12** for the Streamlit environment. Keep Python 3.15 installed if you need it for other projects.

### 1. Start MongoDB

Open `Win + R`, type `services.msc`, press Enter, and start **MongoDB Server** if it is stopped. If it is already running, leave it running.

### 2. Configure the backend

Open the project folder in VS Code. In the terminal, run these commands one at a time from the project root:

```powershell
cd backend
Copy-Item .env.example .env
```

If `Copy-Item` says `.env.example` does not exist, create `backend/.env` manually with:

```env
MONGODB_URI=mongodb://127.0.0.1:27017/student_assignment_tracker
PORT=5000
```

Do not add `.env` to the ZIP or share it if you later put database credentials inside it.

Install and start the backend:

```powershell
npm install
node server.js
```

Leave this terminal running. Expected messages include a successful MongoDB connection and `Server running on http://localhost:5000`.

### 3. Set up Streamlit in a second terminal

Open **Terminal → New Terminal**. If the new terminal starts in the project root, run:

```powershell
cd streamlit_app
py -3.12 -m venv .venv
```

If `.venv` already exists, do not recreate it; continue with the next command.

Install the Python packages using the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
```

Wait until pip finishes and returns to the prompt. Do not cancel the install. Then start Streamlit:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open **http://localhost:8501** in the browser.

### 4. Demonstrate it to your teacher

1. Register a student account and sign in.
2. Add assignments due yesterday, today, and tomorrow.
3. Show the overdue section and deadline reminders.
4. Mark one assignment Completed and show the progress ring and charts update.
5. Click a date in the calendar.
6. Download the PDF report.
7. Show `backend/server.js` and explain GET, POST, PUT, PATCH, and DELETE.
8. Open MongoDB Compass and refresh the `users` or `assignments` collection to show stored data.

## Database connection

- MongoDB Compass connection address: `mongodb://127.0.0.1:27017`
- Project database: `student_assignment_tracker`
- Frontend: `http://localhost:8501`
- Backend: `http://localhost:5000`

Streamlit does **not** connect directly to MongoDB. It uses Python `requests` to call Express REST APIs. Express uses Mongoose to read and write MongoDB.

## API facts for the viva

- **17 backend endpoints** are defined in `backend/server.js`: 2 server checks, 5 authentication/profile endpoints, and 10 assignment endpoints.
- The Streamlit UI calls the main 9 endpoints for register, login, logout, profile update, list/create/edit/status-update/delete assignments.
- The progress ring, reminders, charts, calendar, and PDF use the assignments returned by `GET /api/assignments`; they do not need a separate endpoint each.
- HTTP methods: GET = read, POST = create/sign in, PUT = update full details, PATCH = update a field/status, DELETE = remove.

## Troubleshooting

- **`cd backend` not found:** run `dir`. You may already be inside `backend`, or you may need to open the folder containing both `backend` and `streamlit_app`.
- **MongoDB URI undefined:** make sure `backend/.env` exists and contains `MONGODB_URI=...`.
- **`No module named streamlit`:** finish installing `requirements.txt` with `streamlit_app/.venv/Scripts/python.exe`; do not run Streamlit using Python 3.15.
- **`ERROR: Operation cancelled by user`:** rerun the install and let it finish; do not press Ctrl+C.
- **Backend connection error in the app:** leave `node server.js` running in a separate terminal.
- **MongoDB database not visible in Compass:** register a user or save an assignment first, then refresh Compass.

## Project scope

Designed for a local college demonstration. A public production deployment should additionally use HTTPS, login rate limiting, session expiry, and stricter input validation.
