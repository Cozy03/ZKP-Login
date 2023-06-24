import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import secrets
import sqlite3
from Cryptodome.PublicKey import ECC
import hashlib
import json
from sigma import SigmaPro
from gentemp import *


class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Login")

        # Username Frame
        self.username_frame = ttk.Frame(self.window)
        self.username_frame.pack(pady=10)

        self.lbl_username = ttk.Label(self.username_frame, text="Username:")
        self.lbl_username.grid(row=0, column=0, padx=5, pady=5)

        self.entry_username = ttk.Entry(self.username_frame)
        self.entry_username.grid(row=0, column=1, padx=5, pady=5)

        self.btn_generate_challenge = ttk.Button(
            self.username_frame, text="Generate Challenge", command=self.generate_challenge
        )
        self.btn_generate_challenge.grid(row=0, column=2, padx=5, pady=5)

        # Challenge Frame
        self.challenge_frame = ttk.Frame(self.window)
        self.challenge_frame.pack(pady=10)

        self.lbl_challenge = ttk.Label(self.challenge_frame, text="Challenge:")
        self.lbl_challenge.grid(row=0, column=0, padx=5, pady=5)

        self.entry_challenge = ttk.Entry(self.challenge_frame, state="disabled")
        self.entry_challenge.grid(row=0, column=1, padx=5, pady=5)

        self.lbl_verify = ttk.Label(self.challenge_frame, text="Verify Challenge:")
        self.lbl_verify.grid(row=1, column=0, padx=5, pady=5)

        self.entry_verify = ttk.Entry(self.challenge_frame, state="disabled")
        self.entry_verify.grid(row=1, column=1, padx=5, pady=5)

        self.btn_verify = ttk.Button(
            self.challenge_frame, text="Verify", command=self.verify_challenge, state="disabled"
        )
        self.btn_verify.grid(row=1, column=2, padx=5, pady=5)

        self.window.mainloop()

    def generate_challenge(self):
        username = self.entry_username.get()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        # Check if the user exists in the database
        exists = self.check_user_exists(username)

        if exists:
            # Enable challenge-related widgets
            self.entry_challenge.config(state="normal")
            self.entry_verify.config(state="normal")
            self.btn_verify.config(state="normal")

            # Generate challenge and display
            challenge = self.generate_challenge_value()
            self.entry_challenge.delete(0, tk.END)
            self.entry_challenge.insert(0, challenge)
        else:
            messagebox.showerror("Error", "User does not exist.")

    def verify_challenge(self):
        username = self.entry_username.get()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        challenge = self.entry_challenge.get()
        verify_input = self.entry_verify.get()
        sigma_pro = SigmaPro("mydatabase.db", "server_private_key.pem")

        if not challenge or not verify_input:
            messagebox.showerror("Error", "Please enter both the challenge and verification values.")
            return

        public_key = sigma_pro.get_public_key(username)

        if public_key:
            sks = sigma_pro.load_private_key()
            ss_server = sigma_pro.multiply_keys(public_key, sks)
            print(ss_server)
            server_calculation = sigma_pro.server_calculation(ss_server, challenge)
            print(server_calculation.hex())
            if verify_input == server_calculation.hex():
                messagebox.showinfo("Success", "Verification successful. User logged in.")
                self.open_login_screen()
            else:
                messagebox.showerror("Error", "Verification failed. Invalid challenge.")
        else:
            messagebox.showerror("Error", "Public key not found for the user.")

    def check_user_exists(self, username):
        connection = sqlite3.connect("mydatabase.db")
        cursor = connection.cursor()
        cursor.execute("SELECT Username FROM users WHERE Username = ?", (username,))
        result = cursor.fetchone()
        connection.close()
        return result is not None

    def generate_challenge_value(self):
        challenge = secrets.token_hex(16)
        return challenge

    def open_login_screen(self):
        self.window.destroy()

        login_screen = tk.Tk()
        login_screen.title("Login Screen")

        self.display_box = tk.Text(login_screen, width=60, height=20)
        self.display_box.pack()

        btn_get_temperature = ttk.Button(
            login_screen, text="Get Temperature", command=self.generate_temps
        )
        btn_get_temperature.pack()

        btn_stop_generating = ttk.Button(
            login_screen, text="Stop Generating", command=self.stop_generating_temps
        )
        btn_stop_generating.pack()

        btn_back = ttk.Button(login_screen, text="Back", command=self.back_to_main)
        btn_back.pack()

        self.login_screen = login_screen
        self.device_id = "DEVICE001"
        self.generate_temp = False  # Set generate_temp to False initially
        # self.generate_temps()  # Removed the immediate generation of temperature

        login_screen.mainloop()

    def back_to_main(self):
        self.window.deiconify()

    def generate_temp_and_send(self):
        if self.generate_temp:
            temperature_data = generate_temperature(self.device_id)
            json_data = json.dumps(temperature_data)
            self.display_box.insert(tk.END, json_data)
            self.display_box.insert(tk.END, "\n")
            self.display_box.see(tk.END)
            send_temperature_data(temperature_data)

    def generate_temps(self):
        self.generate_temp = True
        self.generate_temp_and_send()
        self.login_screen.after(2000, self.generate_temps)  # Generate the next temperature after 2 seconds

    def stop_generating_temps(self):
        self.generate_temp = False

    def print_button_click(self):
        print("Button clicked")


if __name__ == "__main__":
    login_window = LoginWindow()