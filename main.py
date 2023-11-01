from SessionClass import Session

session = Session(
	video_path='test2.mp4',
	model='model.pt',
	route_id="304A",
	bus_id="081433"
)
session.run()