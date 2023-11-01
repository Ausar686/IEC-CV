from session import Session


# Initialize session parameters
weights = "model.pt"
bus_id = "081433"
route_id = "304A"
n_cameras = 2

# Initialize and run the session
session = Session(
	weights=weights,
	bus_id=bus_id,
	route_id=route_id, 
	n_cameras=n_cameras)
session.run()