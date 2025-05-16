from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for session management

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'baldos_inventory'

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

SALT = 'poiuytrewq9087'
mysql = MySQL(app)

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        salted = str(SALT + password).encode('utf-8')
        hashed_password = hashlib.sha512(salted).hexdigest()

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username FROM users WHERE username=%s AND password=%s", (username, hashed_password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = user[1]  # username from database
            session['user_id'] = user[0]    # id from database
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Get products
    cur.execute("SELECT id, name, unit, price, quantity FROM products")
    products = cur.fetchall()
    
    # Get recent sales for dashboard
    cur.execute("""
        SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date, u.username 
        FROM sales s
        JOIN products p ON s.product_id = p.id
        JOIN users u ON s.user_id = u.id
        ORDER BY s.sale_date DESC LIMIT 5
    """)
    recent_sales = cur.fetchall()
    
    # Get sales summary for dashboard
    cur.execute("""
        SELECT 
            SUM(total_price) as total_sales,
            COUNT(*) as total_transactions,
            DATE(sale_date) as sale_day
        FROM sales
        WHERE DATE(sale_date) = CURDATE()
        GROUP BY sale_day
    """)
    sales_summary = cur.fetchone()
    
    cur.close()
    
    return render_template('dashboard.html', 
                         username=session['username'], 
                         products=products,
                         recent_sales=recent_sales,
                         sales_summary=sales_summary)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# Product CRUD Operations
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form['name']
        unit = request.form['unit']
        price = request.form['price']
        quantity = request.form['quantity']

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO products (name, unit, price, quantity) VALUES (%s, %s, %s, %s)",
                (name, unit, price, quantity)
            )
            mysql.connection.commit()
            flash('Product added successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
        finally:
            cur.close()
    
    return redirect(url_for('dashboard'))

@app.route('/edit_product/<int:id>', methods=['POST'])
def edit_product(id):
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form['name']
        unit = request.form['unit']
        price = request.form['price']
        quantity = request.form['quantity']

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "UPDATE products SET name=%s, unit=%s, price=%s, quantity=%s WHERE id=%s",
                (name, unit, price, quantity, id)
            )
            mysql.connection.commit()
            flash('Product updated successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
        finally:
            cur.close()
    
    return redirect(url_for('dashboard'))

@app.route('/delete_product/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor()
    try:
        # First check if the product exists
        cur.execute("SELECT id FROM products WHERE id=%s", (id,))
        product = cur.fetchone()
        
        if not product:
            flash('Product not found', 'danger')
            return redirect(url_for('dashboard'))
            
        # Delete any sales records associated with this product first
        cur.execute("DELETE FROM sales WHERE product_id=%s", (id,))
        # Then delete the product
        cur.execute("DELETE FROM products WHERE id=%s", (id,))
        mysql.connection.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('dashboard'))

@app.route('/get_product/<int:id>')
def get_product(id):
    if 'username' not in session or 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, unit, price, quantity FROM products WHERE id=%s", (id,))
    product = cur.fetchone()
    cur.close()
    
    if product:
        return jsonify({
            'id': product[0],
            'name': product[1],
            'unit': product[2],
            'price': float(product[3]),
            'quantity': product[4]
        })
    return jsonify({'error': 'Product not found'}), 404

# Sales Management
@app.route('/sales')
def sales():
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Get all sales with product and user info
    cur.execute("""
        SELECT s.id, p.name, s.quantity, s.total_price, s.sale_date, u.username 
        FROM sales s
        JOIN products p ON s.product_id = p.id
        JOIN users u ON s.user_id = u.id
        ORDER BY s.sale_date DESC
    """)
    sales = cur.fetchall()
    
    # Get sales summary
    cur.execute("""
        SELECT 
            SUM(total_price) as total_sales,
            COUNT(*) as total_transactions
        FROM sales
    """)
    sales_summary = cur.fetchone()
    
    cur.close()
    
    return render_template('sales.html', 
                         username=session['username'],
                         sales=sales,
                         sales_summary=sales_summary)

@app.route('/record_sale', methods=['POST'])
def record_sale():
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        
        # Check if user_id exists in session
        if 'user_id' not in session:
            flash('Session expired. Please login again.', 'danger')
            return redirect(url_for('login'))
            
        user_id = session['user_id']
        
        cur = mysql.connection.cursor()
        
        try:
            # Get product details
            cur.execute("SELECT price, quantity FROM products WHERE id=%s", (product_id,))
            product = cur.fetchone()
            
            if not product:
                flash('Product not found', 'danger')
                return redirect(url_for('dashboard'))
                
            price = float(product[0])
            current_quantity = int(product[1])
            
            # Check if enough stock is available
            if current_quantity < quantity:
                flash('Not enough stock available', 'danger')
                return redirect(url_for('dashboard'))
                
            # Calculate total price
            total_price = price * quantity
            
            # Record the sale
            cur.execute(
                "INSERT INTO sales (product_id, user_id, quantity, total_price, sale_date) VALUES (%s, %s, %s, %s, %s)",
                (product_id, user_id, quantity, total_price, datetime.now())
            )
            
            # Update product quantity
            new_quantity = current_quantity - quantity
            cur.execute(
                "UPDATE products SET quantity=%s WHERE id=%s",
                (new_quantity, product_id)
            )
            
            mysql.connection.commit()
            flash('Sale recorded successfully!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error recording sale: {str(e)}', 'danger')
        finally:
            cur.close()
    
    return redirect(url_for('dashboard'))

# Reports
@app.route('/reports')
def reports():
    if 'username' not in session or 'user_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    # Daily sales report
    cur.execute("""
        SELECT 
            DATE(sale_date) as sale_date,
            SUM(total_price) as total_sales,
            COUNT(*) as transaction_count
        FROM sales
        GROUP BY DATE(sale_date)
        ORDER BY sale_date DESC
        LIMIT 30
    """)
    daily_sales = cur.fetchall()
    
    # Product performance report
    cur.execute("""
        SELECT 
            p.name,
            SUM(s.quantity) as total_quantity,
            SUM(s.total_price) as total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_revenue DESC
    """)
    product_performance = cur.fetchall()
    
    cur.close()
    
    return render_template('reports.html',
                         username=session['username'],
                         daily_sales=daily_sales,
                         product_performance=product_performance)

if __name__ == '__main__':
    app.run(debug=True)