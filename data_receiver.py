import can

class DoorReceiver:
    def __init__(self, channel='vcan0', bustype='socketcan'):
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)

    def listen(self):
        message = self.bus.recv()
        if message and message.arbitration_id == 0x401:
            if message.data[0] == 0x01:
                return "Opened"
            elif message.data[0] == 0x00:
                return "Closed"
        return None


if __name__ == '__main__':
    # Instantiate the DoorReceiver
    receiver = DoorReceiver()

    try:
        cnt = 0
        while True:
            cnt += 1
            # Listen for a message and get the door state
            current_state = receiver.listen()
            if current_state:
                print(f"Door is {current_state}")
            else:
                print(f"No signal. Counter: {cnt}")
    except KeyboardInterrupt:
        print("Stopping...")