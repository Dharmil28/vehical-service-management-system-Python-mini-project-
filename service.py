
from datetime import date
from decimal import Decimal
from database import Database


class Service:
    def __init__(self, vehicle_id, service_type, service_date, cost=0):
        self.vehicle_id = vehicle_id
        self.service_type = service_type
        self.service_date = service_date
        self.cost = Decimal(str(cost))

    def book_service(self):
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO services
                (vehicle_id, service_type, service_date, cost)
            VALUES (%s, %s, %s, %s)
        """

        try:
            cursor.execute(query, (
                self.vehicle_id,
                self.service_type,
                self.service_date,
                self.cost
            ))
            connection.commit()
            print("Service booked successfully!")
            print("Service ID:", cursor.lastrowid)

        except Exception as error:
            connection.rollback()
            print("Error:", error)

        finally:
            cursor.close()
            db.close()

    @staticmethod
    def view_services():
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT s.service_id, v.registration_no,
                       s.service_type, s.service_date,
                       s.status, s.cost
                FROM services s
                JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                ORDER BY s.service_id
            """
            cursor.execute(query)

            records = cursor.fetchall()

            if not records:
                print("No service records found.")
            else:
                for record in records:
                    print(record)

        except Exception as error:
            print("Error:", error)

        finally:
            cursor.close()
            db.close()

    @staticmethod
    def update_status(service_id, status):
        allowed_statuses = (
            "Pending", "In Progress", "Completed"
        )

        if status not in allowed_statuses:
            print("Invalid status.")
            return

        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "UPDATE services SET status = %s WHERE service_id = %s",
                (status, service_id)
            )
            connection.commit()

            if cursor.rowcount:
                print("Service status updated successfully!")
            else:
                print("Service ID not found.")

        except Exception as error:
            connection.rollback()
            print("Error:", error)

        finally:
            cursor.close()
            db.close()


if __name__ == "__main__":
    while True:
        print("\n--- Service Management ---")
        print("1. Book Service")
        print("2. View Services")
        print("3. Update Service Status")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            try:
                vehicle_id = int(input("Enter vehicle ID: "))
                service_type = input("Enter service type: ").strip()
                service_date = input(
                    "Enter date (YYYY-MM-DD): "
                ).strip()
                date.fromisoformat(service_date)

                cost = input("Enter service cost: ").strip()

                if not service_type:
                    print("Service type cannot be empty.")
                    continue

                service = Service(
                    vehicle_id, service_type, service_date, cost
                )
                service.book_service()

            except ValueError:
                print("Enter a valid date, vehicle ID, and cost.")

        elif choice == "2":
            Service.view_services()

        elif choice == "3":
            try:
                service_id = int(input("Enter service ID: "))
                print("1. Pending")
                print("2. In Progress")
                print("3. Completed")

                status_choice = input("Choose new status: ").strip()

                statuses = {
                    "1": "Pending",
                    "2": "In Progress",
                    "3": "Completed"
                }

                if status_choice in statuses:
                    Service.update_status(
                        service_id, statuses[status_choice]
                    )
                else:
                    print("Invalid choice.")

            except ValueError:
                print("Service ID must be a number.")

        elif choice == "4":
            break

        else:
            print("Invalid choice. Enter 1 to 4.")

