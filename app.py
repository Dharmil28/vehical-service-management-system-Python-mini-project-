from flask import Flask, request, redirect, url_for, render_template_string
import mysql.connector
from decimal import Decimal

app = Flask(__name__)


def db_query(sql, params=(), fetch=False):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="vehicle_service_db"
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def page(title, body):
    return render_template_string("""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{{ title }} | Vehicle Service Management</title>
      <style>
        body { margin:0; font-family:Arial,sans-serif; background:#f1f5f9; color:#172033; }
        header { background:#14213d; color:white; padding:22px 5%; }
        header h1 { margin:0 0 15px; font-size:25px; }
        nav { display:flex; flex-wrap:wrap; gap:18px; }
        nav a { color:white; text-decoration:none; }
        main { max-width:1100px; margin:30px auto; padding:0 18px; }
        .panel { background:white; padding:22px; border-radius:12px; margin-bottom:20px;
                 box-shadow:0 2px 8px #0000000b; overflow-x:auto; }
        .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:16px; }
        .number { font-size:30px; font-weight:bold; color:#2563eb; }
        input,select { padding:10px; border:1px solid #cbd5e1; border-radius:6px;
                       width:100%; box-sizing:border-box; margin:6px 0 14px; }
        button { background:#2563eb; color:white; border:0; border-radius:6px;
                 padding:11px 17px; cursor:pointer; }
        table { border-collapse:collapse; width:100%; }
        th,td { padding:11px; text-align:left; border-bottom:1px solid #e2e8f0; }
        th { background:#f8fafc; }
        .note { color:#475569; }
        .error { background:#fee2e2; padding:12px; border-radius:6px; }
      </style>
    </head>
    <body>
      <header>
        <h1>Vehicle Service Management</h1>
        <nav>
          <a href="/">Dashboard</a>
          <a href="/customers">Customers</a>
          <a href="/vehicles">Vehicles</a>
          <a href="/services">Services</a>
          <a href="/payments">Payments</a>
        </nav>
      </header>
      <main>
        <h2>{{ title }}</h2>
        {{ body|safe }}
      </main>
    </body>
    </html>
    """, title=title, body=body)


@app.route("/")
def home():
    customers = db_query("SELECT COUNT(*) AS n FROM customers", fetch=True)[0]["n"]
    vehicles = db_query("SELECT COUNT(*) AS n FROM vehicles", fetch=True)[0]["n"]
    services = db_query("SELECT COUNT(*) AS n FROM services", fetch=True)[0]["n"]
    payments = db_query("SELECT COALESCE(SUM(amount),0) AS n FROM payments", fetch=True)[0]["n"]
    body = f"""
    <div class="cards">
      <div class="panel"><p>Customers</p><div class="number">{customers}</div></div>
      <div class="panel"><p>Vehicles</p><div class="number">{vehicles}</div></div>
      <div class="panel"><p>Service bookings</p><div class="number">{services}</div></div>
      <div class="panel"><p>Total payments</p><div class="number">₹{payments}</div></div>
    </div>
    <div class="panel">
      <h3>Welcome!</h3>
      <p class="note">Use the menu above to manage customers, vehicles, service bookings and payments.</p>
    </div>
    """
    return page("Dashboard", body)


@app.route("/customers", methods=["GET", "POST"])
def customers_page():
    message = ""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        if not name or not phone:
            message = '<p class="error">Name and phone are required.</p>'
        else:
            db_query(
                "INSERT INTO customers (name, phone, email, address) VALUES (%s,%s,%s,%s)",
                (name, phone, email or None, address or None)
            )
            return redirect(url_for("customers_page"))

    rows = db_query("SELECT * FROM customers ORDER BY customer_id DESC", fetch=True)
    body = message + """
    <div class="panel"><h3>Add customer</h3>
    <form method="post">
      <label>Name *</label><input name="name" required>
      <label>Phone *</label><input name="phone" required>
      <label>Email</label><input name="email" type="email">
      <label>Address</label><input name="address">
      <button type="submit">Add customer</button>
    </form></div>
    <div class="panel"><h3>Customer records</h3><table>
    <tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Address</th></tr>
    """
    for r in rows:
        body += "<tr>" + "".join(
            f"<td>{r.get(k) or ''}</td>"
            for k in ("customer_id", "name", "phone", "email", "address")
        ) + "</tr>"
    body += "</table></div>"
    return page("Customers", body)


