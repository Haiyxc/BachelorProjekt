import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import threading
import cv2

class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Workout Tracker")
        
        # Create a dropdown for workout selection
        self.workout_var = tk.StringVar(master)
        self.workout_var.set("Choose your workout")  # default value
        self.workouts = ['Push-Ups', 'Sit-Ups', 'Squats']
        self.workout_menu = tk.OptionMenu(master, self.workout_var, *self.workouts)
        self.workout_menu.pack()

        # Create a label for the timer
        self.timer_label = tk.Label(master, text="00:00:00", font=("Arial", 24))
        self.timer_label.pack()

        # Create a label for the reps count
        self.reps_label = tk.Label(master, text="Reps: 0", font=("Arial", 24))
        self.reps_label.pack()

        # Create a label for feedback
        self.feedback_label = tk.Label(master, text="Start your workout", font=("Arial", 14))
        self.feedback_label.pack()

        # Start and stop buttons (no functionality yet)
        self.start_button = tk.Button(master, text="Start", font=("Arial", 14))
        self.start_button.pack(side=tk.LEFT, padx=(20, 10), pady=(20, 20))

        self.stop_button = tk.Button(master, text="Stop", font=("Arial", 14))
        self.stop_button.pack(side=tk.RIGHT, padx=(10, 20), pady=(20, 20))

        self.skeleton_image_label = tk.Label(master)
        self.skeleton_image_label.pack()

 
def update_gui_image(self, cv_image):
    # Ensure the image is not None and has content
    if cv_image is None or cv_image.size == 0:
        print("Received empty or None image in GUI.")
        return

    # Proceed with conversion and display
    image_pil = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
    image_tk = ImageTk.PhotoImage(image_pil)
    self.skeleton_image_label.configure(image=image_tk)
    self.skeleton_image_label.image = image_tk



# Create the main window and pass it to the GUI class
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()
