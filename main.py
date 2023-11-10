import multiprocessing as mp
import sys

from session import Session
from utils import run_session

if __name__ == "__main__":

    # Initialize session parameters
    weights = "model.pt"
    bus_id = "081433"
    route_id = "304A"
    n_cameras = 3
    streams = [
        "video/self/demo1.mp4",
        "video/self/demo2.mp4",
        "video/self/demo3.mp4"
    ]
    logs_dir = "/home/gleb/projects/iec_dev/logs"
    sys.path.append(logs_dir)
    sys.path = [sys.path[-1], *sys.path[:-1]]

    # Initialize and run the session
    session = Session(
        bus_id=bus_id,
        route_id=route_id, 
        n_cameras=n_cameras,
        streams=streams,
        weights=weights
    )
    run_session(session)