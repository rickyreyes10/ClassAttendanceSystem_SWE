import tkinter as tk
from tkinter import messagebox, dialog
import pickle
import os
import face_recognition

# Global or constant for database path
DB_PATH = "./db"
FACIAL_RECOGNITION_PATH = "facial_recognition"

#Return the specific path for a given CRN (Course Registration Number)
def get_crn_specific_path(crn):
    return os.path.join(DB_PATH, crn, FACIAL_RECOGNITION_PATH)

#Creates and returns a tkinter button with specified properties.
def get_button(window, text, color, command, fg='white', font_size=20, height=2, width=20):
    """
    Creates a button with specified properties.

    Parameters:
        window: tk.Tk or tk.Toplevel
            The tkinter window where the button will be placed.
        text: str
            Text to display on the button.
        color: str
            Background color of the button.
        command: function
            The function to be executed when the button is clicked.
        fg: str, optional
            Foreground color of the button. Default is 'white'.
        font_size: int, optional
            Font size of the text. Default is 20.
        height: int, optional
            Height of the button. Default is 2.
        width: int, optional
            Width of the button. Default is 20.

    Returns:
        tk.Button: A tkinter Button object.
    """
    button = tk.Button(
        window,
        text=text,
        activebackground="black",
        activeforeground="white",
        fg=fg,
        bg=color,
        command=command,
        height=height,
        width=width,
        font=(f'Helvetica bold', font_size)
    )
    return button

#Display a custom modal dialog box with a specified title, message, and button text.
def custom_dialog(title, message, button_text):
    def on_button_click():
        dialog.destroy()

    dialog = tk.Toplevel()
    dialog.title(title)
    tk.Label(dialog, text=message).pack(padx=20, pady=20)
    tk.Button(dialog, text=button_text, command=on_button_click).pack(pady=10)
    dialog.grab_set() #make it modal

#Create and return a tkinter label for displaying images.
def get_img_label(root, bg=None):
    label = tk.Label(root)
    if bg:
        label.configure(bg=bg)
    return label

#Create and return a text label with specified properties.
def get_text_label(window, text, font_size=21, justify="left", fg_color='white', bg_color='black'):
    label = tk.Label(window, text=text, fg=fg_color, bg=bg_color)
    label.config(font=("sans-serif", font_size), justify=justify)
    return label

#Create and return a tkinter text entry widget with specified properties.
def get_entry_text(window, height=2, width=15, font_size=32):
    txt_input = tk.Text(window, height=height, width=width, font=("Arial", font_size))
    return txt_input

#Display an informational message box with a specified title and description.
def msg_box(title, description):
    messagebox.showinfo(title, description)

#Save the face encoding for a specific CRN (Course Registration Number) to disk.
def save_face_encoding(crn, filename, encoding):
    crn_path = get_crn_specific_path(crn)
    if not os.path.exists(crn_path):
        os.makedirs(crn_path)
    with open(os.path.join(crn_path, filename), 'wb') as f:
        pickle.dump(encoding, f)

#Attempt to recognize a face in an image based on known encodings for a given CRN.
def recognize(face_image, crn):
    crn_path = get_crn_specific_path(crn)

    face_locations = face_recognition.face_locations(face_image)
    if len(face_locations) == 0:
        return 'no_persons_found'

    face_encodings = face_recognition.face_encodings(face_image, face_locations)

    for face_encoding in face_encodings:
        for filename in os.listdir(crn_path):
            if filename.endswith('.pkl'):
                with open(os.path.join(crn_path, filename), 'rb') as f:
                    known_face_encoding = pickle.load(f)

                matches = face_recognition.compare_faces([known_face_encoding], face_encoding)

                print(f"Matches for {filename}: {matches}")  # Debug line

                if True in matches:
                    print(f"Matched with filename: {filename}")  # Debug line
                    return filename.replace('.pkl', '')

    return 'unknown_person'

#Retrieve the closest matching filename for a given face encoding and CRN
def get_closest_match(face_encoding, crn):
    crn_path = get_crn_specific_path(crn)
    closest_match = None
    closest_distance = 0.6  # You can adjust the threshold

    for filename in os.listdir(crn_path):
        if filename.endswith('.pkl'):
            with open(os.path.join(crn_path, filename), 'rb') as f:
                known_face_encoding = pickle.load(f)

            distances = face_recognition.face_distance([known_face_encoding], face_encoding)
            if distances[0] < closest_distance:
                closest_distance = distances[0]
                closest_match = filename.replace('.pkl', '')

    return closest_match


#Attempt to recognize a face from its encoding based on known encodings for a given CRN.
def recognize_from_encoding(face_encoding, crn):
    crn_path = get_crn_specific_path(crn)
    closest_match = None
    closest_distance = 0.6  # You can adjust the threshold

    for filename in os.listdir(crn_path):
        if filename.endswith('.pkl'):
            with open(os.path.join(crn_path, filename), 'rb') as f:
                known_face_encoding = pickle.load(f)

            distances = face_recognition.face_distance([known_face_encoding], face_encoding)
            if distances[0] < closest_distance:
                closest_distance = distances[0]
                closest_match = filename.replace('.pkl', '')

    return closest_match or 'unknown_person'


