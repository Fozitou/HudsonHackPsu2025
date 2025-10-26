import serial
import time
import tkinter as tk
from tkinter import messagebox

import time



#setup serial

try:
    arduino = serial.Serial(port='COM10', baudrate=9600, timeout=1) #my arduino com port; change as needed
    time.sleep(2)  #reset time
except serial.SerialException:
    arduino = None
    print("failed to connect to arduino.")

#GUI setup
def send_command(direction,speed=0,angle=0,center_cam=0,turns=0):
    if arduino and arduino.is_open:
        data = f"{direction},{speed},{angle},{center_cam},{turns}\n"
        arduino.write(data.encode())
    else:
        messagebox.showerror("Error", "Arduino not connected")


speed_var = 100


#button functions
def forward():
    try:
        interval = 3
        

        send_command("F", speed_var,0,0,0)
        

        time.sleep(interval)
        

        stop()
    
        return {"name": "forward", "status": 200, "speed_sent": speed_var, "interval": interval}
    except Exception as e:
        print(f"[App] Error in forward(): {e}")
        return {
            "name": "forward",
            "status": 500,
            "error": str(e)
        }


def stop():
    send_command("S",speed_var,0,0,0)
    return {"name": "stop", "status":200}
def right_forward():
    try:
        interval = 3
    

        send_command("R",speed_var,0,0,0)
        time.sleep(interval)
        

        stop()
        return {"name": "forward", "status":200}
    except Exception as e:
        print(f"[App] Error in forward(): {e}")
        return {
            "name": "right_forward",
            "status": 500,
            "error": str(e)
        }

def left_forward():
    try: 
        interval = 3
        
        send_command("L",speed_var,0,0,0)
        time.sleep(interval)
        stop()
        return {"name": "left_forward", "status":200}
    except Exception as e:
        print(f"[App] Error in forward(): {e}")
        return {
            "name": "left_forward",
            "status": 500,
            "error": str(e)
        }
def grab():
    try:
        angle = 180
        send_command("A",0,angle,0,0)
        return {"name": "grab", "status": 200}
    except Exception as e:
        print(f"[App] Error in grab(): {e}")
        return {
            "name": "grab",
            "status": 500,
            "error": str(e) }

def release():
    try:
        angle = 55
        send_command("A",0,angle,0,0)
        return {"name": "release", "status": 200}
    except Exception as e:
        print(f"[App] Error in release(): {e}")
        return {
            "name": "grab",
            "status": 500,
            "error": str(e) }

def center_cam():
    try:
        angle = 90
        print("sending center cam signal")
        send_command("Z",0,0,angle,0)
        print("ending center cam signal")
        return {"name": "center_cam", "status":200}
    except Exception as e:
        print(f"[App] Error in center_cam(): {e}")
        return {
            "name": "center_cam",
            "status": 500,
            "error": str(e) }

def left_cam():
    try:
        angle = 180
        print("sending left cam signal")
        send_command("Z",0,0,angle)
        print("ending left cam signal")
        return {"name": "left_cam", "status":200}
    except Exception as e:
        print(f"[App] Error in left_cam(): {e}")
        return {
            "name": "left_cam",
            "status": 500,
            "error": str(e) }

def right_cam():
    try:
        angle = 0
        print("sending right cam signal")
        send_command("Z",0,0,angle)
        print("enindg right cam signal")
        return {"name": "right_cam", "status":200}
    except Exception as e:
        print(f"[App] Error in right_cam(): {e}")
        return {
            "name": "right_cam",
            "status": 500,
            "error": str(e) }

def SpinRIGHT(turns):
    try:
        send_command("V",0,0,0,turns)
        return {"name": "SpinRIGHT", "status":200, "turns": turns}
    
    except Exception as e:
        print(f"[App] Error in SpinRIGHT(): {e}")
        return {
            "name": "SpinRIGHT",
            "status": 500,
            "error": str(e) }


def SpinLEFT(turns):
    try:
        
        send_command("U",0,0,0,turns)
        return {"name": "SpinLEFT", "status":200,"turns": turns}
    
    except Exception as e:
        print(f"[App] Error in SpinLEFT(): {e}")
        return {
            "name": "SpinLEFT",
            "status": 500,
            "error": str(e) }
    



def avante():
    try:
        interval = 0.5
        

        send_command("F", speed_var,0,0,0)
        

        time.sleep(interval)
        

        stop()
    
        return {"name": "forward", "status": 200, "speed_sent": speed_var, "interval": interval}
    except Exception as e:
        print(f"[App] Error in forward(): {e}")
        return {
            "name": "forward",
            "status": 500,
            "error": str(e)
        }