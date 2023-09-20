import os
import sqlite3

from flask import (Flask, flash, redirect, render_template, request,
                   render_template_string, session, url_for)
from flask_login import (LoginManager, current_user, login_required, login_user)

from User import User
from src.server.html_generator import HTMLGenerator
from utilities import DBAgent

app = Flask(__name__)
app.secret_key = 'mysecretkey'

app.config['ENV'] = 'development'
app.config['DEBUG'] = True

login_manager = LoginManager()
login_manager.init_app(app)


db_agent = DBAgent()
html_generator = HTMLGenerator(db_agent)

db_path = db_agent.get_db_path()

if __name__ == '__main__':
    app.run(debug=True)


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
    user = c.fetchone()
    if user:
        return User(id=user[0], username=user[1], password=user[2], role=user[4])
    return None


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(
            "SELECT * FROM Users WHERE Username = ? AND Password = ?", (username, password))
        user = c.fetchone()
        if user:
            user_obj = User(id=user[0], username=user[1],
                            password=user[2], role=user[4])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'login')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'csrf_token' not in session:
        session['csrf_token'] = os.urandom(24).hex()

    if request.method == 'POST':
        print(request.form)  # Debug line
        username = request.form['username']
        email = username + '@email.com'
        password = request.form['password']

        db_agent.execute_query("INSERT INTO Users (Username, Email, Password, Role) VALUES (?, ?, ?, 'admin')",
                      (username, email, password))

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        print(url_for('admin_skills'))
        return redirect(url_for('admin_skills'))
    else:
        return redirect(url_for('user_skills'))


