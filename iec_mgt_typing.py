class BaseType:
    def __getitem__(self, *args, **kwargs):
        pass

class Session(BaseType):
    pass

class StreamManager(BaseType):
    pass

class VideoReader(BaseType):
    pass

class Preprocessor(BaseType):
    pass

class Detector(BaseType):
    pass

class Tracker(BaseType):
    pass

class Logger(BaseType):
    pass

class Log(BaseType):
    pass

class GPS(BaseType):
    pass

class Writer(BaseType):
    pass