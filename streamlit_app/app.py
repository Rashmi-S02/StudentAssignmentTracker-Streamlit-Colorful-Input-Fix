"""TaskTrack: colourful, beginner-friendly Streamlit assignment tracker."""
import calendar
import html
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from api_client import api, APIError
from helpers import due_date, make_pdf, progress_stats, reminder_text

st.set_page_config(
    page_title="TaskTrack | Student Assignment Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSET_DIR = Path(__file__).parent / "assets"
HERO_IMAGE = ASSET_DIR / "hero_student.png"

# Colourful styles are kept here so they are easy to find and explain in a viva.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&display=swap');
    :root { --ink:#172554; --muted:#64748b; --purple:#6d4aff; --blue:#3b82f6; }
    html, body, [class*="css"] { font-family: 'Nunito', 'Segoe UI', sans-serif; }
    .stApp { background: linear-gradient(135deg,#f7f8ff 0%,#f8fbff 52%,#fff8fd 100%); color:var(--ink); }
    header[data-testid="stHeader"] { background:rgba(255,255,255,0); }
    .block-container { padding-top:1.1rem; padding-bottom:2.2rem; max-width:1500px; }
    h1,h2,h3 { color:#172554; letter-spacing:-.4px; }
    p, label, .stMarkdown { color:#263454; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#17264f 0%,#1d3268 100%); }
    [data-testid="stSidebar"] * { color:#f8fafc; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#e0e7ff; }
    [data-testid="stSidebar"] .stRadio > label { color:#c7d2fe; font-weight:800; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap:7px; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.07);
        border-radius:13px; padding:10px 12px; transition:all .2s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:rgba(124,92,255,.35); }
    [data-testid="stSidebar"] div[role="radiogroup"] label p { color:#fff !important; font-weight:700; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child { display:none; }
    [data-testid="stSidebar"] .stButton button { background:linear-gradient(90deg,#7c5cff,#4f7cff); color:#fff; border:0; border-radius:12px; font-weight:800; }
    .stButton button, .stDownloadButton button, .stFormSubmitButton button {
        border-radius:12px !important; font-weight:800 !important; transition:transform .15s ease, box-shadow .15s ease;
    }
    .stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover {
        transform:translateY(-1px); box-shadow:0 8px 20px rgba(91,86,200,.16);
    }
    /* Keep all form text clearly visible while typing (including passwords and autofilled fields). */
    .stTextInput input, .stTextArea textarea, .stDateInput input,
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input, div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        border-radius:11px !important;
        border-color:#dbe4f5 !important;
        background:#ffffff !important;
        background-color:#ffffff !important;
        color:#172554 !important;
        -webkit-text-fill-color:#172554 !important;
        caret-color:#172554 !important;
        opacity:1 !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder,
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color:#64748b !important;
        -webkit-text-fill-color:#64748b !important;
        opacity:1 !important;
    }
    /* Chrome can apply its own dark colours to saved/autofilled values. Override them. */
    input:-webkit-autofill, input:-webkit-autofill:hover,
    input:-webkit-autofill:focus, textarea:-webkit-autofill {
        -webkit-text-fill-color:#172554 !important;
        caret-color:#172554 !important;
        -webkit-box-shadow:0 0 0 1000px #ffffff inset !important;
        box-shadow:0 0 0 1000px #ffffff inset !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        border-radius:11px !important;
        border-color:#dbe4f5 !important;
        background:#ffffff !important;
        color:#172554 !important;
    }
    div[data-testid="stForm"] { background:#fff; border:1px solid #e5eaf7; border-radius:18px; padding:20px; box-shadow:0 6px 22px rgba(30,50,100,.045); }
    div[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,255,255,.96); border:1px solid #e6ebf8 !important; border-radius:21px !important; padding:18px 20px !important; box-shadow:0 7px 23px rgba(35,55,115,.05); margin-bottom:16px; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { border:0 !important; }
    .stTabs [data-baseweb="tab-list"] { gap:8px; background:#edf1ff; border-radius:14px; padding:6px; }
    .stTabs [data-baseweb="tab"] { border-radius:10px; padding:10px 16px; font-weight:800; }
    .stTabs [aria-selected="true"] { background:#fff !important; color:#6045df !important; box-shadow:0 3px 10px #dfe5ff; }
    .hero-banner { display:grid; grid-template-columns:1.1fr .9fr; gap:10px; align-items:center; min-height:245px; padding:25px 30px; border-radius:25px; overflow:hidden; background:linear-gradient(115deg,#dbeafe 0%,#f3e8ff 55%,#fff0f5 100%); border:1px solid #e5e7ff; box-shadow:0 10px 28px rgba(71,85,180,.08); margin-bottom:22px; }
    .hero-eyebrow { display:inline-block; background:rgba(255,255,255,.75); color:#6045df; padding:7px 12px; border-radius:999px; font-size:12px; font-weight:900; letter-spacing:1px; }
    .hero-title { color:#172554; font-size:clamp(28px,3vw,43px); line-height:1.06; font-weight:900; margin:13px 0 10px; }
    .hero-title span { color:#6347df; }
    .hero-subtitle { font-size:16px; color:#465574; margin:0; }
    .hero-art { width:100%; height:220px; background-position:center; background-repeat:no-repeat; background-size:contain; }
    .section-kicker { color:#6d4aff; font-weight:900; text-transform:uppercase; font-size:11px; letter-spacing:1.4px; margin-bottom:4px; }
    .section-title { font-size:23px; font-weight:900; color:#172554; margin:0 0 14px; }
    .metric-card { min-height:122px; border-radius:20px; padding:18px 19px; border:1px solid rgba(255,255,255,.85); box-shadow:0 8px 24px rgba(40,60,120,.055); }
    .metric-top { display:flex; align-items:center; gap:12px; }
    .metric-icon { width:47px; height:47px; display:flex; align-items:center; justify-content:center; border-radius:15px; font-size:25px; background:rgba(255,255,255,.72); }
    .metric-label { font-size:13px; font-weight:900; margin-bottom:4px; }
    .metric-value { font-size:31px; line-height:1.1; font-weight:900; color:#172554; }
    .metric-note { font-size:11px; font-weight:700; margin-top:7px; color:#52617e; }
    .metric-blue { background:linear-gradient(135deg,#dbeafe,#c7e4ff); }
    .metric-green { background:linear-gradient(135deg,#dcfce7,#c7f9d9); }
    .metric-orange { background:linear-gradient(135deg,#ffedd5,#ffe1c4); }
    .metric-purple { background:linear-gradient(135deg,#f3e8ff,#e7d5ff); }
    .panel { background:rgba(255,255,255,.94); border:1px solid #e6ebf8; border-radius:21px; padding:21px; box-shadow:0 7px 23px rgba(35,55,115,.05); margin-bottom:18px; }
    .panel-heading { font-size:19px; font-weight:900; color:#172554; margin:0 0 14px; }
    .panel-subtitle { color:#71809c; font-size:13px; margin-top:-8px; margin-bottom:14px; }
    .progress-row { display:flex; align-items:center; gap:22px; }
    .progress-ring { flex:0 0 140px; width:140px; height:140px; border-radius:50%; display:flex; align-items:center; justify-content:center; }
    .progress-ring-inner { width:104px; height:104px; border-radius:50%; background:white; display:flex; flex-direction:column; align-items:center; justify-content:center; box-shadow:inset 0 0 0 1px #edf0fb; }
    .progress-number { font-size:27px; font-weight:900; color:#172554; line-height:1.1; }
    .progress-caption { font-size:11px; color:#71809c; font-weight:800; }
    .legend-row { display:flex; align-items:center; gap:9px; font-size:13px; font-weight:800; margin:8px 0; color:#344362; }
    .legend-dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
    .deadline-row { display:flex; align-items:center; gap:12px; padding:12px 0; border-bottom:1px solid #edf0f8; }
    .deadline-row:last-child { border-bottom:0; }
    .deadline-icon { width:38px; height:38px; flex:0 0 38px; border-radius:13px; display:flex; align-items:center; justify-content:center; font-size:18px; }
    .deadline-title { font-weight:900; color:#1e2b4d; font-size:14px; }
    .deadline-meta { color:#75829a; font-size:12px; margin-top:3px; }
    .priority-pill { margin-left:auto; border-radius:999px; padding:5px 10px; font-size:11px; font-weight:900; white-space:nowrap; }
    .priority-high { background:#fee2e2; color:#b91c1c; }
    .priority-medium { background:#dbeafe; color:#1d4ed8; }
    .priority-low { background:#dcfce7; color:#15803d; }
    .status-pill { border-radius:999px; padding:5px 9px; font-size:11px; font-weight:900; display:inline-block; }
    .status-completed { background:#dcfce7; color:#15803d; }
    .status-pending { background:#ffedd5; color:#c2410c; }
    .status-in-progress { background:#dbeafe; color:#1d4ed8; }
    .reminder-box { border-radius:13px; padding:12px 14px; margin-bottom:9px; border:1px solid #f0e8ff; background:#faf8ff; }
    .reminder-overdue { background:#fff1f2; border-color:#fecdd3; }
    .reminder-today { background:#fff7ed; border-color:#fed7aa; }
    .reminder-tomorrow { background:#eff6ff; border-color:#bfdbfe; }
    .motivation { border-radius:22px; background:linear-gradient(110deg,#ede9fe,#fce7f3); padding:22px; display:flex; align-items:center; gap:18px; border:1px solid #e9d5ff; min-height:125px; }
    .trophy { font-size:48px; }
    .motivation-title { color:#3b267d; font-size:22px; font-weight:900; margin-bottom:3px; }
    .motivation-text { color:#61577f; font-size:13px; }
    .brand-logo { text-align:center; padding:6px 0 14px; }
    .brand-cap { font-size:40px; }
    .brand-name { font-size:21px; font-weight:900; line-height:1.1; color:#fff; }
    .sidebar-quote { margin-top:22px; border:1px solid rgba(167,139,250,.6); background:rgba(255,255,255,.05); border-radius:18px; padding:16px 12px; text-align:center; color:#fde68a; font-size:16px; font-weight:900; line-height:1.5; }
    .login-shell { background:white; border:1px solid #e7eafe; border-radius:25px; padding:28px; box-shadow:0 16px 45px rgba(45,55,140,.09); }
    .login-brand { background:linear-gradient(145deg,#dbeafe,#f3e8ff,#fff1f2); border-radius:22px; padding:26px; min-height:390px; }
    .calendar-note { color:#64748b; font-size:12px; }
    @media (max-width:900px) { .hero-banner { grid-template-columns:1fr; } .hero-art { height:150px; } .progress-row { flex-wrap:wrap; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe(value):
    """Escape text before placing database values inside our small HTML cards."""
    return html.escape(str(value or ""))


def set_page(page_name):
    st.session_state["navigation"] = page_name
    st.rerun()


def show_metric(icon, label, value, note, colour):
    st.markdown(
        f"""<div class="metric-card metric-{colour}">
        <div class="metric-top"><div class="metric-icon">{icon}</div>
        <div><div class="metric-label">{safe(label)}</div><div class="metric-value">{safe(value)}</div></div></div>
        <div class="metric-note">{safe(note)}</div></div>""",
        unsafe_allow_html=True,
    )


def priority_class(priority):
    return {"High": "priority-high", "Medium": "priority-medium", "Low": "priority-low"}.get(priority, "priority-medium")


def status_class(status):
    return {"Completed": "status-completed", "Pending": "status-pending", "In Progress": "status-in-progress"}.get(status, "status-pending")


def show_deadline(assignment, today):
    due = due_date(assignment)
    label = reminder_text(assignment, today)
    icon = "🚨" if label == "Overdue" else "⏰" if label == "Due today" else "📅"
    kind = "reminder-overdue" if label == "Overdue" else "reminder-today" if label == "Due today" else "reminder-tomorrow"
    st.markdown(
        f"""<div class="deadline-row">
        <div class="deadline-icon" style="background:#f1edff">{icon}</div>
        <div style="flex:1;min-width:0"><div class="deadline-title">{safe(assignment.get('title'))}</div>
        <div class="deadline-meta">{safe(assignment.get('subject'))} · Due {due.isoformat()}</div></div>
        <span class="priority-pill {priority_class(assignment.get('priority'))}">{safe(assignment.get('priority'))}</span>
        </div>""",
        unsafe_allow_html=True,
    )


# -------------------- 1. Login / registration --------------------
if "token" not in st.session_state:
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        st.markdown(
            """<div class="login-brand">
            <div style="font-size:52px">🎓</div>
            <div class="section-kicker">YOUR FRIENDLY STUDY COMPANION</div>
            <div style="font-size:38px;line-height:1.08;font-weight:900;color:#172554;margin:10px 0">Make every<br><span style="color:#6546df">deadline count.</span></div>
            <p style="font-size:16px;color:#52617e">Plan your assignments, track your progress, and feel confident about your studies.</p>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:20px">
              <span style="background:#fff;padding:8px 12px;border-radius:999px;color:#5b45c9;font-weight:800">📊 Progress</span>
              <span style="background:#fff;padding:8px 12px;border-radius:999px;color:#16834b;font-weight:800">🔔 Reminders</span>
              <span style="background:#fff;padding:8px 12px;border-radius:999px;color:#2563eb;font-weight:800">📅 Calendar</span>
            </div></div>""",
            unsafe_allow_html=True,
        )
        if HERO_IMAGE.exists():
            st.image(str(HERO_IMAGE), use_container_width=True)
    with right:
        with st.container(border=True):
            st.markdown("### Welcome to TaskTrack 👋")
            st.caption("Sign in to your own account or create a new student account.")
            login_tab, register_tab = st.tabs(["🔐 Sign in", "✨ Create account"])

            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Email address", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    sign_in = st.form_submit_button("Sign in to dashboard", type="primary", use_container_width=True)
                if sign_in:
                    try:
                        result = api("POST", "/api/auth/login", data={"email": email, "password": password})
                        st.session_state["token"] = result["token"]
                        st.session_state["user"] = result["user"]
                        st.session_state["navigation"] = "🏠 Dashboard"
                        st.rerun()
                    except APIError as error:
                        st.error(str(error))

            with register_tab:
                with st.form("register_form"):
                    name = st.text_input("Full name", placeholder="Your name")
                    new_email = st.text_input("Email address", placeholder="you@example.com")
                    new_password = st.text_input("Password (8+ characters)", type="password")
                    confirm = st.text_input("Confirm password", type="password")
                    register = st.form_submit_button("Create my account", type="primary", use_container_width=True)
                if register:
                    if not name.strip() or not new_email.strip():
                        st.error("Please enter your name and email address.")
                    elif len(new_password) < 8:
                        st.error("Use a password with at least 8 characters.")
                    elif new_password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            result = api("POST", "/api/auth/register", data={
                                "name": name.strip(), "email": new_email.strip(), "password": new_password
                            })
                            st.session_state["token"] = result["token"]
                            st.session_state["user"] = result["user"]
                            st.session_state["navigation"] = "🏠 Dashboard"
                            st.rerun()
                        except APIError as error:
                            st.error(str(error))
            st.markdown("<div style='text-align:center;color:#8a96ad;font-size:12px;margin-top:8px'>🔒 Secure sign-in · Your assignments are private</div>", unsafe_allow_html=True)
    st.stop()


# -------------------- 2. Load the signed-in student's data --------------------
token = st.session_state["token"]
user = st.session_state.get("user", {})
NAV_ITEMS = ["🏠 Dashboard", "📚 My Assignments", "➕ Add Assignment", "📅 Calendar", "👤 Profile"]
st.session_state.setdefault("navigation", NAV_ITEMS[0])

with st.sidebar:
    st.markdown(
        """<div class="brand-logo"><div class="brand-cap">🎓</div>
        <div class="brand-name">Student<br>Assignment Tracker</div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div style='background:rgba(255,255,255,.08);border-radius:14px;padding:12px;margin-bottom:14px'><div style='font-weight:900'>Welcome, {safe(user.get('name', 'Student'))} 👋</div><div style='font-size:11px;color:#c7d2fe;overflow-wrap:anywhere'>{safe(user.get('email', ''))}</div></div>", unsafe_allow_html=True)
    selected_page = st.radio("YOUR WORKSPACE", NAV_ITEMS, key="navigation", label_visibility="visible")
    st.markdown("<div class='sidebar-quote'>Dream Big ✨<br>Study Hard 📚<br>Achieve More!</div>", unsafe_allow_html=True)
    st.divider()
    st.caption("Student workspace · Express APIs · MongoDB")
    if st.button("🚪 Log out", use_container_width=True):
        try:
            api("POST", "/api/auth/logout", token)
        except APIError:
            pass
        st.session_state.clear()
        st.rerun()

try:
    assignments = api("GET", "/api/assignments", token)
except APIError as error:
    st.error(str(error))
    st.info("Check that MongoDB is running and the Node.js backend is running in its own terminal.")
    st.stop()

# -------------------- 3. Common calculations --------------------
today = date.today()
stats = progress_stats(assignments, today)
status_counts = Counter(a.get("status", "Pending") for a in assignments)
priority_counts = Counter(a.get("priority", "Medium") for a in assignments)
incomplete = [a for a in assignments if a.get("status") != "Completed"]
overdue = sorted([a for a in incomplete if due_date(a) < today], key=due_date)
upcoming = sorted([a for a in incomplete if due_date(a) >= today], key=due_date)
reminders = sorted([a for a in incomplete if reminder_text(a, today)], key=due_date)
pending_count = status_counts.get("Pending", 0)
in_progress_count = status_counts.get("In Progress", 0)
high_priority_count = sum(a.get("priority") == "High" and a.get("status") != "Completed" for a in assignments)


# -------------------- 4. Dashboard --------------------
if selected_page == "🏠 Dashboard":
    hero_image_data = ""
    if HERO_IMAGE.exists():
        import base64
        hero_image_data = base64.b64encode(HERO_IMAGE.read_bytes()).decode("ascii")
    st.markdown(
        f"""<div class="hero-banner">
          <div><span class="hero-eyebrow">YOUR STUDY SPACE ✨</span>
          <div class="hero-title">Welcome back, {safe(user.get('name', 'Student')).split(' ')[0]}!<br><span>Your Assignment Dashboard</span></div>
          <p class="hero-subtitle">Stay organized. Meet deadlines. Excel in your studies!</p>
          <div style="margin-top:16px;color:#5f6685;font-size:12px;font-weight:800">📅 {today.strftime('%A, %d %B %Y')}</div></div>
          <div class="hero-art" style="background-image:url('data:image/png;base64,{hero_image_data}')"></div>
        </div>""",
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4, gap="medium")
    with metric_cols[0]:
        show_metric("🗂️", "Total assignments", stats["total"], "Everything in one place", "blue")
    with metric_cols[1]:
        show_metric("✅", "Completed", stats["completed"], "Great work — keep going!", "green")
    with metric_cols[2]:
        show_metric("⏳", "Pending", pending_count + in_progress_count, f"{pending_count} pending · {in_progress_count} in progress", "orange")
    with metric_cols[3]:
        show_metric("⚡", "High priority", high_priority_count, f"{stats['overdue']} overdue assignment(s)", "purple")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    left, right = st.columns([0.92, 1.08], gap="large")
    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-heading">📈 Your assignment progress</div><div class="panel-subtitle">Every small step counts. Keep moving forward!</div>', unsafe_allow_html=True)
            percent = stats["percent"]
            st.markdown(
                f"""<div class="progress-row"><div class="progress-ring" style="background:conic-gradient(#22c55e {percent}%, #e5e7eb 0)">
                <div class="progress-ring-inner"><div class="progress-number">{percent}%</div><div class="progress-caption">COMPLETED</div></div></div>
                <div style="flex:1"><div class="legend-row"><span class="legend-dot" style="background:#22c55e"></span>Completed <span style="margin-left:auto">{stats['completed']}</span></div>
                <div class="legend-row"><span class="legend-dot" style="background:#f59e0b"></span>Pending <span style="margin-left:auto">{pending_count}</span></div>
                <div class="legend-row"><span class="legend-dot" style="background:#3b82f6"></span>In progress <span style="margin-left:auto">{in_progress_count}</span></div>
                <div style="color:#71809c;font-size:12px;margin-top:13px">{stats['completed']} of {stats['total']} assignments completed</div></div></div>""",
                unsafe_allow_html=True,
            )

        with st.container(border=True):
            st.markdown('<div class="panel-heading">🔔 Deadline reminders</div>', unsafe_allow_html=True)
            if not reminders:
                st.success("You're all caught up! No urgent deadlines.")
            else:
                for task in reminders[:5]:
                    label = reminder_text(task, today)
                    kind = "reminder-overdue" if label == "Overdue" else "reminder-today" if label == "Due today" else "reminder-tomorrow"
                    icon = "🚨" if label == "Overdue" else "⏰" if label == "Due today" else "📅"
                    st.markdown(f"<div class='reminder-box {kind}'><div style='font-weight:900'>{icon} {safe(task.get('title'))}</div><div style='font-size:12px;color:#64748b;margin-top:3px'>{safe(label)} · Due {due_date(task).isoformat()}</div></div>", unsafe_allow_html=True)

    with right:
        with st.container(border=True):
            st.markdown('<div class="panel-heading">📅 Upcoming deadlines</div><div class="panel-subtitle">Your next tasks, sorted by due date</div>', unsafe_allow_html=True)
            if not upcoming:
                st.info("No upcoming assignments. Enjoy the breathing room!")
            else:
                for task in upcoming[:5]:
                    show_deadline(task, today)

        with st.container(border=True):
            st.markdown('<div class="panel-heading">🚨 Overdue assignments</div><div class="panel-subtitle">These deadlines have passed and still need attention.</div>', unsafe_allow_html=True)
            if not overdue:
                st.success("No overdue assignments. Amazing!")
            else:
                for task in overdue[:5]:
                    st.markdown(f"<div class='deadline-row'><div class='deadline-icon' style='background:#fee2e2'>⚠️</div><div style='flex:1'><div class='deadline-title'>{safe(task.get('title'))}</div><div class='deadline-meta'>{safe(task.get('subject'))} · Was due {due_date(task).isoformat()}</div></div><span class='priority-pill priority-high'>OVERDUE</span></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-kicker">SEE YOUR MOMENTUM</div><div class="section-title">Performance at a glance</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        with st.container(border=True):
            st.markdown('<div class="panel-heading">📊 Assignment status</div>', unsafe_allow_html=True)
            status_df = pd.DataFrame({"Status": ["Completed", "In Progress", "Pending"], "Assignments": [status_counts.get("Completed", 0), status_counts.get("In Progress", 0), status_counts.get("Pending", 0)]})
            st.bar_chart(status_df, x="Status", y="Assignments", color="#7c5cff")
    with chart_right:
        with st.container(border=True):
            st.markdown('<div class="panel-heading">🎯 Priority breakdown</div>', unsafe_allow_html=True)
            priority_df = pd.DataFrame({"Priority": ["High", "Medium", "Low"], "Assignments": [priority_counts.get("High", 0), priority_counts.get("Medium", 0), priority_counts.get("Low", 0)]})
            st.bar_chart(priority_df, x="Priority", y="Assignments", color="#38bdf8")

    st.markdown('<div class="motivation"><div class="trophy">🏆</div><div><div class="motivation-title">Keep going!</div><div class="motivation-text">You are building great study habits, one assignment at a time.</div></div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    quick1, quick2, quick3 = st.columns(3)
    with quick1:
        if st.button("➕ Add assignment", use_container_width=True):
            set_page("➕ Add Assignment")
    with quick2:
        if st.button("📚 View all assignments", use_container_width=True):
            set_page("📚 My Assignments")
    with quick3:
        if st.button("📄 Download PDF report", use_container_width=True):
            st.session_state["download_report_hint"] = True
            st.rerun()
    if st.session_state.pop("download_report_hint", False):
        st.download_button("⬇️ Download your assignment report", data=make_pdf(assignments, user), file_name="TaskTrack_Assignment_Report.pdf", mime="application/pdf", use_container_width=True)


# -------------------- 5. Add assignment --------------------
elif selected_page == "➕ Add Assignment":
    st.markdown('<div class="section-kicker">BUILD YOUR PLAN</div><div class="section-title">➕ Add a new assignment</div>', unsafe_allow_html=True)
    st.caption("Add the details once and TaskTrack will help you keep an eye on the deadline.")
    form_left, form_right = st.columns([1.25, 0.75], gap="large")
    with form_left:
        with st.form("add_assignment", clear_on_submit=True):
            title = st.text_input("Assignment title", placeholder="e.g. Java mini project")
            subject = st.text_input("Subject", placeholder="e.g. Java Programming")
            description = st.text_area("Description (optional)", placeholder="What do you need to complete?")
            due = st.date_input("Due date", value=today + timedelta(days=1), min_value=date(2000, 1, 1))
            field1, field2 = st.columns(2)
            with field1:
                priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)
            with field2:
                status = st.selectbox("Initial status", ["Pending", "In Progress", "Completed"], index=0)
            submitted = st.form_submit_button("💾 Save assignment", type="primary", use_container_width=True)
        if submitted:
            if not title.strip() or not subject.strip():
                st.error("Title and subject are required.")
            else:
                try:
                    api("POST", "/api/assignments", token, {
                        "title": title.strip(), "subject": subject.strip(), "description": description.strip(),
                        "dueDate": due.isoformat(), "priority": priority, "status": status,
                    })
                    st.success("Assignment saved to MongoDB!")
                    st.rerun()
                except APIError as error:
                    st.error(str(error))
    with form_right:
        st.markdown('<div class="panel"><div style="font-size:40px">🪄</div><div class="panel-heading">A little planning goes a long way</div><p style="color:#64748b">Use a clear title, choose the real deadline, and set the priority so you know what to focus on first.</p><div class="reminder-box reminder-today">🔔 TaskTrack will flag deadlines due today or tomorrow.</div><div class="reminder-box">📊 Your dashboard updates when you save.</div></div>', unsafe_allow_html=True)


# -------------------- 6. Assignment list and editing --------------------
elif selected_page == "📚 My Assignments":
    st.markdown('<div class="section-kicker">YOUR TASK LIST</div><div class="section-title">📚 My assignments</div>', unsafe_allow_html=True)
    search_col, filter_col = st.columns([1.4, 0.8])
    with search_col:
        search = st.text_input("🔎 Search assignments", placeholder="Search by title or subject...").strip().lower()
    with filter_col:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "In Progress", "Completed"])
    visible = [a for a in assignments if (search in a.get("title", "").lower() or search in a.get("subject", "").lower() or search in a.get("description", "").lower()) and (status_filter == "All" or a.get("status") == status_filter)]
    st.caption(f"Showing {len(visible)} of {len(assignments)} assignment(s)")
    if not visible:
        st.info("No assignments match your search. Try a different keyword or add a new assignment.")
    for task in sorted(visible, key=due_date):
        task_id = str(task["_id"])
        label = f"{task.get('title', 'Assignment')}  ·  {task.get('subject', '')}  ·  {due_date(task).isoformat()}"
        with st.expander(label, expanded=False):
            detail_left, detail_right = st.columns([1.4, 0.8])
            with detail_left:
                st.write(task.get("description") or "No description added.")
                st.markdown(f"<span class='status-pill {status_class(task.get('status'))}'>{safe(task.get('status'))}</span> &nbsp; <span class='priority-pill {priority_class(task.get('priority'))}'>{safe(task.get('priority'))} priority</span>", unsafe_allow_html=True)
                st.caption(f"Due date: {due_date(task).isoformat()}")
            with detail_right:
                new_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(task.get("status", "Pending")), key="status_" + task_id)
                if st.button("Update status", key="quick_" + task_id, use_container_width=True):
                    try:
                        api("PATCH", f"/api/assignments/{task_id}/status", token, {"status": new_status})
                        st.success("Status updated.")
                        st.rerun()
                    except APIError as error:
                        st.error(str(error))
            with st.form("edit_" + task_id):
                st.markdown("**Edit assignment details**")
                edit_title = st.text_input("Title", value=task.get("title", ""), key="title_" + task_id)
                edit_subject = st.text_input("Subject", value=task.get("subject", ""), key="subject_" + task_id)
                edit_description = st.text_area("Description", value=task.get("description", ""), key="description_" + task_id)
                edit_due = st.date_input("Due date", value=due_date(task), key="due_" + task_id)
                edit_priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(task.get("priority", "Medium")), key="priority_" + task_id)
                save_edit = st.form_submit_button("Save changes")
            if save_edit:
                if not edit_title.strip() or not edit_subject.strip():
                    st.error("Title and subject are required.")
                else:
                    try:
                        api("PUT", f"/api/assignments/{task_id}", token, {
                            "title": edit_title.strip(), "subject": edit_subject.strip(), "description": edit_description.strip(),
                            "dueDate": edit_due.isoformat(), "priority": edit_priority, "status": new_status,
                        })
                        st.success("Assignment updated.")
                        st.rerun()
                    except APIError as error:
                        st.error(str(error))
            confirm_delete = st.checkbox("I want to delete this assignment", key="confirm_delete_" + task_id)
            if st.button("🗑️ Delete assignment", key="delete_" + task_id, disabled=not confirm_delete):
                try:
                    api("DELETE", f"/api/assignments/{task_id}", token)
                    st.success("Assignment deleted.")
                    st.rerun()
                except APIError as error:
                    st.error(str(error))


# -------------------- 7. Clickable monthly calendar --------------------
elif selected_page == "📅 Calendar":
    st.markdown('<div class="section-kicker">SEE THE MONTH AHEAD</div><div class="section-title">📅 Assignment calendar</div>', unsafe_allow_html=True)
    month_col, year_col = st.columns([1, 1])
    with month_col:
        month = st.selectbox("Month", range(1, 13), index=today.month - 1, format_func=lambda number: calendar.month_name[number])
    with year_col:
        year = int(st.number_input("Year", min_value=2020, max_value=2100, value=today.year, step=1))
    date_map = {}
    for task in assignments:
        date_map.setdefault(due_date(task), []).append(task)
    with st.container(border=True):
        weekdays = st.columns(7)
        for col, weekday in zip(weekdays, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            col.markdown(f"<div style='text-align:center;font-weight:900;color:#6d4aff;padding:8px 0'>{weekday}</div>", unsafe_allow_html=True)
        for week in calendar.monthcalendar(year, month):
            day_cols = st.columns(7)
            for col, day in zip(day_cols, week):
                if day == 0:
                    col.markdown("<div style='height:54px'></div>", unsafe_allow_html=True)
                    continue
                chosen = date(year, month, day)
                count = len(date_map.get(chosen, []))
                label = f"{day}  📌{count}" if count else str(day)
                if col.button(label, key="calendar_" + chosen.isoformat(), use_container_width=True, help=f"{count} assignment(s) due on this date"):
                    st.session_state["chosen_day"] = chosen.isoformat()
    st.markdown("<div class='calendar-note'>💡 Dates with 📌 show how many assignments are due. Select a date to see its tasks.</div>", unsafe_allow_html=True)
    selected_day_text = st.session_state.get("chosen_day")
    if selected_day_text:
        try:
            selected_day = date.fromisoformat(selected_day_text)
        except ValueError:
            selected_day = None
        if selected_day:
            with st.container(border=True):
                st.markdown(f"<div class='panel-heading'>🗓️ Assignments on {selected_day.isoformat()}</div>", unsafe_allow_html=True)
                selected_tasks = date_map.get(selected_day, [])
                if not selected_tasks:
                    st.info("No assignments due on this date.")
                for task in selected_tasks:
                    st.markdown(f"<div class='deadline-row'><div class='deadline-icon' style='background:#ede9fe'>📚</div><div style='flex:1'><div class='deadline-title'>{safe(task.get('title'))}</div><div class='deadline-meta'>{safe(task.get('subject'))} · {safe(task.get('status'))}</div></div><span class='priority-pill {priority_class(task.get('priority'))}'>{safe(task.get('priority'))}</span></div>", unsafe_allow_html=True)


# -------------------- 8. Student profile --------------------
elif selected_page == "👤 Profile":
    st.markdown('<div class="section-kicker">YOUR STUDENT DETAILS</div><div class="section-title">👤 My profile</div>', unsafe_allow_html=True)
    profile_left, profile_right = st.columns([1, 1.25], gap="large")
    with profile_left:
        with st.container(border=True):
            st.markdown(f"""<div style="text-align:center;padding:8px"><div style="font-size:64px">🧑‍🎓</div><div style="font-size:23px;font-weight:900;color:#172554">{safe(user.get('name', 'Student'))}</div><div style="color:#71809c;font-size:13px;overflow-wrap:anywhere">{safe(user.get('email', ''))}</div><div style="margin-top:18px"><span class="status-pill status-completed">Verified account session</span></div></div>""", unsafe_allow_html=True)
    with profile_right:
        with st.form("profile_form"):
            name = st.text_input("Full name", value=user.get("name", ""))
            st.text_input("Email address", value=user.get("email", ""), disabled=True)
            roll_no = st.text_input("Roll number", value=user.get("rollNo", ""))
            department = st.text_input("Department", value=user.get("department", ""))
            year_text = st.text_input("Year of study", value=user.get("year", ""))
            semester = st.text_input("Semester", value=user.get("semester", ""))
            save_profile = st.form_submit_button("💾 Save profile", type="primary", use_container_width=True)
        if save_profile:
            try:
                result = api("PUT", "/api/auth/profile", token, {
                    "name": name.strip(), "rollNo": roll_no.strip(), "department": department.strip(),
                    "year": year_text.strip(), "semester": semester.strip(),
                })
                st.session_state["user"] = result.get("profile", user)
                st.success("Profile updated successfully.")
                st.rerun()
            except APIError as error:
                st.error(str(error))

    with st.container(border=True):
        st.markdown('<div class="panel-heading">📄 Your assignment report</div><p style="color:#64748b">Download a PDF summary to keep a record or show your project results during the demo.</p>', unsafe_allow_html=True)
        st.download_button("⬇️ Download PDF report", data=make_pdf(assignments, user), file_name="TaskTrack_Assignment_Report.pdf", mime="application/pdf")

st.markdown("<div style='text-align:center;color:#94a3b8;font-size:11px;padding:18px 0 0'>TaskTrack · Stay organized, meet deadlines, and make progress 🌟</div>", unsafe_allow_html=True)
