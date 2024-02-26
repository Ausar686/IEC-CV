import json
import re
import os
import subprocess
import time
from typing import List

import requests

from utils.debug import (
    debug_gps_init,
    debug_gps_get_geolocation,
)
from utils.types import Session


class GPS(object):

    def __init__(self, session: Session):
        self.session = session
        self.api_key = self.session.gps_api_key
        self.url = "http://api.lbs.yandex.net/geolocation"
        self.networks = []
        debug_gps_init(self)
        return

    def get_location(self) -> None:
        """
        Get current device geolocation and store it into session.
        
        Don't forget to set 'SUDO_PASS' variable in /home/$USERNAME/.bashrc
        Example:
            export SUDO_PASS="1234"
        """
        iwlist_output = subprocess.check_output(
            f"echo \"{os.environ.get('SUDO_PASS')}\" | sudo -S iwlist scan",
            encoding="utf-8",
            shell=True
        )
        self.networks = self._parse_iwlist_output(iwlist_output)
        geolocation = self._request_geolocation()
        self.session.latitude.value = geolocation.get("latitude")
        self.session.longitude.value = geolocation.get("longitude")
        debug_gps_get_geolocation(self, geolocation)
        time.sleep(60)
        return

    def _request_geolocation(self) -> dict:
        """Request current geolocation based on networks"""
        # Connection is lost
        if not self.networks:
            return {"latitude": None, "longitude": None}
        strongest_network = max(self.networks, key=lambda x: x["signal_strength"])
        data = {
            "common": {
                "version": "1.0",
                "api_key": self.api_key
            },
            "wifi_networks": [strongest_network]
        }
        json_str = json.dumps(data)
        payload = {"json": json_str}
        response = requests.post(self.url, data=payload)
        try:
            geolocation = response.json()
        except Exception:
            geolocation = {}
        latitude = geolocation.get("position", {}).get("latitude", None)
        longitude = geolocation.get("position", {}).get("longitude", None)
        return {"latitude": latitude, "longitude": longitude}

    def _parse_iwlist_output(self, output: str) -> List[dict]:
        """Return WiFi networks obtained from iwlist command."""
        cell_re = re.compile(r'Cell \d+ - Address: (\S+)')
        signal_re = re.compile(r'Signal level=(-?\d+)')
        wifi_networks = []
        for line in output.split('\n'):
            cell_match = cell_re.search(line)
            signal_match = signal_re.search(line)
            if cell_match:
                # Get lowercase MAC-address
                mac_address = cell_match.group(1) 
            if signal_match:
                signal_strength = int(signal_match.group(1))
                wifi_network = {
                    "mac": mac_address,
                    "signal_strength": signal_strength
                }
                wifi_networks.append(wifi_network)
        return wifi_networks 

    def run(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)