from typing import Tuple
from datetime import datetime
import json
import hashlib

from iec_mgt_typing import Session


class Logger:

	def __init__(self, session: Session=None):
		self.session = session
		self.set_session_params()
		self.start_date = datetime(1970, 1, 1)
		return

	def set_session_params(self) -> None:
		if self.session is not None:
			self.log_path = self.session.event_log_path
			self.route_id = self.session.route_id
			self.bus_id = self.session.bus_id
			self.session_id = self.session.session_id
		else:
			self.log_path = self.create_log_path()
			self.route_id = None
			self.bus_id = None
			self.session_id = None
		return

	@staticmethod
	def create_log_path() -> str:
		now = datetime.now()
		curtime = (now - self.start_date).total_seconds()
		hashed_curtime = hashlib.sha256(str.encode(str(curtime))).hexdigest()
		date_str = str(now.date())
		log_path = f"log_{date_str}_NO_SESSION_{hashed_curtime}.json"
		return log_path

	@staticmethod
	def prepare_data(
		timestamp: float,
		date: str,
		time: str,
		camera: int,
		route_id: str,
		bus_id: str,
		session_id: str,
		event: str,
		geolocation: Tuple[float, float]
	) -> dict:
		latitude, longitude = geolocation
		data = {
			"timestamp": timestamp,
			"date": date,
			"time": time,
			"camera": camera,
			"route_id": route_id, 
			"bus_id": bus_id,
			"session_id": session_id,
			"event": event,
			"geolocation": {
				"latitude": latitude,
				"longitude": longitude,
			}
		}
		return data

	def log(
		self,
		camera: int,
		event: str,
		geolocation: Tuple[float, float]=None
	) -> None:
		now = datetime.now()
		timestamp = (now - self.start_date).total_seconds()
		date = str(now.date())
		time = str(now.time())
		if geolocation is None:
			geolocation = (None, None)
		data = self.prepare_data(
			timestamp,
			date, 
			time, 
			camera, 
			self.route_id, 
			self.bus_id, 
			self.session_id, 
			event, 
			geolocation
		)
		with open(self.log_path, "a", encoding="utf-8") as log_file:
			if log_file.tell():
				data_str = ",\n" + json.dumps(data, indent=4)
			else:
				data_str = json.dumps(data, indent=4)
			log_file.write(data_str)
		return