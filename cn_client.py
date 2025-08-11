import socket
import json
import random
import time

# Simulate sensor data
def get_sensor_data():
    return {
        'patient_id': random.randint(1, 10),
        'heart_rate': random.randint(60, 120),
        'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
        'temperature': round(random.uniform(36.5, 39.5), 1)
    }

# Function to handle connection and data transmission
def send_data_to_server():
    while True:
        try:
            # Connect to the server
            print("Attempting to connect to the server...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            print("Connected to the server!")
            
            while True:
                data = get_sensor_data()
                print(f"Sending data: {data}")
                client_socket.sendall(json.dumps(data).encode())
                time.sleep(2)  # Send every 2 seconds
        
        except (ConnectionRefusedError, BrokenPipeError):
            print("Connection to server lost. Retrying in 5 seconds...")
            time.sleep(5)  # Retry connection after 5 seconds
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
        finally:
            try:
                client_socket.close()
            except Exception:
                pass

# Start the client
send_data_to_server()
