# StepperServoCANtester
This is a simple GUI program that can be used to test the StepperServoCAN motor. It is based on the [StepperServo-hardware](https://github.com/dzid26/StepperServo-hardware) and [StepperServoCAN](https://github.com/dzid26/StepperServoCAN) projects.

![20230322_102941](https://user-images.githubusercontent.com/37126045/227361324-ecf9a5af-96b3-4739-9827-1915c412b687.jpg)

## Requirements
- Python 3
- tkinter
- cantools
- python-can

## Installation

1. Clone the repository:

  `git clone https://github.com/killinen/StepperServoCANtester.git`
  
  `cd StepperServoCANtester`

2. Install the required libraries:
  
  `pip install tkinter cantools python-can`

3. Connect the StepperServoCAN motor to the computer via CAN interface.

## Usage

4. Run the program: 

  `python3 StepperServoCAN_GUI.py`

5. The program will automatically detect and display a list of available CAN interfaces to the user. In case multiple interfaces are available, the user will be prompted to select one.
6. Upon connecting to the selected CAN interface, the program will present a user-friendly GUI with two input fields for setting the torque and angle values of the motor.
7. The user can update the injected values to the motor by clicking the "Update Torque/Angle Value" button or by pressing the "Return" key on the keyboard.
8. Once the user selects either "TorqueControl" and provides a "Steer Torque" value, or selects "RelativeControl" and provides a "Steer Angle" value, the StepperServoCAN motor will start spinning.
9. To exit the program, the user can click the "Exit" button, press the "ESC" key, or simply close the window.

![image](https://user-images.githubusercontent.com/37126045/227358591-f02fb505-541d-4003-8dd9-05046cff7847.png)

![image](https://user-images.githubusercontent.com/37126045/227360534-95258b39-5341-41d9-accd-8cfae35a3295.png)

## Notes

- The torque value should be between -16 and 16, and the angle value should be between -4096 and 4096.
- If no CAN interfaces are found, the program will abort. To test the program, you can set up a virtual CAN interface with the following commands:

  `sudo modprobe vcan`
  
  `sudo ip link add dev vcan0 type vcan`
  
  `sudo ip link set up vcan0`
  
- You can check for available CAN interfaces that are UP in Linux with following command:

  `ip -details -brief link | grep can | grep -i 'state up\|state unknown'`
