# from flask import Flask ,render_template,request,redirect,url_for,jsonify,Response
# from openpyxl import Workbook
# import io
# from flask import send_file

from flask import Flask, render_template, request, redirect, url_for, send_file
from openpyxl import Workbook
import io
from flask_mysqldb import MySQL
from flask_mysqldb import MySQL
app=Flask(__name__)
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="group_eight"

mysql=MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("About-product.html")
@app.route("/add")
def add_product():
    return render_template("Add-product.html")
@app.route("/list")
def list_product():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM products ORDER BY product_id DESC")
    deta =cur.fetchall()
    cur.close()
    return render_template("list-product.html ", products=deta)

@app.route("/add", methods=["GET", "POST"])
def add_student():
    print(request.method)
    if request.method == "POST":
        # print(request.form)
        name = request.form["name"]
        # userproduct = request.form["userproduct"]S
        price= request.form["price"]
        quantity=request.form["quantity"]
        brand = request.form['brand']


        cur = mysql.connection.cursor()
        brand = request.form['brand']
        cur.execute(
        "INSERT INTO products (name, price, quantity, brand) VALUES (%s, %s, %s, %s)",
        (name, price, quantity, brand))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("list_product"))
    return render_template("Add-product.html")
@app.route('/Products/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_products(product_id):
    # Fetch student by id, then update logic here
    print(request.method)
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products WHERE product_id = %s",(product_id,))
        data = cur.fetchone()
        cur.close()
        return render_template("edit-product.html", product=data)
    return redirect(url_for('list_product'))
@app.route('/Products/update_product', methods=['POST', 'GET'])
def update_products():
    # Fetch student by id, then update logic here
    print(request.form)
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        brand = request.form['brand']
        

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE products 
            SET product_name = %s,product_brand=%s, product_price = %s, product_quantity = %s
            WHERE product_id = %s
        """, (name, brand ,price, quantity, id))
        mysql.connection.commit()   # ✅ commit on connection, not cursor
        cur.close()

        return redirect(url_for('list_product'))  
    # return redirect("../students/list-students")

@app.route('/products/delete<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    # Delete student from DB logic here
    print(request.method)
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM products WHERE product_id ={product_id};")
    mysql.connection.commit()
    cur.close()
    # return redirect("../list_product")
    return redirect(url_for('list_product'))
@app.route("/list-products", methods=["GET"])
def list_products():
    search_query = request.args.get("q")   # get search term
    selected_brand = request.args.get("brand")  # get selected brand

    cur = mysql.connection.cursor()

    # Start SQL query
    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    # Filter by product name (case-insensitive)
    if search_query:
        sql += " AND LOWER(name) LIKE %s"
        params.append("%" + search_query + "%")

    # Filter by brand
    if selected_brand and  selected_brand != "All":
        sql += " AND brand = %s"
        params.append(selected_brand)

    sql += " ORDER BY product_id DESC"
    cur.execute(sql, tuple(params))
    products = cur.fetchall()

    # Get all brands for dropdown (unfiltered)
    cur.execute("SELECT DISTINCT brand FROM products")
    brands = [row[0] for row in cur.fetchall()]

    cur.close()

    return render_template(
        'list-product.html',
        products=products,
        brands=brands,
        selected_brand=selected_brand,
        search_query=search_query
    )




@app.route('/products/<int:product_id>', methods=['GET'])
def view_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT product_id, name, brand, price, quantity FROM products WHERE product_id=%s", (product_id,))

    products = cur.fetchone()
    cur.close()

    if products:
        return render_template("info.html", products=products)
    else:
        return "Product not found", 404
# Download products as Excel
@app.route('/products/download/excel')
def download_products_excel():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    data = cur.fetchall()
    cur.close()

    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    # Header row
    ws.append(['ID', 'Name','brand', 'Price', 'Quantity'])

    # Data rows
    for row in data:
        ws.append(row)

    # Save to in-memory buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="products.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



    



if __name__=="__main__":
    app.run(debug=True)