@app.route("/vehicles", methods=["GET", "POST"])
def vehicles_page():
    message = ""
    customers = db_query("SELECT customer_id, name FROM customers ORDER BY name", fetch=True)

    if request.method == "POST":
        try:
            db_query("""
                INSERT INTO vehicles
                (customer_id, registration_no, brand, model, manufacture_year)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                int(request.form["customer_id"]),
                request.form["registration_no"].strip(),
                request.form.get("brand", "").strip() or None,
                request.form.get("model", "").strip() or None,
                int(request.form["manufacture_year"]) if request.form.get("manufacture_year") else None
            ))
            return redirect(url_for("vehicles_page"))
        except (ValueError, mysql.connector.Error) as e:
            message = f'<p class="error">Could not add vehicle: {e}</p>'

    rows = db_query("""
        SELECT v.*, c.name AS customer_name
        FROM vehicles v JOIN customers c ON v.customer_id=c.customer_id
        ORDER BY v.vehicle_id DESC
    """, fetch=True)

    options = "".join(
        f'<option value="{c["customer_id"]}">{c["name"]} (ID {c["customer_id"]})</option>'
        for c in customers
    )
    body = message + f"""
    <div class="panel"><h3>Register vehicle</h3>
    <form method="post">
      <label>Customer *</label><select name="customer_id" required>{options}</select>
      <label>Registration number *</label><input name="registration_no" required>
      <label>Brand</label><input name="brand">
      <label>Model</label><input name="model">
      <label>Manufacture year</label><input name="manufacture_year" type="number" min="1900" max="2100">
      <button type="submit">Register vehicle</button>
    </form></div>
    <div class="panel"><h3>Vehicle records</h3><table>
    <tr><th>ID</th><th>Owner</th><th>Registration</th><th>Brand</th><th>Model</th><th>Year</th></tr>
    """
    for r in rows:
        body += "<tr>" + "".join(
            f"<td>{r.get(k) or ''}</td>"
            for k in ("vehicle_id", "customer_name", "registration_no", "brand", "model", "manufacture_year")
        ) + "</tr>"
    body += "</table></div>"
    return page("Vehicles", body)


@app.route("/services", methods=["GET", "POST"])
def services_page():
    message = ""
    vehicles = db_query("""
        SELECT v.vehicle_id, v.registration_no, c.name AS owner
        FROM vehicles v JOIN customers c ON v.customer_id=c.customer_id
        ORDER BY v.registration_no
    """, fetch=True)

    if request.method == "POST":
        try:
            db_query("""
                INSERT INTO services
                (vehicle_id, service_type, service_date, status, cost, description)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                int(request.form["vehicle_id"]),
                request.form["service_type"].strip(),
                request.form["service_date"],
                "Pending",
                Decimal(request.form.get("cost", "0")),
                request.form.get("description", "").strip() or None
            ))
            return redirect(url_for("services_page"))
        except (ValueError, mysql.connector.Error) as e:
            message = f'<p class="error">Could not book service: {e}</p>'

    if request.method == "POST" and request.form.get("update_status"):
        pass

    if request.args.get("status_id") and request.args.get("status"):
        db_query(
            "UPDATE services SET status=%s WHERE service_id=%s",
            (request.args["status"], int(request.args["status_id"]))
        )
        return redirect(url_for("services_page"))

    rows = db_query("""
        SELECT s.*, v.registration_no, c.name AS customer_name
        FROM services s JOIN vehicles v ON s.vehicle_id=v.vehicle_id
        JOIN customers c ON v.customer_id=c.customer_id
        ORDER BY s.service_id DESC
    """, fetch=True)

    options = "".join(
        f'<option value="{v["vehicle_id"]}">{v["registration_no"]} — {v["owner"]}</option>'
        for v in vehicles
    )
    body = message + f"""
    <div class="panel"><h3>Book service</h3>
    <form method="post">
      <label>Vehicle *</label><select name="vehicle_id" required>{options}</select>
      <label>Service type *</label><input name="service_type" required placeholder="Oil change, repair, etc.">
      <label>Service date *</label><input name="service_date" type="date" required>
      <label>Estimated cost (₹)</label><input name="cost" type="number" min="0" step="0.01" value="0">
      <label>Description</label><input name="description">
      <button type="submit">Book service</button>
    </form></div>
    <div class="panel"><h3>Service records</h3><table>
    <tr><th>ID</th><th>Vehicle</th><th>Customer</th><th>Type</th><th>Date</th><th>Status</th><th>Cost</th><th>Update</th></tr>
    """
    for r in rows:
        sid = r["service_id"]
        body += f"""<tr>
        <td>{sid}</td><td>{r["registration_no"]}</td><td>{r["customer_name"]}</td>
        <td>{r["service_type"]}</td><td>{r["service_date"]}</td>
        <td>{r["status"]}</td><td>₹{r["cost"]}</td><td>
        <form method="get" style="min-width:150px">
          <input type="hidden" name="status_id" value="{sid}">
          <select name="status">
            {''.join(f'<option value="{s}" {"selected" if r["status"] == s else ""}>{s}</option>' for s in ["Pending","In Progress","Completed","Cancelled"])}
          </select><button>Save</button>
        </form></td></tr>"""
    body += "</table></div>"
    return page("Services", body)


