const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true, trim: true },
  passwordHash: { type: String, required: true, select: false },
  sessionHash: { type: String, select: false },
  rollNo: { type: String, default: "" },
  department: { type: String, default: "" },
  year: { type: String, default: "" },
  semester: { type: String, default: "" },
  gpa: { type: String, default: "" },
}, { timestamps: true });

module.exports = mongoose.model("User", userSchema);
