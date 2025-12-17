# config.py
import mysql.connector

# Koneksi ke database
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="restaurant_orders"
)

# Cursor untuk execute query
c = conn.cursor()

# Fungsi ambil data customers dengan total spending
def view_customers():
    c.execute('''
        SELECT c.*, COALESCE(SUM(od.total_price), 0) as total_spending
        FROM Customers c
        LEFT JOIN Orders o ON c.customer_id = o.customer_id
        LEFT JOIN Order_Details od ON o.order_id = od.order_id
        GROUP BY c.customer_id
        ORDER BY total_spending DESC
    ''')
    return c.fetchall()

# Fungsi ambil data categories dengan total quantity
def view_categories():
    c.execute('''
        SELECT c.category_id, c.category_name, 
               COALESCE(SUM(od.quantity), 0) as total_qty,
               DATE(o.order_time) as order_date
        FROM Categories c
        LEFT JOIN Menu m ON c.category_id = m.category_id
        LEFT JOIN Order_Details od ON m.menu_id = od.menu_id
        LEFT JOIN Orders o ON od.order_id = o.order_id
        GROUP BY c.category_id, DATE(o.order_time)
    ''')
    return c.fetchall()

# Fungsi ambil data payment methods dengan revenue
def view_payment_methods():
    c.execute('''
        SELECT p.payment_id, p.method_name, 
               COALESCE(SUM(od.total_price), 0) as revenue,
               DATE(o.order_time) as order_date
        FROM Payment_Methods p
        LEFT JOIN Orders o ON p.payment_id = o.payment_id
        LEFT JOIN Order_Details od ON o.order_id = od.order_id
        GROUP BY p.payment_id, DATE(o.order_time)
    ''')
    return c.fetchall()

# Fungsi ambil data tables
def view_tables():
    c.execute('SELECT * FROM Tables ORDER BY table_id ASC')
    return c.fetchall()

# Fungsi ambil data penggunaan meja
def view_table_usage():
    c.execute('''
        SELECT t.table_id, t.table_number, t.capacity, 
               COUNT(o.order_id) as times_used,
               DATE(o.order_time) as order_date
        FROM Tables t
        LEFT JOIN Orders o ON t.table_id = o.table_id
        GROUP BY t.table_id, DATE(o.order_time)
    ''')
    return c.fetchall()

# Fungsi ambil data menu dengan total ordered
def view_menu():
    c.execute('''
        SELECT m.menu_id, m.item_name, m.unit_price, m.member_only,
               c.category_name, COALESCE(SUM(od.quantity), 0) as total_ordered,
               DATE(o.order_time) as order_date
        FROM Menu m
        LEFT JOIN Categories c ON m.category_id = c.category_id
        LEFT JOIN Order_Details od ON m.menu_id = od.menu_id
        LEFT JOIN Orders o ON od.order_id = o.order_id
        GROUP BY m.menu_id, DATE(o.order_time)
    ''')
    return c.fetchall()

# Fungsi ambil data orders lengkap
def view_orders():
    c.execute('''
        SELECT o.order_id, o.customer_id, o.guest_name, o.service_type,
               o.table_id, o.payment_id, o.order_status, o.order_time,
               p.method_name, t.table_number, c.customer_name,
               DATE(o.order_time) as order_date
        FROM Orders o
        LEFT JOIN Payment_Methods p ON o.payment_id = p.payment_id
        LEFT JOIN Tables t ON o.table_id = t.table_id
        LEFT JOIN Customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_time DESC
    ''')
    return c.fetchall()

# Fungsi ambil data order details lengkap
def view_order_details():
    c.execute('''
        SELECT od.order_detail_id, od.order_id, od.menu_id, od.quantity,
               od.total_price, od.request_note, m.item_name, m.unit_price,
               DATE(o.order_time) as order_date
        FROM Order_Details od
        JOIN Menu m ON od.menu_id = m.menu_id
        JOIN Orders o ON od.order_id = o.order_id
        ORDER BY o.order_time DESC
    ''')
    return c.fetchall()

# Fungsi ambil data reservations lengkap
def view_reservations():
    c.execute('''
        SELECT r.reservation_id, r.customer_id, r.table_id, r.reservation_date,
               r.check_in, r.check_out, r.party_size, r.status, r.special_request,
               t.table_number, t.capacity, c.customer_name
        FROM Reservations r
        JOIN Tables t ON r.table_id = t.table_id
        JOIN Customers c ON r.customer_id = c.customer_id
        ORDER BY r.reservation_date DESC
    ''')
    return c.fetchall()

# Fungsi ambil data reviews lengkap
def view_reviews():
    c.execute('''
        SELECT r.review_id, r.order_id, r.rating, r.comment, r.review_date,
               c.customer_name
        FROM Reviews r
        JOIN Orders o ON r.order_id = o.order_id
        LEFT JOIN Customers c ON o.customer_id = c.customer_id
        ORDER BY r.review_date DESC
    ''')
    return c.fetchall()
