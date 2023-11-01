from video_reader import VideoReader


urls = [
    "rtsp://admin:2023IEC2023@192.168.1.64",
    "rtsp://admin:2023IEC2023@192.168.1.65",
    "rtsp://admin:2023IEC2023@192.168.1.66"
]
reader = VideoReader(urls=['test3.mp4'])
while True:
    reader.run()
    reader.display()
    if reader.exit_flag:
        break
reader.close()