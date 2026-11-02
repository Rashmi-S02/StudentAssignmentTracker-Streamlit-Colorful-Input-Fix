# TaskTrack: simple API viva reference

**17 endpoints total: 10 assignment + 5 auth/profile + 2 server checks.**
All 17 route registrations (`app.get`, `app.post`, `app.put`, `app.patch`,
`app.delete`) are located in `server.js`.

**What is an API?** It is a URL and HTTP method the frontend uses to
communicate with the backend.

**What is CRUD?** Create = POST, Read = GET, Update = PUT/PATCH, Delete = DELETE.

**How does login work?** The server hashes and stores passwords with scrypt;
login verifies the password, generates a random token, and stores only a
SHA-256 hash of that token. Other protected routes use `requireAuth` to check
that token and find the correct student.

**How is data stored?** Mongoose manages the `User` and `Assignment` models in
MongoDB. Each assignment has an `owner` field, so students see only their own.

**How are progress, reminders, charts, and calendar built?** React receives
assignments from `GET /api/assignments` and calculates these values in the
browser. PDF is also generated in the browser.

**Which endpoints are currently called from the frontend?** 9: `POST register`,
`POST login`, `POST logout`, `PUT profile`, `GET assignments`, `POST assignments`,
`PUT assignment/:id`, `PATCH assignment/:id/status`, `DELETE assignment/:id`.

**What about the other 8?** 2 health endpoints, 1 get-profile endpoint, and 5
assignment utility endpoints: stats, upcoming, search, get-by-ID, bulk delete.

**In VS Code**: Open `backend/server.js` to show all Express API registrations.
Use Thunder Client/Postman for endpoints not called by the frontend. The
assignment APIs require an `Authorization: Bearer <token>` header from login.

**Recommended 15-mark demo:** Register -> Login -> Add 3 assignments with
past/today/tomorrow due dates -> Show overdue/reminders/calendar -> Mark
one Complete -> Show progress and charts change -> Download PDF -> Logout.
