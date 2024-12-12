from serial_communicator import SerialCommunicator
from typing import Optional

FARST = 2
LAST = 3

SHUTDOWN_STATUS = {
    "startup": True,
    "shutdown": False
}

RESPONSE_STATUS = {
    "not_waiting": True,
    "waiting": False
}

DATA_PREFIX = {
    "ack": b'\x02',
    "data_in": b'\x01'
}

LINE_ENDING = b'\n'

class SerialManager:
    def __init__(self, serial_params: dict):
        self.send_data = b''
        self.serial_comm = SerialCommunicator(**serial_params)
        self.shutdown_flag: bool = SHUTDOWN_STATUS["startup"]
        self.wait_for_response: bool = RESPONSE_STATUS["not_waiting"]

    def serial_receive(self) -> tuple[bytes, bool]:
        if self.shutdown_flag:
            try:
                rcv_data = self.serial_comm.log_serial_read()
                return rcv_data
            except Exception as e:
                print(f"Manager Recive unexpected error: {e}")
    
    def serial_send(self, data: bytes):
        if self.shutdown_flag:
            try:
                self.serial_comm.log_serial_write(data)                
            except Exception as e:
                print(f"Manager Send unexpected error: {e}")
    
    def format_bytes(self, data: bytes, prefix: bytes=DATA_PREFIX["data_in"]):
        converted_data = prefix + data + LINE_ENDING
        return converted_data
    
    def serial_response(self, data: bytes):
        if self.shutdown_flag:
            try:
                self.serial_comm.log_serial_write(data)
            except Exception as e:
                print(f"Response unexpected error: {e}")
    
    def compare_receive(self, data: bytes):
        prefix_request = DATA_PREFIX["data_in"]
        prefix_response = DATA_PREFIX["ack"]

        if data.startswith(prefix_request):
            print("PLCからの送信データだよ")
            # 応答を返すよ
            self.response(data[2:3], prefix_response)
            # エラー関連かのデータも渡すこと
            return data[1:3]
            
        elif data.startswith(prefix_response):
            print("PLCからの応答データだよ")
            # 応答待ちフラグを解除
            self.wait_for_response = RESPONSE_STATUS["not_waiting"]
            # 合っているか判別するよ
            self.compare(data[2:3])
            return b''

        else:
            print("よくわからないデータだよ")
            # 応答待ちフラグは解除するよ
            self.wait_for_response = RESPONSE_STATUS["not_waiting"]
            return b''
        
    def response(self, data: bytes, prefix: bytes):
        # データの成形
        response_data = self.format_bytes(data,prefix)
        # データの送信(1回)
        self.serial_response(response_data)

    def compare(self, data: bytes):
        if data == self.send_data[1:2]:
            print("OK。送信データと応答データが一致したよ")
        else:
            print("NG。送信データと応答データが不一致だったよ")
            # 再送させるよ
            self.send(data)

    def send(self, data: bytes):
        if self.wait_for_response:
            # データの成形
            request_data = self.format_bytes(data)
            # 判定用に保存
            self.send_data = request_data
            # データの送信(1回？)
            self.serial_send(request_data)
            self.wait_for_response = RESPONSE_STATUS["waiting"]

    def receive(self):
        result = b''
        # データの受信
        rcv_data = self.serial_receive()
        if rcv_data[0]:
            # 受信データの判別
            result = self.compare_receive(rcv_data[0])
        return result

    def serial_close(self):
        self.shutdown_flag = SHUTDOWN_STATUS["shutdown"]
        self.serial_comm.serial_close()