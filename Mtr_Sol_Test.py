import serial.test
import pc_comands
import plc_pc
import serial_communicator
import serial
import struct

def main():
    serial_params1 = {
        "port": "COM3",# COMポートの指定 (str型)
        "baudrate": 9600,# ボーレートの指定(int型)
        "parity": serial.PARITY_NONE,   # パリティービットの指定(None)
        "stopbits": serial.STOPBITS_ONE,    # ストップビットの指定(1bit)
        "timeout": 0.08,                # タイムアウト時間の指定(float型)
    }

    serial_comm1 = serial_communicator.SerialCommunicator(**serial_params1)
    # serial_test = pc_comands.PCManager(serial_comm1)

    while True:
        inpt = input("Enter command: ")
        if inpt == "exit":
            break
        try:
            # 入力を数値に変換
            number = int(inpt)
            # 数値をバイト列に変換（整数型として送信）
            data = struct.pack(">B", number)
            serial_comm1.serial_write(data)
            data = serial_comm1.serial_read()
            if data[0]:
                print(data)
            else:
                print("No data received.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.") 
        
if __name__ == "__main__":
    main()