@app.route('/update_skill/<int:skill_id>', methods=['GET', 'POST'])
@login_required
def update_skill(skill_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM Skills WHERE SkillID = ?", (skill_id,))
    skill = c.fetchone()
    conn.close()

    if skill:
        skill_dict = {'id': skill[0], 'name': skill[1], 'description': skill[2], 'price': skill[3],
                      'launch_date': skill[4], 'category_id': skill[5]}

        if request.method == 'POST':
            new_skill_name = request.form.get('name')
            new_description = request.form.get('description')
            new_price = request.form.get('price')
            new_launch_date = request.form.get('launch_date')
            new_category_id = request.form.get('category_id')
            db_agent.execute_query(
                "UPDATE Skills SET SkillName = ?, Description = ?, Price = ?, LaunchDate = ?, CategoryID = ? WHERE SkillID = ?",
                (new_skill_name, new_description, new_price, new_launch_date, new_category_id, skill_id))

            flash('Skill updated successfully', 'success')
            return redirect(url_for('admin_skills'))

        return render_template('update_skill.html', skill=skill_dict, skill_id=skill_id)
    else:
        flash('Skill not found', 'danger')
        return redirect(url_for('admin_skills'))


def add_skill(skill_name, description, price, launch_date, category_id):
    db_agent.execute_query("INSERT INTO Skills (SkillName, Description, Price, LaunchDate, CategoryID) VALUES (?, ?, ?, ?, ?)",
                  (skill_name, description, price, launch_date, category_id))


@app.route('/object/<table_name>/create', methods=['GET', 'POST'])
@login_required
def create(table_name):
    if table_name == 'Skills':
        return redirect(url_for('create_skill'))
    elif table_name == 'Categories':
        return redirect(url_for('create_category'))
    elif table_name == 'Users':
        return redirect(url_for('create_user'))
    else:
        flash(f"Table {table_name} is not supported for creation.", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/create_skill', methods=['GET', 'POST'])
@login_required
def create_skill():
    if request.method == 'POST':
        new_skill_name = request.form.get('name')
        new_skill_description = request.form.get('description')
        new_skill_price = request.form.get('price')
        new_skill_launch_date = request.form.get('launch_date')
        new_skill_category_id = request.form.get('category_id')

        db_agent.execute_query("INSERT INTO Skills (SkillName, Description, Price, LaunchDate, CategoryID) VALUES (?, ?, ?, ?, ?)",
                  (
                      new_skill_name, new_skill_description, new_skill_price, new_skill_launch_date,
                      new_skill_category_id))

        flash('Skill created successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_skill.html')


@app.route('/create_category', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        new_category_name = request.form.get('name')

        db_agent.execute_query("INSERT INTO Categories (CategoryName) VALUES (?)",
                  (new_category_name,))

        flash('Category created successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_category.html')


@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_email = request.form.get('email')
        new_role = request.form.get('role')

        db_agent.execute_query("INSERT INTO Users (Username, Password, Email, Role) VALUES (?, ?, ?, ?)",
                  (new_username, new_password, new_email, new_role))

        flash('User created successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_user.html')


@app.route('/object/<table_name>/update/<int:object_id>', methods=['POST'])
@login_required
def update(table_name, object_id):
    print("Update() called ")
    print("kwargs = " + str(request.form.to_dict()))

    if table_name == 'Skills':
        return redirect(url_for('update_skill', skill_id=object_id))
    elif table_name == 'Categories':
        print("Update category chosen form update(). Displaying update_category.html")
        return redirect(url_for('update_category', category_id=object_id))
    elif table_name == 'Users':
        return redirect(url_for('update_user', user_id=object_id))
    else:
        flash(f"Table {table_name} is not supported for updates.", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/update_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def update_category(category_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM Categories WHERE CategoryID = ?", (category_id,))
    category = c.fetchone()
    conn.close()

    if category:
        category_dict = {'id': category[0], 'name': category[1]}

        if request.method == 'POST':
            new_category_name = request.form.get('name')

            db_agent.execute_query("UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?",
                      (new_category_name, category_id))

            flash('Category updated successfully', 'success')
            return redirect(url_for('admin_skills'))

        return render_template('update_category.html', category=category_dict, category_id=category_id)
    else:
        flash('Category not found', 'danger')
        return redirect(url_for('admin_skills'))


@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE UserID = ?", (user_id,))
    user = c.fetchone()
    conn.close()

    if user:
        user_dict = {'id': user[0], 'username': user[1], 'email': user[2], 'password': user[3], 'role': user[4]}

        if request.method == 'POST':
            new_username = request.form.get('username')
            new_email = request.form.get('email')
            new_password = request.form.get('password')
            new_role = request.form.get('role')

            db_agent.execute_query("UPDATE Users SET Username = ?, Email = ?, Password = ?, Role = ? WHERE UserID = ?",
                      (new_username, new_email, new_password, new_role, user_id))

            flash('User updated successfully', 'success')
            return redirect(url_for('admin_skills'))

        return render_template('update_user.html', user=user_dict, user_id=user_id)
    else:
        flash('User not found', 'danger')
        return redirect(url_for('admin_users'))


@app.route('/object/<table_name>/delete/<column_name>/<int:object_id>', methods=['POST'])
@login_required
def delete(table_name, column_name, object_id):
    if current_user.role == 'admin':
        print("Deleting admin")
        delete_object(table_name, column_name, object_id)
        flash(f"Object in {table_name} deleted", 'success')
    else:
        flash("You don't have admin access.", 'warning')
        app.logger.debug("Attempt to delete without admin access")
    return redirect(url_for('dashboard'))


def delete_object(table_name, column_name, object_id):
    query = f"DELETE FROM {table_name} WHERE {column_name} = ?"
    db_agent.execute_query(query, (object_id,))


@app.route('/admin/add_skill', methods=['GET', 'POST'])
@login_required
def admin_add_skill():
    if current_user.role != 'admin':
        flash("You don't have admin access.", 'warning')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        add_skill(request.form['name'], request.form['description'], request.form['price'], request.form['launch_date'],
                  request.form['category_id'])
        return redirect(url_for('dashboard'))

    return render_template('admin_add_skill.html')


@app.route('/admin/skills')
@login_required
def admin_skills():
    print("Table data list: " + str(html_generator.get_table_data_list()))
    print("Generate_table_html: " + str(html_generator.generate_table_html(html_generator.get_table_data_list())))
    print("html: " + render_template_string(html_generator.generate_table_html(html_generator.get_table_data_list())))
    return render_template_string(html_generator.generate_table_html(html_generator.get_table_data_list()))


@app.route('/user/add_skill', methods=['GET', 'POST'])
@login_required
def user_add_skill():
    if request.method == 'POST':
        add_skill(request.form['name'], request.form['description'], request.form['price'], request.form['launch_date'],
                  request.form['category_id'])
        return redirect(url_for('dashboard'))

    return render_template('user_add_skill.html')
