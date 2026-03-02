# 🎬 FilmCollab — Collaborative Film Aspects Web App

A beginner-friendly Flask + MySQL web application for managing collaborative film projects.

---

## 📁 Project Structure

```
film_app/
│
├── app.py                   ← Flask backend (all routes)
├── schema.sql               ← MySQL database setup
├── requirements.txt         ← Python packages needed
│
├── templates/               ← HTML pages (Jinja2)
│   ├── base.html            ← Shared layout (navbar, footer)
│   ├── index.html           ← Home — all projects
│   ├── register.html        ← User registration
│   ├── login.html           ← User login
│   ├── project_detail.html  ← View a project + aspects + contributors
│   ├── add_project.html     ← Create a new project
│   ├── edit_project.html    ← Edit a project
│   └── add_aspect.html      ← Add a film aspect
│
└── static/
    ├── css/style.css        ← All styles
    └── js/validate.js       ← Form validation
```

---

## ⚙️ Setup Instructions

### Step 1 — Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2 — Set up MySQL database
Open MySQL and run:
```bash
mysql -u root -p < schema.sql
```
Or copy-paste the contents of `schema.sql` into MySQL Workbench / phpMyAdmin.

### Step 3 — Configure database credentials
Open `app.py` and update the `get_db()` function:
```python
conn = mysql.connector.connect(
    host='localhost',
    user='root',       # ← Your MySQL username
    password='',       # ← Your MySQL password
    database='film_db'
)
```

### Step 4 — Run the app
```bash
python app.py
```

Open your browser and go to: **http://localhost:5000**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Register / Login | User authentication with password hashing |
| 🎬 Add Projects | Create film projects with title, genre, description |
| 🎭 Add Aspects | Add script, direction, music, editing, etc. |
| 🤝 Join Projects | Any logged-in user can join a project as contributor |
| 📋 View All | Browse all projects, see contributors and aspects |
| ✏️ Edit / Delete | Owners can edit or delete their projects |

---

## 🗃️ Database Tables

| Table | Purpose |
|---|---|
| `users` | Stores registered users |
| `projects` | Film projects created by users |
| `aspects` | Individual film aspects (script, music, etc.) |
| `contributors` | Many-to-many: which users joined which projects |

---

## 🛠️ Technologies Used
- **Python 3** + **Flask** — web framework
- **MySQL** — relational database
- **Jinja2** — HTML templating (built into Flask)
- **HTML + CSS** — frontend layout
- **JavaScript** — client-side form validation only
