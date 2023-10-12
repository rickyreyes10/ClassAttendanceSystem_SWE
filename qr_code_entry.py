import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import cv2
import qrcode
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import util
from datetime import datetime
import json

class QRCodeEntryApp:
    def __init__(self, root, crn):
        self.root = root

        # Define paths for database and QR code directory
        self.crn_directory_path = f"./db/{crn}"
        self.qr_code_directory = f"{self.crn_directory_path}/qr_codes"
        self.event_log_path = f"{self.crn_directory_path}/event_log.txt"

        # Create directory for QR codes if not exists
        if not os.path.exists(self.qr_code_directory):
            os.makedirs(self.qr_code_directory)

        # Window settings
        self.root.title("QR Code Entry System")
        self.root.geometry("1200x750")
        self.root.configure(bg='black')
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)

        # Initialize UI elements and webcam
        self.initialize_ui()
        self.start_webcam()


    # Create and set up the webcam display label
    def initialize_ui(self):
        self.webcam_label = util.get_img_label(self.root)
        self.webcam_label.config(width=640, height=400)
        self.webcam_label.pack(pady=10)

        # Create and set up the 'Register' button
        self.register_button = util.get_button(self.root, 'Register', 'gray', self.register)
        self.register_button.pack(pady=10)

        # Create and set up the 'Retrieve QR' button
        self.retrieve_button = util.get_button(self.root, 'Retrieve QR', 'blue', self.retrieve_qr_code)
        self.retrieve_button.pack(pady=10)

        # Create and set up the 'Exit' button
        self.exit_button = util.get_button(self.root, "Exit", 'red', self.destroy)
        self.exit_button.pack(pady=10)


    # Initialize webcam
    def start_webcam(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showinfo('Error', 'Could not open video device')
            return
        self.process_webcam()

    # Capture and process frames from the webcam
    def process_webcam(self):
        ret, frame = self.cap.read()
        self.most_recent_capture = frame
        qr_info = decode(frame)

        detected = False    # initialize the detected flag

        if not ret:
            return

        # Check if a QR code is detected in the frame
        for qr in qr_info:
            data = qr.data.decode('utf-8')

            try:
                cleaned_data = data.replace("'", '"')
                self.data = json.loads(cleaned_data) #parse the cleaned JSON string into a dictionary
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Received data: {data}")
                return

            # Highlight the QR code area
            rect = qr.rect
            frame = cv2.rectangle(frame, (rect.left, rect.top),
                                  (rect.left + rect.width, rect.top + rect.height), (0, 255, 0), 2)

            # Extract user info and log the attendance
            username = self.data.get('username', 'Unknown')
            email = self.data.get('email', 'Unknown')

            #record attendance
            self.log_event(username, email, 'Present')
            messagebox.showinfo('QR Code Detected', f'Welcome {username}, attendance marked!')

            detected = True    # mark that a QR code was detected

            self.reset_for_next_login()     # reset for next login


        # Display the processed frame in the UI
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (640, 480))

        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)

        self.webcam_label.imgtk = imgtk
        self.webcam_label.configure(image=imgtk)

        # allows the webcam to continue running even after a QR code is detected and processed
        self.webcam_label.after(10, self.process_webcam)


    # Reset data for the next login attempt
    def reset_for_next_login(self):
        self.data = {}


    # Stop the webcam and release resources
    def stop_webcam(self):
        self.cap.release()


    # Display a given QR code image in a new window, once registered
    def show_qr_code(self, img_path):
        new_window = tk.Toplevel(self.root)
        new_window.title("Your QR Code")

        img = Image.open(img_path)
        img = img.resize((300, 300), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)

        label = tk.Label(new_window, image=img)
        label.image = img
        label.pack()



    def register(self):
        # Open registration form window
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register")

        # Username input
        username_label = util.get_text_label(self.register_window, "Username:", font_size=16)
        username_label.pack()

        self.username_entry = util.get_entry_text(self.register_window, height=1, width=30, font_size=16)
        self.username_entry.pack()

        # Email input
        email_label = util.get_text_label(self.register_window, "Email:", font_size=16)
        email_label.pack()

        self.email_entry = util.get_entry_text(self.register_window, height=1, width=30, font_size=16)
        self.email_entry.pack()

        # Submit registration button
        submit_button = util.get_button(self.register_window, 'Submit', 'green', self.submit_registration)
        submit_button.pack()

        self.register_window.grab_set()

    def submit_registration(self):
        # Process the registration form submission
        username = self.username_entry.get("1.0", 'end-1c').strip()
        email = self.email_entry.get("1.0", 'end-1c').strip()

        if username and email:
            # check if this email is already registered
            img_path = f"{self.qr_code_directory}/{email}.png"

            if os.path.exists(img_path):
                messagebox.showwarning('Registration Failed', f'Email {email} is already registered.')
                return

            # Generate the QR code for the new registration
            qr_data = {
                "username": username,
                "email": email
            }

            json_str = json.dumps(qr_data)

            self.generate_qr_code(json_str, img_path)

            messagebox.showinfo('Registration Successful', f'Registered as {username}. QR code saved at {img_path}')

            self.show_qr_code(img_path)

            self.register_window.destroy()


    def generate_qr_code(self, json_str, img_path):
        # Generate a QR code image from a given JSON string
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json_str)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        img.save(img_path)


    # Retrieve a user's QR code using their email address
    def retrieve_qr_code(self):
        email = simpledialog.askstring("Retrieve QR", "Enter your email: ")
        if not email:
            return

        img_path = f"{self.qr_code_directory}/{email}.png"

        if not os.path.exists(img_path):
            messagebox.showwarning('Retrieve QR', 'QR code not found.')
            return

        self.show_qr_code(img_path)

    # Logs the given event (user action) to the event log file with a timestamp.
    def log_event(self, username, email, action):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{current_time}, {username}, {email}, {action}\n"

        with open(self.event_log_path, 'a') as log_file:
            log_file.write(log_message)


    #Closes the application safely, ensuring the webcam is released and the Tkinter main loop is stopped.
    def destroy(self):
        self.stop_webcam()
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        self.root.quit()

#Initializes and runs the main window for the QR Code Entry application
def run_qr_code_entry_window(crn):
    root = tk.Tk()
    app = QRCodeEntryApp(root, crn)
    root.mainloop()