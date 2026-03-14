# User Guide

Complete usage instructions for ICS-LogQueryGPT.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Login and Sign Up](#login-and-sign-up)
- [Home Page](#home-page)
- [Query Logs](#query-logs)
- [Analytics](#analytics)
- [Export Center](#export-center)
- [Admin Dashboard](#admin-dashboard)
- [Benchmark](#benchmark)
- [Alert System](#alert-system)

---

## Getting Started

After running `streamlit run src/ui/app.py`, open your browser at:

```
http://localhost:8501
```

You will see the Login page. Use the default admin credentials or sign up for a new account.

---

## Login and Sign Up

### Login

1. Enter your username and password
2. Click **Sign In**
3. Admin users are redirected to the Admin Dashboard
4. All other users are redirected to the Home page

### Sign Up

1. Click the **Sign Up** tab
2. Enter a username (minimum 3 characters)
3. Enter a password (minimum 6 characters)
4. Click **Create Account**
5. Your account is created with the `analyst` role

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |

---

## Home Page

The home page shows a summary of your current session:

- **Welcome banner** with your username
- **Session Info** card — role, status, sign-in time
- **System Overview** — logs indexed, active users, queries this session, last response time
- **Feature cards** — quick links to Query Logs, Analytics, Export
- **Recent Activity** — your last 5 queries from this session (empty if no queries yet)

The sidebar shows your username, role badge, and navigation buttons. Admin users see an additional **Admin Dashboard** button.

---

## Query Logs

This is the main page for querying your ICS security logs.

### Selecting a Dataset

Use the **Query Source** toggle at the top:
- **Dataset (HDFS)** — 2,000 HDFS distributed system logs
- **Dataset (BGL)** — 2,000 BlueGene/L supercomputer logs
- **Upload Your Own File** — CSV or TXT log file

To switch between HDFS and BGL, use the Dataset dropdown in the left sidebar.

### Uploading Your Own File

1. Select **Upload Your Own File** in the Query Source toggle
2. Click **Browse files** and select a CSV or TXT file
3. Wait 5–8 seconds for indexing (shown with progress bar)
4. Type your query and click **Analyze**

### Query Modes

Select your analysis depth in the sidebar:

| Mode | Speed | Detail | Best For |
|------|-------|--------|----------|
| **Fast** | 1–3s | Overview | Quick checks |
| **Detailed** | 3–6s | Full analysis | Investigation |
| **Deep Analysis** | 5–10s | Comprehensive | Full audit |

### Running a Query

1. Type your question in the **Natural Language Query** box
2. Click **Analyze**
3. Wait for the AI response
4. If critical keywords are detected, a red/yellow alert banner appears

### Example Questions to Try

**HDFS:**
- Show all failed login attempts
- Are there any brute force attacks?
- Which IP addresses have the most failed connections?
- Show me all blocked connections
- What are the most common error types?

**BGL:**
- Are there any hardware failures?
- Show all fatal errors
- What caused the most system crashes?
- Are there any memory failures?
- Show me all critical system alerts

### Actions

- **Clear** — clears the current query and result
- **History** — shows your last 10 queries this session

### Alert Banner

When the AI response contains critical security keywords, a banner appears:
- **Red** = CRITICAL severity
- **Yellow** = WARNING severity
- Shows whether the alert email was sent successfully

---

## Analytics

The analytics page shows charts based on your actual query session.

**Run at least 3–5 queries before visiting Analytics to see meaningful data.**

Charts shown:
- **Activity Timeline** — queries over time
- **Query Mode Breakdown** — pie chart of Fast/Detailed/Deep Analysis usage
- **Dataset Usage** — bar chart of HDFS vs BGL vs Upload queries
- **Response Time Chart** — how long each query took

The sidebar shows the same filters (Protocol, Time Range) which can be used to narrow down the view.

---

## Export Center

The export page lets you download your query data.

### Data Preview

Shows your actual query history from this session as a table. If no queries have been run yet, it shows sample data with a label indicating it is not real.

### Export Options

1. Select **Export Format** from the sidebar (CSV, JSON, Markdown, Plain Text)
2. Toggle which columns to include (Metadata, Timestamps, Source IPs, Severity)
3. Click **Download** to save the file

Each download is logged in the **Export History** section at the bottom.

### Export Templates

Three pre-configured templates for common reporting needs:

| Template | Contents | Best For |
|----------|----------|----------|
| **Security Report** | Queries + AI answers | Security incident documentation |
| **Traffic Analysis** | Query timeline + sources + modes | Network forensics |
| **Incident Report** | Full log with response times | Compliance filing |

Templates are disabled until you have run at least one query.

### Scheduled Exports

Configure recurring automated exports:
1. Set **Frequency** (Daily/Weekly/Monthly/Every 6 Hours)
2. Set **Time (UTC)**
3. Set **Export Format**
4. Enter **Delivery Email**
5. Check **Enable scheduled export**
6. Click **Save Schedule**

The Schedule Status panel updates to reflect your selections.

---

## Admin Dashboard

Available only when logged in as `admin`.

Navigate here directly after admin login, or via the **Admin Dashboard** button in any sidebar.

### Tab 1: User Management

Shows all registered users with:
- Username and ID
- Role (Admin/Analyst/Viewer)
- Last login time
- Active/Disabled status
- Enable/Disable button (not available for the admin account)

### Tab 2: Activity Log

Shows the last 100 login sessions with:
- Username
- Role
- Login time
- Last activity time
- Session status (Active/Ended)

Click **Refresh Activity Log** to reload.

### Tab 3: Create User

Create new user accounts with role assignment:
1. Enter username (minimum 3 characters)
2. Enter password (minimum 6 characters)
3. Select role: **Admin**, **Analyst**, or **Viewer**
4. Click **Create User**

**Role Permissions:**
- **Admin** — full access including Admin Dashboard and Benchmark
- **Analyst** — can query logs, view analytics, export results
- **Viewer** — read-only access, can view results but not query

### Benchmark Access

The **Benchmark** button in the Admin Dashboard sidebar links to the Benchmark page. This page is only accessible by admins.

---

## Benchmark

Available only to admins via the Admin Dashboard sidebar.

### Running a Benchmark

1. Navigate to Benchmark via Admin Dashboard → Benchmark button
2. Click **Run Full Benchmark**
3. Wait 1–2 minutes (8 queries × Groq API call each)
4. Results appear automatically

### What Gets Measured

**Generation Metrics (Answer Quality):**
- BLEU, ROUGE-1, ROUGE-2, ROUGE-L — how well AI answers match reference answers

**Retrieval Metrics (Log Retrieval Quality):**
- Precision@5 — of top-5 retrieved logs, how many were relevant
- Recall@5 — how many relevant logs appear in top-5
- MRR — Mean Reciprocal Rank, how high the first relevant log ranks

### Exporting Results

Download benchmark results as:
- **CSV Report** — per-question scores table
- **JSON Summary** — averaged metrics for paper/report use

---

## Alert System

The alert system runs automatically after every query. No manual action is needed.

### How It Works

1. You run a query and receive an AI answer
2. The system scans the answer for critical keywords
3. If found, a banner appears above the response
4. An HTML email is sent instantly to the configured recipient

### Alert Email Contents

- Severity level (CRITICAL or WARNING)
- The query that triggered the alert
- AI answer summary
- Dataset, response time, triggering user, timestamp

### Configuring Alerts

Edit your `.env` file:
```
ALERT_EMAIL=your_gmail@gmail.com
ALERT_EMAIL_PASSWORD=your_16char_app_password
ALERT_RECIPIENT=recipient@gmail.com
```

The App Password must be generated from Google Account → Security → App Passwords. Your regular Gmail password will not work.

---

## Tips

- Run several queries before visiting Analytics or Export — both pages are more useful with real data
- Use **Fast** mode for quick exploration, **Detailed** for actual analysis
- The query history is session-based — it resets when you restart the app
- Admin users can create new analyst or viewer accounts from the Admin Dashboard
- The alert system only emails on CRITICAL/WARNING keyword detection — normal queries do not send emails

---

**Version:** 1.0.0 | **Last Updated:** March 2026
