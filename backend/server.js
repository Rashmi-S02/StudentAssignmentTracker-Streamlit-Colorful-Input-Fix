// TaskTrack Student Assignment Tracker — all 17 HTTP endpoints visible here.
// 2 server check endpoints + 5 authentication/profile endpoints + 10 assignment endpoints.
// Data models live in models/, and login validation middleware lives in middleware/auth.js.
// All /api/assignments routes require a valid logged-in student token.
const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const crypto = require("crypto");
const { promisify } = require("util");
const User = require("./models/User");
const Assignment = require("./models/Assignment");
const { requireAuth, hashToken } = require("./middleware/auth");
require("dotenv").config();

const app = express();
const scrypt = promisify(crypto.scrypt);
app.use(cors());
app.use(express.json());

// -----------------------------------
// A. SERVER CHECK APIs (2)
// -----------------------------------
app.get("/", (req, res) => {
  res.send("Student Assignment Tracker Backend is running!");
});

app.get("/api/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    message: "Server is healthy",
    uptime: `${Math.floor(process.uptime())}s`,
    timestamp: new Date().toISOString(),
  });
});

// -----------------------------------
// B. AUTHENTICATION AND PROFILE APIs (5)
// -----------------------------------
async function hashPassword(password, salt = crypto.randomBytes(16).toString("hex")) {
  const key = await scrypt(password, salt, 64);
  return `${salt}:${key.toString("hex")}`;
}

async function verifyPassword(password, saved) {
  const [salt, stored] = (saved || "").split(":");
  if (!salt || !stored || !/^[a-f0-9]{128}$/.test(stored)) return false;
  const candidate = Buffer.from((await hashPassword(password, salt)).split(":")[1], "hex");
  return crypto.timingSafeEqual(candidate, Buffer.from(stored, "hex"));
}

function publicUser(user) {
  const { _id, name, email, rollNo, department, year, semester, gpa } = user;
  return { id: String(_id), name, email, rollNo, department, year, semester, gpa, role: "Student", avatarUrl: "/student_avatar.jpg" };
}

async function startSession(user, res, status = 200) {
  const token = crypto.randomBytes(32).toString("hex");
  user.sessionHash = hashToken(token);
  await user.save();
  res.status(status).json({ token, user: publicUser(user) });
}

app.post("/api/auth/register", async (req, res) => {
  try {
    const name = String(req.body.name || "").trim();
    const email = String(req.body.email || "").trim().toLowerCase();
    const password = String(req.body.password || "");
    if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || password.length < 8) {
      return res.status(400).json({ error: "Enter your name, a valid email, and a password of at least 8 characters." });
    }
    if (await User.exists({ email })) return res.status(409).json({ error: "An account with this email already exists." });
    const user = await User.create({ name, email, passwordHash: await hashPassword(password) });
    await startSession(user, res, 201);
  } catch (error) {
    if (error.code === 11000) return res.status(409).json({ error: "An account with this email already exists." });
    res.status(500).json({ error: "Could not create account. Try again." });
  }
});

app.post("/api/auth/login", async (req, res) => {
  try {
    const email = String(req.body.email || "").trim().toLowerCase();
    const user = await User.findOne({ email }).select("+passwordHash +sessionHash");
    if (!user || !(await verifyPassword(String(req.body.password || ""), user.passwordHash))) {
      return res.status(401).json({ error: "Incorrect email or password." });
    }
    await startSession(user, res);
  } catch (error) {
    res.status(500).json({ error: "Could not sign in. Try again." });
  }
});

app.get("/api/auth/profile", requireAuth, (req, res) => res.json(publicUser(req.user)));

app.put("/api/auth/profile", requireAuth, async (req, res) => {
  try {
    for (const field of ["name", "rollNo", "department", "year", "semester", "gpa"]) {
      if (typeof req.body[field] === "string") req.user[field] = req.body[field].trim();
    }
    await req.user.save();
    res.json({ profile: publicUser(req.user) });
  } catch (error) {
    res.status(400).json({ error: "Could not update profile." });
  }
});

app.post("/api/auth/logout", requireAuth, async (req, res) => {
  req.user.sessionHash = undefined;
  await req.user.save();
  res.json({ message: "Logged out." });
});


// -----------------------------------
// C. ASSIGNMENT APIs (10)
// -----------------------------------
// Auth guard: runs before every endpoint whose URL starts with /api/assignments.
app.use("/api/assignments", requireAuth);

