import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, InvalidOperation
from database import Database


class VehicleServiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Service Management System")
        self.root.geometry("850x600")
        self.root.minsize(700, 500)

        self.root.configure(bg="#eef2f7")

        header = tk.Frame(root, bg="#17365d", pady=22)
        header.pack(fill="x")

        tk.Label(
            header,
            text="VEHICLE SERVICE MANAGEMENT SYSTEM",
            font=("Arial", 20, "bold"),
            bg="#17365d",
            fg="white"
        ).pack()

        tk.Label(
            root,
            text="Manage customers, vehicles, services and payments",
            font=("Arial", 11),
            bg="#eef2f7",
            fg="#444444"
        ).pack(pady=15)

        menu = tk.Frame(root, bg="#eef2f7")
        menu.pack(pady=10)

        buttons = [
            ("Customer Management", self.customer_menu),
            ("Vehicle Management", self.vehicle_menu),
            ("Service Management", self.service_menu),
            ("Billing & Payments", self.billing_menu),
        ]

        for index, (label, command) in enumerate(buttons):
            button = tk.Button(
                menu,
                text=label,
                command=command,
                width=28,
                height=2,
                font=("Arial", 12, "bold"),
                bg="#ffffff",
                fg="#17365d",
                relief="groove",
                cursor="hand2"
            )
            button.grid(
                row=index // 2,
                column=index % 2,
                padx=12,
                pady=12,
                sticky="nsew"
            )

        menu.grid_columnconfigure(0, weight=1)
        menu.grid_columnconfigure(1, weight=1)

        tk.Label(
            root,
            text="Python OOP  |  Tkinter  |  MySQL",
            font=("Arial", 10),
            bg="#eef2f7",
            fg="#666666"
        ).pack(side="bottom", pady=15)

    # ---------- DATABASE HELPERS ----------

    def fetch_all(self, query, values=()):
        db = None
        cursor = None

        try:
            db = Database()
            cursor = db.get_connection().cursor()
            cursor.execute(query, values)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def execute_query(self, query, values=()):
        db = None
        cursor = None

        try:
            db = Database()
            connection = db.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, values)
            connection.commit()

            return cursor.lastrowid

        except Exception:
            if db:
                try:
                    db.get_connection().rollback()
                except Exception:
                    pass
            raise

        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

    def show_error(self, error, window):
        messagebox.showerror(
            "Error",
            str(error),
            parent=window
        )

    def create_window(self, title, geometry="800x550"):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(geometry)
        window.minsize(650, 400)

        tk.Label(
            window,
            text=title,
            font=("Arial", 17, "bold"),
            fg="#17365d"
        ).pack(pady=12)

        return window

    def create_table(self, parent, columns, widths=None):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=12, pady=10)

        table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=10
        )

        for index, column in enumerate(columns):
            table.heading(column, text=column)
            width = widths[index] if widths else 130
            table.column(column, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=table.yview
        )
        table.configure(yscrollcommand=scrollbar.set)

        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return table

    # ---------- CUSTOMER MANAGEMENT ----------

    def customer_menu(self):
        window = self.create_window(
            "Customer Management", "800x600"
        )

        form = tk.Frame(window)
        form.pack(pady=5)

        fields = ["Name", "Phone", "Email", "Address"]
        entries = {}

        for row, field in enumerate(fields):
            tk.Label(form, text=field + ":").grid(
                row=row, column=0, padx=8, pady=5, sticky="w"
            )
            entry = tk.Entry(form, width=35)
            entry.grid(row=row, column=1, padx=8, pady=5)
            entries[field] = entry

        columns = ("ID", "Name", "Phone", "Email", "Address")
        table = self.create_table(
            window, columns, [50, 150, 110, 170, 220]
        )

        def refresh():
            try:
                records = self.fetch_all("""
                    SELECT customer_id, name, phone, email, address
                    FROM customers
                    ORDER BY customer_id DESC
                """)

                table.delete(*table.get_children())

                for record in records:
                    table.insert("", "end", values=record)

            except Exception as error:
                self.show_error(error, window)

        def add_customer():
            name = entries["Name"].get().strip()
            phone = entries["Phone"].get().strip()
            email = entries["Email"].get().strip()
            address = entries["Address"].get().strip()

            if not name or not phone:
                messagebox.showwarning(
                    "Required",
                    "Name and phone are required.",
                    parent=window
                )
                return

            try:
                customer_id = self.execute_query("""
                    INSERT INTO customers (name, phone, email, address)
                    VALUES (%s, %s, %s, %s)
                """, (name, phone, email, address))

                messagebox.showinfo(
                    "Success",
                    f"Customer added successfully!\nID: {customer_id}",
                    parent=window
                )

                for entry in entries.values():
                    entry.delete(0, tk.END)

                refresh()

            except Exception as error:
                self.show_error(error, window)

        tk.Button(
            window, text="Add Customer",
            command=add_customer, width=18
        ).pack(pady=4)

        tk.Button(
            window, text="Refresh Customers",
            command=refresh
        ).pack(pady=4)

        refresh()

    # ---------- VEHICLE MANAGEMENT ----------

    def vehicle_menu(self):
        window = self.create_window(
            "Vehicle Management", "850x600"
        )

        form = tk.Frame(window)
        form.pack(pady=5)

        fields = [
            ("Customer ID", "customer_id"),
            ("Registration Number", "registration"),
            ("Brand", "brand"),
            ("Model", "model")
        ]

        entries = {}

        for row, (label, key) in enumerate(fields):
            tk.Label(form, text=label + ":").grid(
                row=row, column=0, padx=8, pady=5, sticky="w"
            )
            entry = tk.Entry(form, width=32)
            entry.grid(row=row, column=1, padx=8, pady=5)
            entries[key] = entry

        columns = (
            "Vehicle ID", "Customer", "Registration", "Brand", "Model"
        )
        table = self.create_table(
            window, columns, [80, 150, 160, 120, 120]
        )

        def refresh():
            try:
                records = self.fetch_all("""
                    SELECT v.vehicle_id, c.name, v.registration_no,
                           v.brand, v.model
                    FROM vehicles v
                    JOIN customers c
                      ON v.customer_id = c.customer_id
                    ORDER BY v.vehicle_id DESC
                """)

                table.delete(*table.get_children())

                for record in records:
                    table.insert("", "end", values=record)

            except Exception as error:
                self.show_error(error, window)

        def add_vehicle():
            try:
                customer_id = int(
                    entries["customer_id"].get().strip()
                )
                registration = entries["registration"].get().strip()
                brand = entries["brand"].get().strip()
                model = entries["model"].get().strip()

                if not registration:
                    messagebox.showwarning(
                        "Required",
                        "Registration number is required.",
                        parent=window
                    )
                    return

                vehicle_id = self.execute_query("""
                    INSERT INTO vehicles
                        (customer_id, registration_no, brand, model)
                    VALUES (%s, %s, %s, %s)
                """, (customer_id, registration, brand, model))

                messagebox.showinfo(
                    "Success",
                    f"Vehicle registered!\nVehicle ID: {vehicle_id}",
                    parent=window
                )

                for entry in entries.values():
                    entry.delete(0, tk.END)

                refresh()

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Customer ID must be a number.",
                    parent=window
                )
            except Exception as error:
                self.show_error(error, window)

        tk.Button(
            window, text="Register Vehicle",
            command=add_vehicle, width=18
        ).pack(pady=4)

        tk.Button(
            window, text="Refresh Vehicles",
            command=refresh
        ).pack(pady=4)

        refresh()

    # ---------- SERVICE MANAGEMENT ----------

    def service_menu(self):
        window = self.create_window(
            "Service Management", "900x650"
        )

        form = tk.Frame(window)
        form.pack(pady=5)

        fields = [
            ("Vehicle ID", "vehicle_id"),
            ("Service Type", "service_type"),
            ("Date (YYYY-MM-DD)", "service_date"),
            ("Cost (INR)", "cost")
        ]

        entries = {}

        for row, (label, key) in enumerate(fields):
            tk.Label(form, text=label + ":").grid(
                row=row, column=0, padx=8, pady=5, sticky="w"
            )
            entry = tk.Entry(form, width=32)
            entry.grid(row=row, column=1, padx=8, pady=5)
            entries[key] = entry

        entries["service_date"].insert(0, date.today().isoformat())
        entries["cost"].insert(0, "0")

        columns = (
            "Service ID", "Vehicle", "Service", "Date", "Status", "Cost"
        )
        table = self.create_table(
            window, columns, [80, 120, 150, 110, 110, 100]
        )

        def refresh():
            try:
                records = self.fetch_all("""
                    SELECT s.service_id, v.registration_no,
                           s.service_type, s.service_date,
                           s.status, s.cost
                    FROM services s
                    JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                    ORDER BY s.service_id DESC
                """)

                table.delete(*table.get_children())

                for record in records:
                    table.insert("", "end", values=record)

            except Exception as error:
                self.show_error(error, window)

        def book_service():
            try:
                vehicle_id = int(
                    entries["vehicle_id"].get().strip()
                )
                service_type = entries["service_type"].get().strip()
                service_date = entries["service_date"].get().strip()
                date.fromisoformat(service_date)

                cost = Decimal(entries["cost"].get().strip())

                if not service_type:
                    messagebox.showwarning(
                        "Required",
                        "Service type is required.",
                        parent=window
                    )
                    return

                if not cost.is_finite() or cost < 0:
                    raise ValueError("Cost must be a non-negative number.")

                service_id = self.execute_query("""
                    INSERT INTO services
                        (vehicle_id, service_type, service_date, cost)
                    VALUES (%s, %s, %s, %s)
                """, (vehicle_id, service_type, service_date, cost))

                messagebox.showinfo(
                    "Success",
                    f"Service booked!\nService ID: {service_id}",
                    parent=window
                )

                entries["vehicle_id"].delete(0, tk.END)
                entries["service_type"].delete(0, tk.END)
                entries["cost"].delete(0, tk.END)
                entries["cost"].insert(0, "0")

                refresh()

            except (ValueError, InvalidOperation):
                messagebox.showerror(
                    "Invalid Input",
                    "Check the vehicle ID, date (YYYY-MM-DD), and cost.",
                    parent=window
                )
            except Exception as error:
                self.show_error(error, window)

        def update_status():
            selected = table.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Service",
                    "Select a service row in the table first.",
                    parent=window
                )
                return

            record = table.item(selected[0], "values")
            service_id = record[0]

            status_window = tk.Toplevel(window)
            status_window.title("Update Service Status")
            status_window.geometry("300x180")

            tk.Label(
                status_window,
                text=f"Service ID: {service_id}"
            ).pack(pady=10)

            status_var = tk.StringVar(value="Pending")

            combo = ttk.Combobox(
                status_window,
                textvariable=status_var,
                values=("Pending", "In Progress", "Completed"),
                state="readonly"
            )
            combo.pack(pady=8)

            def save_status():
                try:
                    self.execute_query("""
                        UPDATE services
                        SET status = %s
                        WHERE service_id = %s
                    """, (status_var.get(), service_id))

                    messagebox.showinfo(
                        "Success", "Service status updated.",
                        parent=status_window
                    )
                    status_window.destroy()
                    refresh()

                except Exception as error:
                    self.show_error(error, status_window)

            tk.Button(
                status_window,
                text="Save Status",
                command=save_status
            ).pack(pady=8)

        tk.Button(
            window, text="Book Service",
            command=book_service, width=18
        ).pack(pady=4)

        tk.Button(
            window, text="Update Selected Service Status",
            command=update_status
        ).pack(pady=4)

        tk.Button(
            window, text="Refresh Services",
            command=refresh
        ).pack(pady=4)

        refresh()

    # ---------- BILLING AND PAYMENTS ----------

    def billing_menu(self):
        window = self.create_window(
            "Billing & Payments", "850x600"
        )

        form = tk.Frame(window)
        form.pack(pady=8)

        tk.Label(form, text="Service ID:").grid(
            row=0, column=0, padx=8, pady=5
        )

        service_id_entry = tk.Entry(form, width=18)
        service_id_entry.grid(row=0, column=1, padx=8, pady=5)

        columns = (
            "Payment ID", "Service ID", "Amount", "Date", "Method"
        )
        table = self.create_table(
            window, columns, [100, 100, 130, 130, 120]
        )

        bill_text = tk.Text(
            window, height=8, width=75,
            font=("Courier", 10), state="disabled"
        )
        bill_text.pack(padx=12, pady=8, fill="x")

        def get_service_id():
            try:
                service_id = int(service_id_entry.get().strip())
                if service_id <= 0:
                    raise ValueError
                return service_id
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Enter a valid positive Service ID.",
                    parent=window
                )
                return None

        def refresh_payments(service_id):
            try:
                records = self.fetch_all("""
                    SELECT payment_id, service_id, amount,
                           payment_date, payment_method
                    FROM payments
                    WHERE service_id = %s
                    ORDER BY payment_id DESC
                """, (service_id,))

                table.delete(*table.get_children())

                for record in records:
                    table.insert("", "end", values=record)

            except Exception as error:
                self.show_error(error, window)

        def generate_bill():
            service_id = get_service_id()
            if service_id is None:
                return

            try:
                records = self.fetch_all("""
                    SELECT s.service_id, c.name, v.registration_no,
                           s.service_type, s.service_date,
                           s.status, s.cost
                    FROM services s
                    JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                    JOIN customers c ON v.customer_id = c.customer_id
                    WHERE s.service_id = %s
                """, (service_id,))

                if not records:
                    messagebox.showwarning(
                        "Not Found",
                        "Service record not found.",
                        parent=window
                    )
                    return

                record = records[0]
                sid, customer, registration, service_type, service_date, status, cost = record

                payment_records = self.fetch_all("""
                    SELECT COALESCE(SUM(amount), 0)
                    FROM payments
                    WHERE service_id = %s
                """, (service_id,))

                paid = Decimal(str(payment_records[0][0]))
                total = Decimal(str(cost))
                balance = total - paid

                receipt = (
                    "========== VEHICLE SERVICE BILL ==========\n"
                    f"Service ID    : {sid}\n"
                    f"Customer      : {customer}\n"
                    f"Vehicle       : {registration}\n"
                    f"Service       : {service_type}\n"
                    f"Service Date  : {service_date}\n"
                    f"Status        : {status}\n"
                    "-------------------------------------------\n"
                    f"Total Cost    : Rs. {total:.2f}\n"
                    f"Paid          : Rs. {paid:.2f}\n"
                    f"Balance Due   : Rs. {balance:.2f}\n"
                    "===========================================\n"
                )

                bill_text.config(state="normal")
                bill_text.delete("1.0", tk.END)
                bill_text.insert("1.0", receipt)
                bill_text.config(state="disabled")

                refresh_payments(service_id)

            except Exception as error:
                self.show_error(error, window)

        def record_payment():
            service_id = get_service_id()
            if service_id is None:
                return

            payment_window = tk.Toplevel(window)
            payment_window.title("Record Payment")
            payment_window.geometry("350x250")

            tk.Label(
                payment_window,
                text=f"Service ID: {service_id}"
            ).pack(pady=8)

            tk.Label(
                payment_window, text="Amount (INR):"
            ).pack()

            amount_entry = tk.Entry(payment_window)
            amount_entry.pack(pady=5)

            tk.Label(
                payment_window, text="Payment Method:"
            ).pack()

            method_var = tk.StringVar(value="Cash")
            method_combo = ttk.Combobox(
                payment_window,
                textvariable=method_var,
                values=("Cash", "UPI", "Card"),
                state="readonly"
            )
            method_combo.pack(pady=5)

            def save_payment():
                try:
                    amount = Decimal(amount_entry.get().strip())

                    if not amount.is_finite() or amount <= 0:
                        raise ValueError(
                            "Payment must be greater than zero."
                        )

                    db = Database()
                    cursor = None

                    try:
                        connection = db.get_connection()
                        connection.start_transaction()
                        cursor = connection.cursor()

                        cursor.execute("""
                            SELECT cost FROM services
                            WHERE service_id = %s
                            FOR UPDATE
                        """, (service_id,))

                        service = cursor.fetchone()

                        if not service:
                            connection.rollback()
                            raise ValueError(
                                "Service record not found."
                            )

                        total = Decimal(str(service[0]))

                        cursor.execute("""
                            SELECT COALESCE(SUM(amount), 0)
                            FROM payments
                            WHERE service_id = %s
                        """, (service_id,))

                        paid = Decimal(str(cursor.fetchone()[0]))
                        balance = total - paid

                        if balance <= 0:
                            connection.rollback()
                            raise ValueError(
                                "This service is already fully paid."
                            )

                        if amount > balance:
                            connection.rollback()
                            raise ValueError(
                                f"Payment exceeds balance of Rs. {balance:.2f}."
                            )

                        cursor.execute("""
                            INSERT INTO payments
                                (service_id, amount, payment_date, payment_method)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            service_id,
                            amount,
                            date.today(),
                            method_var.get()
                        ))

                        connection.commit()
                        remaining = balance - amount

                    except Exception:
                        try:
                            db.get_connection().rollback()
                        except Exception:
                            pass
                        raise

                    finally:
                        if cursor:
                            cursor.close()
                        db.close()

                    messagebox.showinfo(
                        "Payment Successful",
                        f"Payment recorded: Rs. {amount:.2f}\n"
                        f"Remaining balance: Rs. {remaining:.2f}",
                        parent=payment_window
                    )

                    payment_window.destroy()
                    generate_bill()

                except (ValueError, InvalidOperation) as error:
                    messagebox.showerror(
                        "Payment Error", str(error),
                        parent=payment_window
                    )
                except Exception as error:
                    self.show_error(error, payment_window)

            tk.Button(
                payment_window,
                text="Save Payment",
                command=save_payment
            ).pack(pady=12)

        tk.Button(
            form, text="Generate Bill",
            command=generate_bill
        ).grid(row=0, column=2, padx=8)

        tk.Button(
            form, text="Record Payment",
            command=record_payment
        ).grid(row=0, column=3, padx=8)


if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleServiceApp(root)
    root.mainloop()
PY
