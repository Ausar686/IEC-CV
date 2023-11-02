from session import Session
from utils import run_session

if __name__ == "__main__":
	# Initialize session parameters
	weights = "model.pt"
	bus_id = "081433"
	route_id = "304A"
	n_cameras = 3
	streams = [
		"test1.mp4",
		"test2.mp4",
		"test3.mp4"
	]

	# Initialize and run the session
	session = Session(
		bus_id=bus_id,
		route_id=route_id, 
		n_cameras=n_cameras,
		streams=streams,
		weights=weights
	)
	run_session(session)