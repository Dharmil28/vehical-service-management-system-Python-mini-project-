
from database import Database


class Customer:
    def __init__(self, name, phone, email="", address=""):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address

    def add_customer(self):
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO customers (name, phone, email, address)
            VALUES (%s, %s, %s, %s)
        """

        values = (self.name, self.phone, self.email, self.address)

        try:
            cursor.execute(query, values)
            connection.commit()
            print("Customer added successfully!")
            print("Customer ID:", cursor.lastrowid)
        except Exception as error:
            connection.rollback()
            print("Error:", error)
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def view_customers():
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()

            if not customers:
                print("No customers found.")
                return

            for customer in customers:
                print(customer)

        except Exception as error:
            print("Error:", error)
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def search_customer(customer_id):
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT * FROM customers WHERE customer_id = %s",
                (customer_id,)
            )
            customer = cursor.fetchone()

            if customer:
                print(customer)
            else:
                print("Customer not found.")

        except Exception as error:
            print("Error:", error)
        finally:
            cursor.close()
            db.close()


if __name__ == "__main__":
    while True:
        print("\n--- Customer Management ---")
        print("1. Add Customer")
        print("2. View Customers")
        print("3. Search Customer")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            email = input("Enter email: ")
            address = input("Enter address: ")

            customer = Customer(name, phone, email, address)
            customer.add_customer()

        elif choice == "2":
            Customer.view_customers()

        elif choice == "3":
            try:
                customer_id = int(input("Enter customer ID: "))
                Customer.search_customer(customer_id)
            except ValueError:
                print("Please enter a valid numeric ID.")

        elif choice == "4":
            print("Exiting Customer Management.")
            break

        else:
            print("Invalid choice. Try again.")

