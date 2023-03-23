#!/usr/bin/python3

"""
This is simple gui program that can be used to test StepperServoCAN motor.
https://github.com/dzid26/StepperServo-hardware
https://github.com/dzid26/StepperServoCAN

"""

import os
import sys
import subprocess

import time
import threading

import tkinter as tk
from tkinter import messagebox
import cantools
import can

# This function checks if the operating system is Linux. If not, it prints an error message and aborts the program.
def check_linux():
    """
    Check if the operating system is Linux. If not, print an error message and abort the program.

    Raises:
        SystemExit: If the operating system is not Linux.

    """
    if sys.platform != "linux":
        print("Error: Operating system is not Linux. Aborting program.")
        sys.exit(1)

def msg_calc_checksum_8bit(data: bytes, len: int, msg_id: int) -> int:
    """
    This function calculates 8-bit checksum for given data, length and message id.
    """
    checksum = msg_id
    for i in range(len):
        checksum += data[i]
    checksum = (checksum & 0xFF) + (checksum >> 8)
    checksum &= 0xFF

    return checksum

# Function to search for available CAN interfaces and connect to one.
def connect_to_can_interface():
    """
    This function searches for available CAN interfaces, prompts the user to select one if there are multiple available.
    It then connects to the selected CAN interface using the python-can library and returns a can_bus object.
    """
    # Check for available CAN interfaces
    interfaces = []
    output = subprocess.check_output("ip -details -brief link | grep can", shell=True)
    for line in output.decode().split("\n"):
        if line.strip():
            words = line.split()
            if words[1] == "UP" or words[1] == "UNKNOWN":  # Check if interface is up
                interface = words[0]
                interfaces.append(interface)
    # If multiple CAN interfaces are found, list them and ask in terminal which interface to choose
    if len(interfaces) > 1:
        print("Multiple CAN interfaces found:")
        for i, interface in enumerate(interfaces):
            print(f"{i+1}: {interface}")
        print(f"{len(interfaces)+1}: Abort the program")
        selection = input("Select an interface number: ")
        try:
            selection = int(selection)
            if selection < 1 or selection > len(interfaces)+1:
                raise ValueError
            elif selection == len(interfaces)+1:
                print("Aborting program...")
                sys.exit(1)
        except ValueError:
            print("Invalid selection")
            sys.exit(1)
        interface = interfaces[selection-1]
    # If only 1 interface found, just choose that
    elif len(interfaces) == 1:
        interface = interfaces[0]
    # If no interfaces found abort the program
    else:
        print("No CAN interfaces found that are UP, will abort the program.")
        print("Hint: if you want to test the program set up virtual CAN interface with these commands.")
        print("sudo modprobe vcan")
        print("sudo ip link add dev vcan0 type vcan")
        print("sudo ip link set up vcan0")
        sys.exit(1)

    # Connect to selected CAN interface
    print(f"Connected to CAN interface {interface}")
    can_bus = can.interface.Bus(interface, bustype='socketcan')
    
    return can_bus

# Test if this is run on Linux, otherwise the program will not work
check_linux()

# Search for CAN interface and connect to it
can_bus = connect_to_can_interface()

# Flag to control the CAN traffic
can_enabled = True

counter = 0

# Load the .dbc file
#db = cantools.database.load_file('/home/goran/Downloads/BMW_E39_OP.dbc')
db = cantools.database.load_file('./ocelot_controls.dbc')

msg = db.get_message_by_name('STEERING_COMMAND')

data = msg.encode({
    'STEER_TORQUE': 0,
    'STEER_ANGLE': 0,
    'STEER_MODE': 0,
    'COUNTER': 0,
    'CHECKSUM': 0
})

# Define global variables for torque and angle
torque = 0
angle = 0

# Function to update torque and angle from widget values
def update_values():
    global torque, angle

    torque_str = torque_widget.get()
    if torque_str.lstrip('-').isdigit():
        check_torque = int(torque_str)      # check_torque is used for intermediate value so if the update_message() -thread is checking torque value, it won't be out of .dbc bound
        # print(check_torque)
        if check_torque < -16 or check_torque > 16:
            messagebox.showerror("Error", "Torque value should be between -16 and 16")
        else:
            torque = check_torque
    else:
        torque = 0

    angle_str = angle_widget.get()
    if angle_str.lstrip('-').isdigit():
        check_angle = int(angle_str)        # check_angle is used for intermediate value so if the update_message() -thread is checking angle value, it won't be out of .dbc bound
        print(angle)
        if check_angle < -4096 or check_angle > 4096:
            messagebox.showerror("Error", "Torque value should be between -16 and 16")
        else:
            angle = check_angle
    else:
        angle = 0


