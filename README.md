# StepperServoCANtester
Simple GUI program for testing StepperServoCAN motor

This program use Linux SocketCAN for interfacing with dzids StepperServoCAN board/motor. You have to bring up your CAN interface that is connected to StepperServoCAN board.
You can test the program with SocketCANs virtual interface (vcan). Start the program, if only one CAN interface is up the program will establish connection to that, but if several 
intrerfaces is found it will prompt a question to which interface to connect.

![image](https://user-images.githubusercontent.com/37126045/227358591-f02fb505-541d-4003-8dd9-05046cff7847.png)

You can insert the Steer Torque or Steer Angle values into gui and select the STEER_MODE. The injected values will updated with the "Update Torque/Angle value button or with pressing Return on keyboard.
When either TorqueControl is selected and Steer Torque value is given OR RelativeControl and Steer Angle is given, the StepperServoCAN motor should start spinning.

![image](https://user-images.githubusercontent.com/37126045/227360534-95258b39-5341-41d9-accd-8cfae35a3295.png)
