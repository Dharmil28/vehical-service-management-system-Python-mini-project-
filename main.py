
from datetime import date
from database import Database
from customer import Customer
from vehicle import Vehicle
from service import Service
from billing import Billing


def main():
    while True:
        print("\n====== VEHICLE SERVICE MANAGEMENT SYSTEM ======")
        print("1.  Add Customer")
        print("2.  View Customers")
        print("3.  Search Customer")
        print("4.  Register Vehicle")
        print("5.  View Vehicles")
        print("6.  Search Vehicle")
        print("7.  Book Service")
        print("8.  View Services")
        print("9.  Update Service Status")
        print("10. Generate Bill")
        print("11. Record Payment")
        print("12. Exit")

        choice = input("Enter your choice (1-12): ").strip()

        try:
            if choice == "1":
                name = input("Customer name: ").strip()
                phone = input("Phone: ").strip()
                email = input("Email: ").strip()
                address = input("Address: ").strip()

                if not name or not phone:
                    print("Name and phone are required.")
                    continue

                Customer(name, phone, email, address).add_customer()

            elif choice == "2":
                Customer.view_customers()

            elif choice == "3":
                customer_id = int(input("Customer ID: "))
                Customer.search_customer(customer_id)

            elif choice == "4":
                customer_id = int(input("Customer ID: "))
                registration = input("Registration number: ").strip()
                brand = input("Vehicle brand: ").strip()
                model = input("Vehicle model: ").strip()

                if not registration:
                    print("Registration number is required.")
                    continue

                Vehicle(
                    customer_id, registration, brand, model
                ).add_vehicle()

            elif choice == "5":
                Vehicle.view_vehicles()

            elif choice == "6":
                vehicle_id = int(input("Vehicle ID: "))
                Vehicle.search_vehicle(vehicle_id)

            elif choice == "7":
                vehicle_id = int(input("Vehicle ID: "))
                service_type = input("Service type: ").strip()
                service_date = input("Date (YYYY-MM-DD): ").strip()
                date.fromisoformat(service_date)
                cost = input("Service cost: ").strip()

                if not service_type:
                    print("Service type is required.")
                    continue

                Service(
                    vehicle_id, service_type, service_date, cost
                ).book_service()

            elif choice == "8":
                Service.view_services()

            elif choice == "9":
                service_id = int(input("Service ID: "))
                print("1. Pending")
                print("2. In Progress")
                print("3. Completed")

                status_choice = input("Choose status: ").strip()
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
                    print("Invalid status choice.")

            elif choice == "10":
                service_id = int(input("Service ID: "))
                Billing(service_id).generate_bill()

            elif choice == "11":
                service_id = int(input("Service ID: "))
                amount = input("Payment amount: ").strip()
                method = input("Payment method (Cash/UPI/Card): ").strip().lower()

                methods = {
                    "cash": "Cash",
                    "upi": "Upi",
                    "card": "Card"
                }

                if method not in methods:
                    print("Choose Cash, UPI, or Card.")
                    continue

                Billing(service_id).make_payment(
                    amount, methods[method]
                )

            elif choice == "12":
                print("Thank you for using the system!")
                break

            else:
                print("Invalid choice. Enter a number from 1 to 12.")

        except ValueError:
            print("Invalid input. Check your ID, date, and amount.")
        except Exception as error:
            print("An unexpected error occurred:", error)


if __name__ == "__main__":
    main()

