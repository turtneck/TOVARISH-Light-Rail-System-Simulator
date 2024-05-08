import time
import serial



global board
board = serial.Serial('COM7',9600, timeout = 2)
def ser_read():
    data = board.readline()
    return data.decode()
def ser_send(inp):
    board.write(inp.encode())
    

if __name__ == "__main__":
    try:
        while True:
            print(ser_read())
    except:
        print("NOT DETECTED")