from datetime import datetime
import os
import sys
import time

import cv2

from debug_utils import (
    debug_writer_init,
    debug_writer_create,
    debug_write_empty,
    debug_write_frame,
    debug_fail_write_frame,
)
from iec_mgt_typing import StreamManager
from log import create_log


class VideoWriter:

    def __init__(self, manager: StreamManager):
        # Store a reference to StreamManager as an attribute
        self.manager = manager

        # Unpack parameters
        (_fourcc,fps, width, height) = self.manager.writer_tuple

        # Initialize extensions dictionary
        self._extensions = {
            "XVID": ".avi",
            "MJPG": ".avi",
            "MP4V": ".mp4",
            "X264": ".mp4"
        }

        # Set required attributes
        self.type = "writer"
        self._fourcc = _fourcc
        self.fourcc = cv2.VideoWriter_fourcc(*self._fourcc)
        self.fps = fps
        self.size = (width, height)
        self.out_path = None
        self.writer = None
        self._start_hour = None

        # Initialize cv2 objects for writing the video
        self.create()

        # Print debug info
        debug_writer_init(self)
        return


    def create(self) -> None:
        # Get new video path
        self.out_path = self._make_out_path()

        # Initialize new writer
        self.writer = cv2.VideoWriter(
            self.out_path,
            self.fourcc,
            self.fps,
            self.size,
        )

        # Print debug info
        debug_writer_create(self)
        return
    

    def _make_out_path(self) -> str:
        """
        Generates output path, based on current datetime and PATH variable.
        We use current date and current hour for filename.
        We also current hour for further validity check.
        (Check out 'write' method for details)
        """
        # Get current timestamp and save current hour
        now = datetime.now()
        self._start_hour = now.time().hour
        filename = f"video_{now.date()}_hour{self._start_hour}_cam{self.manager.camera}{self.ext}"

        # The 'out_video_dir' environment variable contains
        # the abspath to directory with output videos.
        directory = os.environ.get("out_video_dir", "/tmp")
        out_path = os.path.join(directory, filename)
        return out_path


    def write(self) -> None:
        """
        Writes a frame into specified output path and checks,
        whether current output path is still valid
        """
        try:
            self.write_frame()
            if not self._is_valid():
                self.restart()
            return
        except:
            self.release()
            raise


    def write_frame(self) -> None:
        """
        Gets frame from the storage and writes it into a file.
        """
        if self.manager.write_storage.empty():
            # debug_write_empty(self)
            time.sleep(0.01)
            return

        # Get next frame
        frame = self.manager.write_storage.get()

        # Write the frame
        try:
            self.writer.write(frame)
            debug_write_frame(self)
        except Exception as e:
            debug_fail_write_frame(self, e)
            log = create_log(self.manager, "writer_write_error", e)
            try:
                self.manager.logs_storage.put(log)
            except Exception:
                pass
        return


    def _is_valid(self) -> bool:
        """
        Checks, whether the output path is valid.
        Basically, output path is set for 1 hour.
        So, we want to generate a new output path each hour,
        in order to limit the size of a single output video. 
        """
        return self._start_hour == datetime.now().time().hour


    def restart(self) -> None:
        """
        This method releases the resources of previous writer 
        and creates a new one
        """
        self.release()
        self.create()
        return


    def release(self) -> None:
        """
        Releases the cv2.VideoWriter resources
        """
        if self.writer is None:
            return
        self.writer.release()
        return


    @property
    def start_hour(self) -> int:
        return self._start_hour


    @property
    def ext(self) -> str:
        return self._extensions.get(self._fourcc, ".avi")


    def run(self) -> None:
        return self.write()


    def __call__(self) -> None:
        return self.write()