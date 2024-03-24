import json
import os
import re
import subprocess
import time

import gpsd
import requests

from utils.debug import (
    debug_gps_fail_get_location,
    debug_gps_get_geolocation,
    debug_gps_init,
)
from utils.types import Session


class GPS:

    def __init__(self, session: Session, socket: str='/etc/default/gpsd'):
        # Store reference to session as an attribute
        self.session = session
        # Set Yandex API attributes
        self.api_key = self.session.gps_api_key
        self.url = "http://api.lbs.yandex.net/geolocation"
        self.networks = []
        self.yandex_location = self._get_location_template()
        self.yandex_timestamp = 0
        self.yandex_cooldown = 60
        # Set attributes for local GPS receiver
        self.socket = socket
        self.packet = None
        # Set request cooldown
        self.cooldown = 1
        # Set max number of retries for local GPS receiver
        self.max_retries = 10000
        # Connect to GPS
        os.environ["GPSD_SOCKET"] = self.socket
        self._gpsd_connected = False
        self._connect()
        debug_gps_init(self)
        return

    def get_location(self) -> None:
        location = self._get_location_gps()
        if self._is_invalid(location):
            try:
                location = self._get_location_yandex()
            except Exception:
                location = self._get_location_template()
        if not self._is_invalid(location):
            self._set_location(location)
        debug_gps_get_geolocation(self, location)
        time.sleep(self.cooldown)
        return

    def _set_location(self, location: dict) -> None:
        """Set geolocation to session and update timestamp."""
        self.session.latitude.value = location.get("latitude")
        self.session.longitude.value = location.get("longitude")
        self.session.timestamp.value = time.time()
        return

    def _get_location_yandex(self) -> dict:
        """Get current device geolocation store it into session."""
        if time.time() < self.yandex_timestamp:
            return self.yandex_location
        nmcli_output = self._get_nmcli_output()
        self.networks = self._parse_nmcli_output(nmcli_output)
        self.yandex_timestamp = time.time() + self.yandex_cooldown
        self.yandex_location = self._request_geolocation()
        return self.yandex_location

    def _request_geolocation(self) -> dict:
        """Request current geolocation based on networks"""
        location = self._get_location_template()
        # Connection is lost
        if not self.networks:
            return location
        strongest_network = max(
            self.networks,
            key=lambda x: x["signal_strength"]
        )
        data = {
            "common": {
                "version": "1.0",
                "api_key": self.api_key
            },
            "wifi_networks": [strongest_network]
        }
        json_str = json.dumps(data)
        payload = {"json": json_str}
        response = requests.post(self.url, data=payload, timeout=5)
        try:
            geolocation = response.json()
        except Exception as e:
            geolocation = {"error": f"{e}"}
        position = geolocation.get("position", {})
        # Return error, if location is determined, based on IP
        if position.get("type") == "ip":
            location["error"] = "IP, not WiFi"
            return location
        # Otherwise process normally
        location["latitude"] = position.get("latitude")
        location["longitude"] = position.get("longitude")
        location["error"] = geolocation.get("error")
        return location

    def _get_nmcli_output(self) -> str:
        nmcli_output = subprocess.check_output(
            "nmcli -f BSSID,SSID,SIGNAL dev wifi",
            encoding="utf-8",
            shell=True
        )
        return nmcli_output

    def _parse_nmcli_output(self, output: str) -> list:
        """Get Wifi networks by parsing nmcli output."""
        wifi_networks = []
        # Compile regular expression to search for required string parts
        line_re = re.compile(r'(^[\w:]+)\s+([\S ]+)\s+(\d+)$')
        # Process output lines to get WiFi networks
        for line in output.split('\n'):
            match = line_re.search(line.strip())
            if match:
                mac_address, ssid, signal_strength = match.groups()
                wifi_network = {"mac": mac_address, "signal_strength": int(signal_strength)}
                wifi_networks.append(wifi_network)
        return wifi_networks 

    def _get_location_gps(self) -> dict:
        """Get location from local GPS receiver."""
        location = self._get_location_template()
        self._connect()
        for _ in range(self.max_retries):
            try:
                self.packet = gpsd.get_current()
            except Exception:
                return location
            if self.packet.mode >= 2 and self.packet.lat != 'n/a' and self.packet.lon != 'n/a':
                location["latitude"] = self.packet.lat
                location["longitude"] = self.packet.lon
                return location
        return location

    def _get_location_template(self) -> dict:
        """Return default location template."""
        return {"latitude": None, "longitude": None, "error": None}

    def _is_invalid(self, location: dict) -> bool:
        """Check whether obtained location is invalid or not."""
        return (
            location.get("error") is not None
            or location.get("latitude") is None
            or location.get("longitude") is None
        )

    def _connect(self) -> None:
        """Wrapper around gps.connect()"""
        if not self._gpsd_connected:
            try:
                gpsd.connect()
                self._gpsd_connected = True
            except Exception:
                return
        return

    def run(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.get_location(*args, **kwargs)