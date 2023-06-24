from sigma import *


my = SigmaPro("mydatabase.db", "server_private_key.pem")
# Register a user
username = "Raj"

key=my.load_private_key_from_pem("raj_key.pem")
sks=my.load_private_key()
pks=my.get_public_key_from_private_key(sks)
ss_client=my.multiply_keys(pks,key)
print(ss_client)

challenge=input("What is the challenge?\n")

clientcal= my.client_calculation(ss_client,challenge)

print(clientcal.hex())