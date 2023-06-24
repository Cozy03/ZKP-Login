import secrets
import sqlite3
from Cryptodome.PublicKey import ECC
import hashlib

class SigmaPro:
    def __init__(self, database_file, key_file):
        self.database_file = database_file
        self.key_file = key_file
        self.private_key = self.load_private_key()
        self.db_connection = self.connect_to_database()

    def load_private_key(self):
        with open(self.key_file, 'rb') as key_file:
            pem_data = key_file.read()
            private_key = ECC.import_key(pem_data)
        return private_key

    def connect_to_database(self):
        connection = sqlite3.connect(self.database_file)
        return connection

    def retrieve_database_contents(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT Username, DeviceId, PublicKey FROM users")
        rows = cursor.fetchall()
        return rows

    def load_private_key_from_pem(self, pem_file):
        with open(pem_file, 'rb') as file:
            pem_data = file.read()
            private_key = ECC.import_key(pem_data)
        return private_key

    def get_public_key(self, username):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT PublicKey FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result is not None:
            public_key_bytes = result[0]
            public_key = ECC.import_key(public_key_bytes)
            return public_key
        else:
            return None
    
    def get_public_key_from_private_key(self, private_key):
        # Load the private key
        return private_key.public_key()


    def generate_client_key(self):
        private_key = ECC.generate(curve='P-256')
        # public_key = private_key.public_key()
        return private_key

    def multiply_keys(self, public_key, private_key):
        shared_key = public_key.pointQ * private_key.d
        return shared_key

    def register_user(self, username, public_key, device_id):
        cursor = self.db_connection.cursor()
        cursor.execute("INSERT INTO users (Username, DeviceId, PublicKey) VALUES (?, ?, ?)",
                       (username, device_id, public_key.export_key(format='PEM')))
        self.db_connection.commit()


    def generate_challenge(self):
        challenge = secrets.token_hex(16)
        return challenge

    def hashing_ss(self, shared_key):
        x_shared_key = shared_key.x.to_bytes(32, byteorder='big')
        y_shared_key = shared_key.y.to_bytes(32, byteorder='big')
        hashed_shared_key = hashlib.sha256(x_shared_key + y_shared_key).digest()
        return hashed_shared_key
      

    def client_calculation(self, ssc, r):
        hashed_ssc = self.hashing_ss(ssc)
        hashed_r = hashlib.sha256(r.encode()).digest()
        val = hashed_ssc + hashed_r
        return val

    def server_calculation(self, sss, r):
        hashed_sss = self.hashing_ss(sss)
        hashed_r = hashlib.sha256(r.encode()).digest()
        val = hashed_sss + hashed_r
        return val


def test_challenge():
    my_instance = SigmaPro("mydatabase.db", "server_private_key.pem")
    # Register a user
    username = "Raj"
    # private_key_c= my_instance.generate_client_key()
    private_key_c = ECC.generate(curve='P-256')
    public_key_c=my_instance.get_public_key_from_private_key(private_key_c)
    with open('raj_key.pem', 'wt') as file:
        file.write(private_key_c.export_key(format='PEM'))

    my_instance.register_user(username, public_key_c,'DEV101')
    sks=my_instance.load_private_key()
    pks=my_instance.get_public_key_from_private_key(sks)
    ss_client=my_instance.multiply_keys(pks,private_key_c)
    ss_server=my_instance.multiply_keys(public_key_c,sks)
    print(ss_client==ss_server)
    challenge=my_instance.generate_challenge()
    challenge1=my_instance.generate_challenge()
    clientcal= my_instance.client_calculation(ss_client,challenge)
    print(clientcal==my_instance.server_calculation(ss_server,challenge))


# test_challenge()