@app.route("/payments", methods=["GET", "POST"])
def payments_page():
    message = ""
    services = db_query("""
        SELECT s.service_id, s.service_type, s.cost, v.registration_no,
               COALESCE((SELECT SUM(p.amount) FROM payments p
                         WHERE p.service_id=s.service_id),0) AS paid
        FROM services s JOIN vehicles v ON s.vehicle_id=v.vehicle_id
        ORDER BY s.service_id DESC
    """, fetch=True)

    if request.method == "POST":
        try:
            sid = int(request.form["service_id"])
            amount = Decimal(request.form["amount"])
            method = request.form["payment_method"]
            match = next((s for s in services if s["service_id"] == sid), None)
            if not match:
                raise ValueError("Please select a valid service.")
            balance = Decimal(str(match["cost"])) - Decimal(str(match["paid"]))
            if amount <= 0:
                raise ValueError("Payment must be greater than zero.")
            if amount > balance:
                raise ValueError("Payment cannot exceed the outstanding balance.")
            db_query("""
                INSERT INTO payments (service_id, amount, payment_date, payment_method)
                VALUES (%s,%s,CURDATE(),%s)
            """, (sid, amount, method))
            return redirect(url_for("payments_page"))
        except (ValueError, ArithmeticError, mysql.connector.Error) as e:
            message = f'<p class="error">{e}</p>'

    options = "".join(
        f'<option value="{s["service_id"]}">#{s["service_id"]} {s["registration_no"]} — {s["service_type"]} (balance ₹{Decimal(str(s["cost"]))-Decimal(str(s["paid"]))})</option>'
        for s in services
        if Decimal(str(s["cost"])) - Decimal(str(s["paid"])) > 0
    )
    payments = db_query("""
        SELECT p.*, s.service_type, v.registration_no
        FROM payments p JOIN services s ON p.service_id=s.service_id
        JOIN vehicles v ON s.vehicle_id=v.vehicle_id
        ORDER BY p.payment_id DESC
    """, fetch=True)

    body = message + f"""
    <div class="panel"><h3>Record payment</h3>
    <form method="post">
      <label>Service *</label><select name="service_id" required>{options}</select>
      <label>Amount (₹) *</label><input name="amount" type="number" min="0.01" step="0.01" required>
      <label>Payment method</label>
      <select name="payment_method"><option>Cash</option><option>UPI</option><option>Card</option><option>Bank transfer</option></select>
      <button type="submit">Record payment</button>
    </form></div>
    <div class="panel"><h3>Payment history</h3><table>
    <tr><th>Payment ID</th><th>Service ID</th><th>Vehicle</th><th>Service</th><th>Amount</th><th>Date</th><th>Method</th></tr>
    """
    for r in payments:
        body += "<tr>" + "".join(
            f"<td>{r.get(k) or ''}</td>"
            for k in ("payment_id", "service_id", "registration_no", "service_type", "amount", "payment_date", "payment_method")
        ) + "</tr>"
    body += "</table></div>"
    return page("Payments", body)


@app.errorhandler(Exception)
def handle_error(error):
    app.logger.exception(error)
    return page(
        "Something went wrong",
        '<div class="panel"><p class="error">The request failed. Check that MySQL is running and the database tables exist.</p>'
        '<p>Technical detail: ' + str(error).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + '</p>'
        '<p><a href="/">Return to dashboard</a></p></div>'
    ), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
