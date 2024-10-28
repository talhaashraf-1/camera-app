import logging
import tkinter as tk
from tkinter import messagebox
from camera import Camera
from database import Database
from logger import setup_logger

logger = setup_logger()


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='camera_app.log',
        filemode='w'
    )
    return logging.getLogger('CameraApp')



import sqlite3
from cryptography.fernet import Fernet


class Database:
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )
            ''')

    def add_user(self, username, password):
        encrypted_password = self.cipher.encrypt(password.encode())
        with self.conn:
            self.conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                              (username, encrypted_password))

    def verify_user(self, username, password):
        cursor = self.conn.execute('SELECT password FROM users WHERE username = ?',
                                   (username,))
        row = cursor.fetchone()
        if row:
            decrypted_password = self.cipher.decrypt(row[0]).decode()
            return decrypted_password == password
        return False

    def close(self):
        self.conn.close()
import cv2
from PIL import Image, ImageTk
import tkinter as tk


class Camera:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)

    def get_frame(self):
        ret, frame = self.vid.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def release(self):
        if self.vid.isOpened():
            self.vid.release()




class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Camera App")

        self.camera = Camera()
        self.database = Database()

        self.canvas = tk.Canvas(master, width=640, height=480)
        self.canvas.pack()

        self.btn_snapshot = tk.Button(master, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack()

        self.update()
        logger.info("Camera App started.")

    def update(self):
        frame = self.camera.get_frame()
        if frame is not None:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        else:
            logger.error("Failed to capture image from camera.")

        self.master.after(10, self.update)

    def snapshot(self):
        frame = self.camera.get_frame()
        if frame is not None:
            cv2.imwrite("snapshot.png", frame)
            logger.info("Snapshot taken and saved as snapshot.png")
            messagebox.showinfo("Info", "Snapshot saved as snapshot.png")
        else:
            logger.error("Failed to take snapshot.")

    def close(self):
        self.camera.release()
        self.database.close()
        logger.info("Camera released and database closed.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()