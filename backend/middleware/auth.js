const crypto = require("crypto");
const User = require("../models/User");

const hashToken = (token) => crypto.createHash("sha256").update(token).digest("hex");

async function requireAuth(req, res, next) {
  try {
    const header = req.get("authorization") || "";
    const token = header.startsWith("Bearer ") ? header.slice(7) : "";
    if (!/^[a-f0-9]{64}$/.test(token)) return res.status(401).json({ error: "Please sign in." });
    const user = await User.findOne({ sessionHash: hashToken(token) });
    if (!user) return res.status(401).json({ error: "Session expired. Please sign in again." });
    req.user = user;
    next();
  } catch (error) {
    next(error);
  }
}

module.exports = { requireAuth, hashToken };