# Function to encode and send the CAN message
def update_message():
    global msg, data, counter, torque, angle

    msg = db.get_message_by_name('STEERING_COMMAND')

    counter = counter + 1
    if counter == 16:
        counter = 0

    data = msg.encode({
        'STEER_TORQUE': torque,
        'STEER_ANGLE': angle,
        'STEER_MODE': steer_mode_widget.get_value(),
        'COUNTER': counter & 0xF,
        'CHECKSUM': 0
    })

    lent = len(data)
    checksum = msg_calc_checksum_8bit(data, lent, 558)

    data = msg.encode({
        'STEER_TORQUE': torque,
        'STEER_ANGLE': angle,
        'STEER_MODE': steer_mode_widget.get_value(),
        'COUNTER': counter & 0xF,
        'CHECKSUM': checksum
    })

def send_message():
    
    global can_enabled

    #can_bus = can.interface.Bus('vcan0', bustype='socketcan')
    while can_enabled:
        # Create a message using the "torque" dbc object
        message = can.Message(arbitration_id=msg.frame_id, data=data, is_extended_id=False)
 
        update_message()
        can_bus.send(message)

        # Sleep for 10ms
        time.sleep(0.01)

class SteerModeWidget:
    def __init__(self, master, label_text, options):
        self.var = tk.IntVar()
        self.label = tk.Label(master, text=label_text)
        self.label.grid(row=2, column=0, sticky="w")  # set sticky to "w" for left alignment
        self.buttons = []
        for idx, option in enumerate(options):
            button = tk.Radiobutton(
                master, text=option[1], variable=self.var, value=option[0]
            )
            button.grid(row=2+idx, column=1, sticky="w")
            self.buttons.append(button)

    def get_value(self):
        return self.var.get()


# Create the GUI window
window = tk.Tk()

# set the title of the window
window.title("StepperServoCAN Tester")

# Set window width and height to custom values
window.geometry("360x210")  # Set window width to 400 pixels and height to 300 pixels

# Add a button to send the message
send_button = tk.Button(window, text='Update Torque/Angle value', command=update_values)

# Create labels for the widgets
torque_label = tk.Label(window, text="Steer Torque:       ")
angle_label = tk.Label(window, text="Steer Angle:       ")
counter_pedal_label = tk.Label(window, text="Counter:")
checksum_pedal_label = tk.Label(window, text="Checksum:")

# Add a widget for each piece of data in the message
torque_widget = tk.Entry(window)
angle_widget = tk.Entry(window)

# Place the labels and widgets using grid
torque_label.grid(row=0, column=0, sticky="w")  # set sticky to "w" for left alignment
torque_widget.grid(row=0, column=1, sticky="w")
angle_label.grid(row=1, column=0, sticky="w")  # set sticky to "w" for left alignment
angle_widget.grid(row=1, column=1, sticky="w")

# Add SteerModeWidget for the Steer Mode option
STEER_MODE_OPTIONS = [
    (0, "Off - instant 0 torque"),
    (1, "TorqueControl"),
    (2, "RelativeControl"),
    (3, "SoftOff - ramp torque to 0 in 1s")
]
steer_mode_widget = SteerModeWidget(window, "Steer Mode:  ", STEER_MODE_OPTIONS)

send_button.grid(row=7, column=0, columnspan=2)

def on_closing():
    global can_enabled
    can_enabled = False
    window.destroy()

# Add the quit button
quit_button = tk.Button(window, text="Quit", command=on_closing)
quit_button.grid(row=10, column=0, columnspan=2, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)

window.bind('<Escape>', lambda event: on_closing())
window.bind('<Return>', lambda event: update_values())

# Start the send_can_message function in a separate thread
thread = threading.Thread(target=send_message)
thread.start()

# Run the GUI loop
window.mainloop()
