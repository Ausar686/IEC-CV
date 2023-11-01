import time

import can


def send_messages():
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    msg_opened = can.Message(arbitration_id=0x401, data=[0x01])
    msg_closed = can.Message(arbitration_id=0x401, data=[0x00])
    
    while True:
        print("Sending opened message...")
        bus.send(msg_opened)
        time.sleep(2)
        print("Sending closed message...")
        bus.send(msg_closed)
        time.sleep(2)

if __name__ == '__main__':
    send_messages()