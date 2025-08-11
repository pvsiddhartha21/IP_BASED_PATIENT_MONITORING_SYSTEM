import socket
import threading
import json
import sqlite3
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox
from collections import deque

# Database setup
conn = sqlite3.connect('patient_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS vitals
                  (patient_id INT, heart_rate INT, blood_pressure TEXT, temperature REAL, timestamp TEXT)''')

def save_to_db(data):
    cursor.execute("INSERT INTO vitals VALUES (?, ?, ?, ?, ?)",
                   (data['patient_id'], data['heart_rate'], data['blood_pressure'], data['temperature'], datetime.now()))
    conn.commit()

# Tkinter GUI setup
root = tk.Tk()
root.title("Patient Monitoring System")
root.geometry("600x600")
hr_label = tk.Label(root, text="Heart Rate: N/A", font=("Helvetica", 16))
hr_label.pack()
temp_label = tk.Label(root, text="Temperature: N/A", font=("Helvetica", 16))
temp_label.pack()

# Alert handling
def check_vital_signs(data):
    if data['heart_rate'] > 100 or data['temperature'] > 38.0:
        messagebox.showwarning("Alert", f"Critical alert for patient {data['patient_id']}!")

# Data storage for live graph
heart_rate_data = deque(maxlen=50)
temperature_data = deque(maxlen=50)

# Matplotlib real-time graph setup
plt.style.use('dark_background')
fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
fig.suptitle("Real-Time Patient Monitoring", fontsize=16)

line_hr, = ax[0].plot([], [], color='lime', lw=2, label="Heart Rate (bpm)")
ax[0].set_ylim(50, 150)
ax[0].set_ylabel("Heart Rate (bpm)")
ax[0].legend(loc="upper right")
ax[0].grid(color="gray", linestyle="--", linewidth=0.5)

line_temp, = ax[1].plot([], [], color='cyan', lw=2, label="Temperature (°C)")
ax[1].set_ylim(35, 40)
ax[1].set_ylabel("Temperature (°C)")
ax[1].set_xlabel("Time")
ax[1].legend(loc="upper right")
ax[1].grid(color="gray", linestyle="--", linewidth=0.5)

# Update the graph dynamically
def update_graph(frame):
    line_hr.set_data(range(len(heart_rate_data)), heart_rate_data)
    line_temp.set_data(range(len(temperature_data)), temperature_data)
    ax[0].set_xlim(0, len(heart_rate_data))
    ax[1].set_xlim(0, len(temperature_data))
    return line_hr, line_temp

ani = FuncAnimation(fig, update_graph, interval=500)

# Handle client connections
def handle_client(client_socket):
    print("Handling new client connection...")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("Client disconnected.")
                break
            data = json.loads(data.decode())
            print(f"Received data: {data}")
            save_to_db(data)

            # Update GUI labels
            hr_label.config(text=f"Heart Rate: {data['heart_rate']} bpm")
            temp_label.config(text=f"Temperature: {data['temperature']} °C")

            # Append data to graph queues
            heart_rate_data.append(data['heart_rate'])
            temperature_data.append(data['temperature'])

            # Trigger alerts if needed
            check_vital_signs(data)

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()
        print("Client connection closed.")

# Secure Socket setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)
print("Server started and listening on port 12345")

# Accept multiple clients with threading
def accept_connections():
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection accepted from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Start server and GUI
threading.Thread(target=accept_connections).start()
plt.show(block=False)
root.mainloop()
