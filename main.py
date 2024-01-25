import json
import os

from session import Session
from utils import run_session, set_environment


if __name__ == "__main__":

    # Initialize paths
    config_path = "config.json"

    # Read config file
    with open(config_path, "r", encoding="utf-8") as config:
        kwargs = json.load(config)
    logs_dir = kwargs.pop("logs_dir", ".")
    out_video_dir = kwargs.pop("out_video_dir", ".")

    # Set environment variables
    set_environment(
        logs_dir=logs_dir,
        out_video_dir=out_video_dir,
    )

    # Initialize and run the session
    session = Session(**kwargs)
    run_session(session)