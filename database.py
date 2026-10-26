import mysql.connector


class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="vehicle_service_db"
        )

    def get_connection(self):
        return self.connection

    def close(self):
        if self.connection.is_connected():
            self.connection.close()


if __name__ == "__main__":
    try:
        db = Database()
        print("MySQL connected successfully!")
        db.close()
    except mysql.connector.Error as error:
        print("Database connection failed:", error)
