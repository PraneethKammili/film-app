# ============================================
# Collaborative Film Aspects Web App
# Backend: Flask + MySQL
# ============================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'film_secret_key_123'  # Change this in production!

# ── Database Connection ──────────────────────
def get_db():
    """Create and return a MySQL database connection."""
    conn = mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
        port=int(os.environ.get("MYSQLPORT"))
    )
    return conn


# ── Helper: Check if user is logged in ──────
def login_required():
    return 'user_id' not in session


# ════════════════════════════════════════════
# AUTH ROUTES
# ════════════════════════════════════════════

@app.route('/')
def index():
    """Home page — show all projects."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.username AS owner_name,
               COUNT(DISTINCT c.user_id) AS contributor_count
        FROM projects p
        JOIN users u ON p.owner_id = u.id
        LEFT JOIN contributors c ON c.project_id = p.id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """)
    projects = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', projects=projects)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']

        hashed = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed)
            )
            db.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists.', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']   = user['id']
            session['username']  = user['username']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out current user."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ════════════════════════════════════════════
# PROJECT ROUTES
# ════════════════════════════════════════════

@app.route('/project/add', methods=['GET', 'POST'])
def add_project():
    """Add a new film project."""
    if login_required():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title       = request.form['title'].strip()
        genre       = request.form['genre'].strip()
        description = request.form['description'].strip()
        owner_id    = session['user_id']

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO projects (title, genre, description, owner_id) VALUES (%s, %s, %s, %s)",
            (title, genre, description, owner_id)
        )
        project_id = cursor.lastrowid
        # Owner automatically becomes a contributor
        cursor.execute(
            "INSERT INTO contributors (project_id, user_id, role) VALUES (%s, %s, %s)",
            (project_id, owner_id, 'Owner')
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Project created successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    return render_template('add_project.html')


@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """View a single project with its aspects and contributors."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get project info
    cursor.execute("""
        SELECT p.*, u.username AS owner_name
        FROM projects p
        JOIN users u ON p.owner_id = u.id
        WHERE p.id = %s
    """, (project_id,))
    project = cursor.fetchone()

    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))

    # Get aspects
    cursor.execute("""
        SELECT a.*, u.username AS contributor_name
        FROM aspects a
        LEFT JOIN users u ON a.assigned_to = u.id
        WHERE a.project_id = %s
        ORDER BY a.created_at
    """, (project_id,))
    aspects = cursor.fetchall()

    # Get contributors
    cursor.execute("""
        SELECT c.role, c.joined_at, u.username
        FROM contributors c
        JOIN users u ON c.user_id = u.id
        WHERE c.project_id = %s
        ORDER BY c.joined_at
    """, (project_id,))
    contributors = cursor.fetchall()

    cursor.close()
    db.close()

    # Check if current user is already a contributor
    is_contributor = False
    if 'user_id' in session:
        is_contributor = any(
            c['username'] == session['username'] for c in contributors
        )

    return render_template('project_detail.html',
                           project=project,
                           aspects=aspects,
                           contributors=contributors,
                           is_contributor=is_contributor)


@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit a project (owner only)."""
    if login_required():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()

    if not project or project['owner_id'] != session['user_id']:
        flash('You are not authorized to edit this project.', 'error')
        cursor.close()
        db.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        title       = request.form['title'].strip()
        genre       = request.form['genre'].strip()
        description = request.form['description'].strip()
        cursor.execute(
            "UPDATE projects SET title=%s, genre=%s, description=%s WHERE id=%s",
            (title, genre, description, project_id)
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Project updated!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    cursor.close()
    db.close()
    return render_template('edit_project.html', project=project)


@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete a project (owner only)."""
    if login_required():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()

    if project and project['owner_id'] == session['user_id']:
        cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        db.commit()
        flash('Project deleted.', 'success')
    else:
        flash('Unauthorized action.', 'error')

    cursor.close()
    db.close()
    return redirect(url_for('index'))


# ════════════════════════════════════════════
# ASPECT ROUTES
# ════════════════════════════════════════════

@app.route('/project/<int:project_id>/aspect/add', methods=['GET', 'POST'])
def add_aspect(project_id):
    """Add an aspect to a project (contributors only)."""
    if login_required():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Verify user is a contributor
    cursor.execute(
        "SELECT * FROM contributors WHERE project_id=%s AND user_id=%s",
        (project_id, session['user_id'])
    )
    if not cursor.fetchone():
        flash('Join the project first to add aspects.', 'error')
        cursor.close()
        db.close()
        return redirect(url_for('project_detail', project_id=project_id))

    if request.method == 'POST':
        aspect_type = request.form['aspect_type'].strip()
        details     = request.form['details'].strip()
        cursor.execute(
            "INSERT INTO aspects (project_id, aspect_type, details, assigned_to) VALUES (%s, %s, %s, %s)",
            (project_id, aspect_type, details, session['user_id'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Aspect added!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))

    cursor.close()
    db.close()
    return render_template('add_aspect.html', project_id=project_id)


@app.route('/aspect/<int:aspect_id>/delete', methods=['POST'])
def delete_aspect(aspect_id):
    """Delete an aspect (assigned user or project owner)."""
    if login_required():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, p.owner_id
        FROM aspects a
        JOIN projects p ON a.project_id = p.id
        WHERE a.id = %s
    """, (aspect_id,))
    aspect = cursor.fetchone()

    if aspect and (aspect['assigned_to'] == session['user_id'] or
                   aspect['owner_id'] == session['user_id']):
        project_id = aspect['project_id']
        cursor.execute("DELETE FROM aspects WHERE id = %s", (aspect_id,))
        db.commit()
        flash('Aspect removed.', 'success')
    else:
        project_id = 0
        flash('Unauthorized.', 'error')

    cursor.close()
    db.close()
    return redirect(url_for('project_detail', project_id=project_id))


# ════════════════════════════════════════════
# CONTRIBUTOR ROUTES
# ════════════════════════════════════════════

@app.route('/project/<int:project_id>/join', methods=['POST'])
def join_project(project_id):
    """Join a project as a contributor."""
    if login_required():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO contributors (project_id, user_id, role) VALUES (%s, %s, %s)",
            (project_id, session['user_id'], 'Member')
        )
        db.commit()
        flash('You joined the project!', 'success')
    except mysql.connector.IntegrityError:
        flash('You are already a contributor.', 'error')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/project/<int:project_id>/leave', methods=['POST'])
def leave_project(project_id):
    """Leave a project."""
    if login_required():
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Owner cannot leave their own project
    cursor.execute("SELECT owner_id FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()

    if project and project['owner_id'] == session['user_id']:
        flash('You cannot leave your own project. Delete it instead.', 'error')
    else:
        cursor.execute(
            "DELETE FROM contributors WHERE project_id=%s AND user_id=%s",
            (project_id, session['user_id'])
        )
        db.commit()
        flash('You left the project.', 'success')

    cursor.close()
    db.close()
    return redirect(url_for('project_detail', project_id=project_id))


# ════════════════════════════════════════════
# RUN
# ════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True)
