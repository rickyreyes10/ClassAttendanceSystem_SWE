import os
import tkinter as tk
from main_window import MainWindow


# This MainApp class acts as the primary controller for the GUI application.
class MainApp:
    # Constructor for the MainApp class.
    # Initializes the main application window.
    def __init__(self, root):
        # root is the primary window for the application.
        self.root = root

        # Ensure the 'db' directory exists, if not, create it
        if not os.path.exists('./db'):
            os.makedirs('./db')


        # The main_window is an instance of the MainWindow class,
        # which represents the main interface of the application.
        self.main_window = MainWindow(root)

# This is the entry point of the program.
# If this script is run as the main module, the following code will execute.
if __name__ == "__main__":
    # Initialize the primary tkinter window.
    root = tk.Tk()
    # Create an instance of our main application class.
    app = MainApp(root)
    # Start the tkinter event loop.
    # This will display the window and make the program wait for user interactions.
    root.mainloop()
