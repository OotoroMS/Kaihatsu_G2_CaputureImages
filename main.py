import cv2
import serial
import serial_communicator
import struct
import time
from datetime import datetime

def log_time(start_time, description):
    elapsed_time = time.time() - start_time
    print(f"{description} completed in {elapsed_time:.2f} seconds.")

def capture_image(cap, filename):
    start_time = time.time()
    print("Starting image capture...")

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
    else:
        print("Error: Unable to capture image.")
        return False

    log_time(start_time, "Image capture")
    return True

def main():
    serial_params = {
        "port": "COM3",
        "baudrate": 9600,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "timeout": 0.08,
    }

    serial_comm = serial_communicator.SerialCommunicator(**serial_params)

    max_steps = 200 # 200ステップで一周
    steps_by_once = 10 # 一回での回転数

    try:
        # Initialize camera index
        camera_index = 0
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return

        # 解像度を明示的に設定
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)  # 幅を2592pxに設定
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944) # 高さを1944pxに設定

        serial_comm.serial_write(struct.pack(">B", 10)) # ソレノイド動作

        for step in range(max_steps // steps_by_once):
            print(f"Step {step+1}/{max_steps // steps_by_once}")

            # Signal PLC to fix the workpiece
            start_time = time.time()
            print("Sending PLC signal to fix workpiece...")
            serial_comm.serial_write(struct.pack(">B", 210)) # ステッピングモーター回転数指示 (200+Step数)
            time.sleep(0.5)
            log_time(start_time, "PLC workpiece fixing signal")

            # Capture image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"./RawImages/{timestamp}.bmp"
            if capture_image(cap, filename):
                print(f"Image saved: {filename}")
            else:
                print("Failed to save image.")

        start_time = time.time()
        print("Releasing solenoid...")
        serial_comm.serial_write(struct.pack(">B", 11)) # ソレノイド解放
        log_time(start_time, "Solenoid release")

        print("Process completed.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cap.release()
        serial_comm.close()

if __name__ == "__main__":
    main()
