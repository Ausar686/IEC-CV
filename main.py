import os

from session import Session
from utils import run_session, set_environment

if __name__ == "__main__":

    # Initialize paths
    video_dir = "/home/gleb/projects/iec_dev"
    weights = "/home/gleb/projects/IEC-CV/model.pt"
    logs_dir = "/home/gleb/projects/iec_dev/logs"
    out_video_dir = "/home/gleb/projects/iec_dev/output"
    stream1 = os.path.join(video_dir, "video/self/demo1.mp4")
    stream2 = os.path.join(video_dir, "video/self/demo2.mp4")
    stream3 = os.path.join(video_dir, "video/self/demo3.mp4")

    # INitialize session parameters
    bus_id = "081433"
    route_id = "304A"
    n_cameras = 3
    streams = [
        stream1,        
        stream2,        
        stream3,        
    ]

    # Set environment variables
    set_environment(
        logs_dir=logs_dir,
        out_video_dir=out_video_dir,
    )

    # Initialize and run the session
    session = Session(
        bus_id=bus_id,
        route_id=route_id, 
        n_cameras=n_cameras,
        streams=streams,
        weights=weights
    )
    run_session(session)