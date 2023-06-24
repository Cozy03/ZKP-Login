import secrets
import sqlite3
from Cryptodome.PublicKey import ECC
import hashlib

class SigmaPro:
    def __init__(self, database_file):
        self.database_file = database_file
        self.db_connection = self.connect_to_database()

    def connect_to_database(self):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()

        # Create the users table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (Username TEXT PRIMARY KEY,
                           DeviceId TEXT,
                           PublicKey BLOB,
                           Blocked INTEGER DEFAULT 0)''')

        connection.commit()

        return connection

    def register_user(self, username, device_id):
        # Generate ECC key pair
        private_key = ECC.generate(curve='P-256')
        public_key = private_key.public_key().export_key(format='PEM')

        cursor = self.db_connection.cursor()

        # Insert user information into the database
        cursor.execute("INSERT INTO users (Username, DeviceId, PublicKey) VALUES (?, ?, ?)",
                       (username, device_id, public_key))

        self.db_connection.commit()

    def retrieve_user_public_key(self, username):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT PublicKey FROM users WHERE Username = ?", (username,))
        result = cursor.fetchone()

        if result is not None:
            public_key_bytes = result[0]
            public_key = ECC.import_key(public_key_bytes)
            return public_key
        else:
            return None

# Example usage
if __name__ == "__main__":
    database_file = "mydatabase.db"

    # Create SigmaPro instance and connect to the database
    sigma_pro = SigmaPro(database_file)

    # Register users with device IDs
    sigma_pro.register_user("Bob", "Device001")
    sigma_pro.register_user("Alice", "Device002")
    sigma_pro.register_user("Eve", "Device003")

    # Retrieve and print public key for a user
    bob_public_key = sigma_pro.retrieve_user_public_key("Bob")
    if bob_public_key:
        print(f"Bob's Public Key: {bob_public_key.export_key(format='PEM')}")
    else:
        print("User not found.")
