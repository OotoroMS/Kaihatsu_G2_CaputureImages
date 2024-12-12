# 撮影、回転をして、学習用画像を保存するプログラム

import cv2
import serial
import struct
import time
from datetime import datetime

def capture_image(camera_index, filename):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Unable to open camera.")
        return False

    # 解像度を明示的に設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)  # 幅を2592pxに設定
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944) # 高さを1944pxに設定

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
    else:
        print("Error: Unable to capture image.")
        cap.release()
        return False

    cap.release()
    return True

def main():
    serial_params = {
        "port": "COM3",
        "baudrate": 9600,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "timeout": 0.08,
    }

    serial_comm = SerialCommunicator(**serial_params)

    max_steps = 200 # 200ステップで一周
    steps_by_once = 10 # 一回での回転数

    try:
        # Initialize camera index
        camera_index = 0

        serial_comm.serial_write(struct.pack(">B", 10)) # ソレノイド動作

        for step in range(max_steps // steps_by_once):
            print(f"Step {step+1}/{max_steps // steps_by_once}")

            # Signal PLC to fix the workpiece
            serial_comm.serial_write(struct.pack(">B", 210)) # ステッピングモーター回転数指示 (200+Step数)
            time.sleep(0.5)

            # Capture image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"./RawImages/{timestamp}.bmp"
            if capture_image(camera_index, filename):
                print(f"Image saved: {filename}")
            else:
                print("Failed to save image.")

        serial_comm.serial_write(struct.pack(">B", 11)) # ソレノイド解放
        print("Process completed.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        serial_comm.close()

if __name__ == "__main__":
    main()
