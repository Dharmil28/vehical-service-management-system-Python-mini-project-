
from database import Database


class Vehicle:
    def __init__(self, customer_id, registration_no, brand, model):
        self.customer_id = customer_id
        self.registration_no = registration_no
        self.brand = brand
        self.model = model

    def add_vehicle(self):
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO vehicles
            (customer_id, registration_no, brand, model)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            self.customer_id,
            self.registration_no,
            self.brand,
            self.model
        )

        try:
            cursor.execute(query, values)
            connection.commit()
            print("Vehicle registered successfully!")
            print("Vehicle ID:", cursor.lastrowid)
        except Exception as error:
            connection.rollback()
            print("Error:", error)
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def view_vehicles():
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT v.vehicle_id, c.name, v.registration_no,
                       v.brand, v.model
                FROM vehicles v
                JOIN customers c
                    ON v.customer_id = c.customer_id
            """
            cursor.execute(query)

            vehicles = cursor.fetchall()

            if not vehicles:
                print("No vehicles found.")
            else:
                for vehicle in vehicles:
                    print(vehicle)

        except Exception as error:
            print("Error:", error)
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def search_vehicle(vehicle_id):
        db = Database()
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT * FROM vehicles WHERE vehicle_id = %s",
                (vehicle_id,)
            )
            vehicle = cursor.fetchone()

            if vehicle:
                print(vehicle)
            else:
                print("Vehicle not found.")

        except Exception as error:
            print("Error:", error)
        finally:
            cursor.close()
            db.close()


if __name__ == "__main__":
    while True:
        print("\n--- Vehicle Management ---")
        print("1. Register Vehicle")
        print("2. View Vehicles")
        print("3. Search Vehicle")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                customer_id = int(input("Enter customer ID: "))
                registration_no = input("Enter registration number: ")
                brand = input("Enter brand: ")
                model = input("Enter model: ")

                vehicle = Vehicle(
                    customer_id, registration_no, brand, model
                )
                vehicle.add_vehicle()
            except ValueError:
                print("Customer ID must be a number.")

        elif choice == "2":
            Vehicle.view_vehicles()

        elif choice == "3":
            try:
                vehicle_id = int(input("Enter vehicle ID: "))
                Vehicle.search_vehicle(vehicle_id)
            except ValueError:
                print("Vehicle ID must be a number.")

        elif choice == "4":
            print("Exiting Vehicle Management.")
            break

        else:
            print("Invalid choice. Try again.")

