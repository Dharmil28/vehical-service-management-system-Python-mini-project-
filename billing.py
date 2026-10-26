
from datetime import date
from decimal import Decimal
from database import Database


class Billing:
    def __init__(self, service_id):
        self.service_id = service_id

    def generate_bill(self):
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT s.service_id, c.name, v.registration_no,
                       s.service_type, s.cost, s.status
                FROM services s
                JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                JOIN customers c ON v.customer_id = c.customer_id
                WHERE s.service_id = %s
            """

            cursor.execute(query, (self.service_id,))
            bill = cursor.fetchone()

            if not bill:
                print("Service record not found.")
                return

            service_id, name, registration, service_type, cost, status = bill

            print("\n========== VEHICLE SERVICE BILL ==========")
            print("Bill / Service ID :", service_id)
            print("Customer          :", name)
            print("Vehicle Number    :", registration)
            print("Service           :", service_type)
            print("Service Cost      : ₹", cost)
            print("Service Status    :", status)
            print("==========================================")

        except Exception as error:
            print("Error:", error)

        finally:
            cursor.close()
            db.close()

    def make_payment(self, amount, payment_method):
        amount = Decimal(str(amount))

        if amount <= 0:
            print("Payment amount must be greater than zero.")
            return

        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            connection.start_transaction()

            cursor.execute(
                "SELECT cost FROM services WHERE service_id = %s",
                (self.service_id,)
            )
            service = cursor.fetchone()

            if not service:
                print("Service record not found.")
                connection.rollback()
                return

            service_cost = Decimal(str(service[0]))

            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE service_id = %s
                """,
                (self.service_id,)
            )
            paid = Decimal(str(cursor.fetchone()[0]))
            balance = service_cost - paid

            if balance <= 0:
                print("This service is already fully paid.")
                connection.rollback()
                return

            if amount > balance:
                print("Payment exceeds the outstanding balance.")
                print("Balance due: ₹", balance)
                connection.rollback()
                return

            cursor.execute(
                """
                INSERT INTO payments
                    (service_id, amount, payment_date, payment_method)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    self.service_id,
                    amount,
                    date.today(),
                    payment_method
                )
            )

            connection.commit()
            print("Payment recorded successfully!")
            print("Amount paid: ₹", amount)
            print("Remaining balance: ₹", balance - amount)

        except Exception as error:
            connection.rollback()
            print("Error:", error)

        finally:
            cursor.close()
            db.close()


if __name__ == "__main__":
    while True:
        print("\n--- Billing & Payments ---")
        print("1. Generate Bill")
        print("2. Record Payment")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            try:
                service_id = int(input("Enter service ID: "))
                Billing(service_id).generate_bill()
            except ValueError:
                print("Enter a valid service ID.")

        elif choice == "2":
            try:
                service_id = int(input("Enter service ID: "))
                amount = input("Enter payment amount: ").strip()
                method = input(
                    "Payment method (Cash/UPI/Card): "
                ).strip().title()

                if method not in ("Cash", "Upi", "Card"):
                    print("Choose Cash, UPI, or Card.")
                    continue

                Billing(service_id).make_payment(amount, method)

            except ValueError:
                print("Enter a valid service ID and amount.")

        elif choice == "3":
            break

        else:
            print("Invalid choice.")

