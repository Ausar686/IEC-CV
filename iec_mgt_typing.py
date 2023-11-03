class BaseType:
    def __getitem__(self, *args, **kwargs):
        pass

class Session(BaseType):
    pass

class StreamManager(BaseType):
    pass

class Detector(BaseType):
    pass

class VideoReader(BaseType):
    pass

class Logger(BaseType):
    pass

class Log(BaseType):
    pass

class GPSReceiver(BaseType):
    pass