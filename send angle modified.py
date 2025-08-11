import serial
import time
import tkinter as tk
import threading

COM_port = 'COM3' # Identify and Modify the COM port from 'device manager' window

def send_angle_to_arduino(angle):
    try:
        with serial.Serial(COM_port, 9600, timeout=5) as ser:
            time.sleep(2)  # Allow Arduino to reset
            microsteps = int(angle * 6400 / 360)    # Modify the microsteps : using the 
            ser.write(f"{microsteps}\n".encode())

            # Wait for Arduino to send "DONE"
            start_time = time.time()
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode().strip()
                    if line == "DONE":
                        return True, f"Sent {microsteps} microsteps and rotation completed"
                if time.time() - start_time > 60:  # Timeout after 10 seconds
                    return False, "Timeout waiting for DONE from Arduino"
    except Exception as e:
        return False, f"Error: {e}"

def send_angle_thread(angle):
    status_label.config(text="Rotating...", fg="blue")
    result_label.config(text="")

    success, msg = send_angle_to_arduino(angle)

    result_label.config(text=msg)
    if success:
        status_label.config(text="Rotation Completed", fg="green")
    else:
        status_label.config(text="Rotation Failed", fg="red")

def on_send_button_click():
    try:
        angle = float(angle_entry.get())
        threading.Thread(target=send_angle_thread, args=(angle,), daemon=True).start()
    except ValueError:
        result_label.config(text="Please enter a valid number")
        status_label.config(text="Invalid Input", fg="red")

root = tk.Tk()
root.title("Send Angle to Arduino")

tk.Label(root, text="Enter angle (degrees):").pack(pady=5)

angle_entry = tk.Entry(root)
angle_entry.pack(pady=5)
angle_entry.focus_set()

send_button = tk.Button(root, text="Send Angle", command=on_send_button_click)
send_button.pack(pady=10)

result_label = tk.Label(root, text="")
result_label.pack(pady=5)

status_label = tk.Label(root, text="", font=('Helvetica', 12, 'bold'))
status_label.pack(pady=5)

root.mainloop()
