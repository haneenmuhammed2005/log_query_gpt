# log_query_gpt

A Natural Language Log Query System that aims to make large-scale system
and application logs easier to understand using AI-based techniques.

This project focuses on exploring how modern NLP models and vector-based
retrieval can be applied to log analysis in an academic and learning-oriented
setting.

---

## 🎯 Project Objective

System logs are usually unstructured, verbose, and difficult to analyze using
traditional keyword search.  
The objective of this project is to design a system that can:

- Understand log data semantically
- Allow users to query logs using natural language
- Retrieve relevant log entries based on meaning, not just keywords

This repository is being developed collaboratively as a learning and
research-focused project.

---

## 📁 Repository Overview

- The main project structure is maintained in a separate branch.
- Development happens in individual branches.
- The `main` branch is kept **stable and clean**.

---

## ⚠️ IMPORTANT — TEAM WORKING INSTRUCTIONS

Please read and follow the instructions below carefully.  
Since all team members are beginners, **this workflow is mandatory**.

---

## 🚫 RULE 1 — DO NOT WORK ON `main`

- ❌ Do NOT write code on `main`
- ❌ Do NOT commit directly to `main`
- ❌ Do NOT merge into `main`

The `main` branch is reserved only for **final, reviewed code**.

---

## 🌱 BASE BRANCH FOR ALL DEVELOPMENT

All development must start from the branch:

### 👉 `structure-setup`

This branch contains:
- The base project folder structure
- Initial setup files
- Common starting point for everyone

---

## 👥 TEAM MEMBERS & ROLES

- **Haneen** — Project lead and final integration  
- **Kripa** — Development and feature work  
- **Krishnendu** — Development and feature work  

---

## 🪜 STEP-BY-STEP: HOW EACH TEAM MEMBER SHOULD WORK

### STEP 1: Clone the repository (only once)

```bash
git clone https://github.com/haneenmuhammed2005/log_query_gpt.git
cd log_query_gpt
STEP 2: Switch to the base branch
bash
Copy code
git fetch
git checkout structure-setup
Confirm you are NOT on main:

bash
Copy code
git branch

STEP 3: Create your OWN branch from structure-setup
Each member must create a separate branch.

Kripa
bash
Copy code
git checkout -b kripa-work
Krishnendu
bash
Copy code
git checkout -b krishnendu-work
Haneen
bash
Copy code
git checkout -b haneen-work
STEP 4: Work only in your branch
Write code

Save files

Commit regularly

Example:

bash
Copy code
git add .
git commit -m "Add preprocessing logic"
git push -u origin <your-branch-name>
🔁 MERGING RULES (VERY IMPORTANT)
❌ No one merges directly into main

✔ Correct merge flow:

bash
Copy code
your-branch → structure-setup → main
Kripa and Krishnendu push their own branches

Haneen reviews and merges changes into structure-setup

Only after everything is stable, structure-setup is merged into main

🛑 COMMON MISTAKES TO AVOID
Working directly on main

Creating branches from main

Merging without discussion

Force-pushing when unsure

If confused at any point:
👉 STOP and ask before proceeding