// 1. GET all assignments (sorted by dueDate)
app.get("/api/assignments", async (req, res) => {
  try {
    console.log("Fetching assignments from MongoDB...");
    const assignments = await Assignment.find({ owner: req.user._id }).sort({ dueDate: 1 });
    console.log("Assignments fetched:", assignments.length);
    res.status(200).json(assignments);
  } catch (error) {
    console.error("GET assignments error:", error);
    res.status(500).json({ message: error.message });
  }
});

// 2. GET assignment statistics summary (total, pending, in-progress, completed, overdue)
app.get("/api/assignments/stats/summary", async (req, res) => {
  try {
    const assignments = await Assignment.find({ owner: req.user._id });
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const total = assignments.length;
    const pending = assignments.filter((a) => a.status === "Pending").length;
    const inProgress = assignments.filter((a) => a.status === "In Progress").length;
    const completed = assignments.filter((a) => a.status === "Completed").length;
    const overdue = assignments.filter((a) => {
      const due = new Date(a.dueDate);
      return a.status !== "Completed" && due < today;
    }).length;

    res.status(200).json({
      total,
      pending,
      inProgress,
      completed,
      overdue,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 3. GET upcoming assignments that are not completed yet
app.get("/api/assignments/filter/upcoming", async (req, res) => {
  try {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const upcoming = await Assignment.find({
      owner: req.user._id,
      status: { $ne: "Completed" },
      dueDate: { $gte: today },
    }).sort({ dueDate: 1 });

    res.status(200).json(upcoming);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 4. GET search assignments by keyword in title, subject, or description (?q=keyword)
app.get("/api/assignments/search", async (req, res) => {
  try {
    const query = req.query.q || "";
    const regex = new RegExp(query, "i");

    const results = await Assignment.find({
      owner: req.user._id,
      $or: [{ title: regex }, { subject: regex }, { description: regex }],
    }).sort({ dueDate: 1 });

    res.status(200).json(results);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 5. DELETE bulk completed assignments (cleanup endpoint)
app.delete("/api/assignments/completed/all", async (req, res) => {
  try {
    const result = await Assignment.deleteMany({ owner: req.user._id, status: "Completed" });
    res.status(200).json({
      message: "Completed assignments deleted successfully",
      deletedCount: result.deletedCount,
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// 6. GET one assignment by ID
app.get("/api/assignments/:id", async (req, res) => {
  try {
    const assignment = await Assignment.findOne({ _id: req.params.id, owner: req.user._id });

    if (!assignment) {
      return res.status(404).json({ message: "Assignment not found" });
    }

    res.status(200).json(assignment);
  } catch (error) {
    res.status(400).json({ message: "Invalid assignment ID" });
  }
});

// 7. CREATE a new assignment
app.post("/api/assignments", async (req, res) => {
  try {
    const { title, subject, description, dueDate, priority, status } = req.body;
    const assignment = await Assignment.create({ owner: req.user._id, title, subject, description, dueDate, priority, status });
    res.status(201).json(assignment);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// 8. PUT update full assignment details
app.put("/api/assignments/:id", async (req, res) => {
  try {
    const { title, subject, description, dueDate, priority, status } = req.body;
    const assignment = await Assignment.findOneAndUpdate(
      { _id: req.params.id, owner: req.user._id },
      { title, subject, description, dueDate, priority, status },
      { new: true, runValidators: true }
    );

    if (!assignment) {
      return res.status(404).json({ message: "Assignment not found" });
    }

    res.status(200).json(assignment);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// 9. PATCH quick-update assignment status only
app.patch("/api/assignments/:id/status", async (req, res) => {
  try {
    const { status } = req.body;
    if (!["Pending", "In Progress", "Completed"].includes(status)) {
      return res.status(400).json({ message: "Invalid status value" });
    }

    const assignment = await Assignment.findOneAndUpdate(
      { _id: req.params.id, owner: req.user._id },
      { status },
      { new: true }
    );

    if (!assignment) {
      return res.status(404).json({ message: "Assignment not found" });
    }

    res.status(200).json(assignment);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

// 10. DELETE an assignment by ID
app.delete("/api/assignments/:id", async (req, res) => {
  try {
    const assignment = await Assignment.findOneAndDelete({ _id: req.params.id, owner: req.user._id });

    if (!assignment) {
      return res.status(404).json({ message: "Assignment not found" });
    }

    res.status(200).json({ message: "Assignment deleted successfully" });
  } catch (error) {
    res.status(400).json({ message: "Invalid assignment ID" });
  }
});


// Start HTTP server only after MongoDB connects.
mongoose
  .connect(process.env.MONGODB_URI)
  .then(() => {
    console.log("MongoDB connected successfully!");
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  })
  .catch((error) => {
    console.error("MongoDB connection failed:", error.message);
  });
