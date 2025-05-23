# Neofi - Event Scheduler API

Neofi is a backend service built using **FastAPI**, **SQLAlchemy**, and **SQLite** that allows users to manage and
collaborate on events. The system supports features like user roles (Owner, Editor, Viewer), event sharing, versioning,
and rollback functionality.

---

## 🚀 Live Demo

The app is live and hosted on **Render**.  
👉 [Swagger Docs](https://neofi-oma8.onrender.com/docs)

---

## 🚀 Features

- ✅ User Authentication (token-based)
- 📅 Event Management (create, update, delete, list)
- 👥 Role-Based Access Control (RBAC)
- 📤 Share Events with Other Users
- 🧾 View and Rollback Event Version History
- 🛡️ Secure input validation and permission checks

---

## 🏗️ Tech Stack

- **FastAPI** – modern, fast web framework
- **SQLAlchemy** – ORM for database interactions
- **SQLite** – lightweight file-based database
- **Pydantic** – data validation and serialization
- **Python 3.10+**

---

## 📌 Note on Async

> This project can benefit significantly from asynchronous operations (`async def` endpoints, async database calls,
> etc.).  
> **However, since SQLite is used**, which has limited async support, the async implementation has not been added yet.

For production or high-load scenarios, it’s recommended to switch to **PostgreSQL** or **MySQL** and update to **async
SQLAlchemy with async FastAPI** routes.

---

## 🔐 Security Measures

- 🔒 OAuth2 with JWT authentication
- ✅ Strict Pydantic input validation
- 🔐 Role-based authorization at every endpoint
- 🚫 Sensitive data never stored in plain text

---

## Setting up Environment

To create and activate the conda environment from the provided `environment.yml` file, run:

```bash
conda env create -f environment.yml
conda activate your_env_name

---



