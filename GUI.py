import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import threading
import cv2
import time
import winsound
from pushUps import PushupCounter  # Ensure correct import path


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Workout Tracker")
       
        # Timer variables
        self.timer_active = False
        self.start_time = 0
        self.countdown_value = 5  # Countdown 5 seconds
       
        # Push-Up Counter
        self.pushup_thread = None
       
        # Create a dropdown for workout selection
        self.workout_var = tk.StringVar(master)
        self.workout_var.set("Choose your workout")  # default value
        self.workouts = ['Push-Ups', 'Sit-Ups', 'Bizeps-Cur']
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


        # Start and stop buttons with functionality
        self.start_button = tk.Button(master, text="Start", font=("Arial", 14), command=self.start_pushup_and_countdown)
        self.start_button.pack(side=tk.LEFT, padx=(20, 10), pady=(20, 20))


        self.stop_button = tk.Button(master, text="Stop", font=("Arial", 14), command=self.stop_timer_and_counter)
        self.stop_button.pack(side=tk.RIGHT, padx=(10, 20), pady=(20, 20))


        self.skeleton_image_label = tk.Label(master)
        self.skeleton_image_label.pack()


    def start_pushup_and_countdown(self):
        selected_workout = self.workout_var.get()
        if selected_workout == "Push-Ups":
            self.start_pushup_counter()
            self.start_countdown()


    def stop_timer_and_counter(self):
        self.timer_active = False
        if self.pushup_thread and self.pushup_thread.is_alive():
            self.pushup_counter_instance.stop()  # Gracefully signal the thread to stop
            self.pushup_thread.join()  # Wait for the thread to finish
        self.feedback_label.config(text="Workout has been stopped")


    def start_countdown(self):
        if self.countdown_value >= 0:
           
            if self.countdown_value == 0:  # Last second high-pitched beep
                self.feedback_label.config(text=f"Workout started!")
                winsound.Beep(1500, 100)  # Higher pitch for the last beep
                self.start_timer()
            else:
                self.feedback_label.config(text=f"Starting in {self.countdown_value} seconds...")
                winsound.Beep(1000, 100)  # Regular beep sound
            self.countdown_value -= 1
            self.master.after(1000, self.start_countdown)
           
        
            


    def start_timer(self):
        self.timer_active = True
        self.start_time = time.time()
        self.update_timer()
        self.feedback_label.config(text="Workout started!")


    def update_timer(self):
        if self.timer_active:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            milliseconds = int((elapsed_time % 1) * 100)
            self.timer_label.config(text=f"{int(minutes):02}:{int(seconds):02}:{milliseconds:02}")
            self.master.after(50, self.update_timer)


    def start_pushup_counter(self):
        if self.pushup_thread is None or not self.pushup_thread.is_alive():
            self.pushup_counter_instance = PushupCounter()  # Store the instance
            self.pushup_thread = threading.Thread(target=self.pushup_counter_instance.run)
            self.pushup_thread.start()


    def run_pushup_counter(self):
        pushup_counter = PushupCounter()
        pushup_counter.run()


    def update_gui_image(self, cv_image):
        if cv_image is None or cv_image.size == 0:
            print("Received empty or None image in GUI.")
            return
        image_pil = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        image_tk = ImageTk.PhotoImage(image_pil)
        self.skeleton_image_label.configure(image=image_tk)
        self.skeleton_image_label.image = image_tk


# Create the main window and pass it to the GUI class
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()