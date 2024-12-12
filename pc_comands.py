from typing import Optional
from queue import Queue
from plc_pc import SerialManager
from error import comand as error
from normal import comand as normal
from time import perf_counter

ERROR_OR_NORMAL = {
    b'\x01' : normal,
    b'\x02' : error
}

ELAPSED_TIME = 0.0

class PCManager:
    def __init__(self, serial):
        self.serial = serial
        # 外部に渡す用の変数
        self.text = None
    
    # 書き込み用
    def write_serial(self, data: bytes):
        self.serial.send(data)
    
    # 読み取り用
    def read_serial(self):
        result = self.serial.receive()
        return result
    
    # どちらの辞書を使用するか選択
    def compare_dict(self,data):                    
        category = data[:1]
        command_dict = ERROR_OR_NORMAL.get(category)
        return command_dict

    def get_cmd_msg(self, dict, data):
        text = dict.get(data[1:],"不明なコード")
        return text
    
    def read(self):
        text = ""
        data = self.read_serial()
        if data:
            dict = self.compare_dict(data)
            text = self.get_cmd_msg(dict,data)            
            self.text = text
        return text

    def get_msg(self):
        return self.text
    
    def test(self,data):
        dict = self.test_compare_dict(data)
        text = self.test_get_cmd_msg(dict, data)
        self.text = text
        return text
    
    def test_compare_dict(self,data):
        start_time = perf_counter()
        elapsed_time = ELAPSED_TIME
        dict = self.compare_dict(data)
        elapsed_time = perf_counter() - start_time
        print(f"dict compare:(Time: {elapsed_time:.9f} sec)")
        return dict

    def test_get_cmd_msg(self, dict, data):
        start_time = perf_counter()
        elapsed_time = ELAPSED_TIME
        text = self.get_cmd_msg(dict, data)
        elapsed_time = perf_counter() - start_time
        print(f"cmd_msg get:(Time: {elapsed_time:.9f} sec)")
        return text

if __name__ == '__main__':
    test = PCManager(None)
    data = b'\x01\x8e'
    text = test.test(data)
    print(test.get_msg())

            