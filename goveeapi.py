import requests
import asyncio
import logging
import json

from govee_led_wez import GoveeController, GoveeDevice, GoveeDeviceState, GoveeColor


_LOGGER = logging.getLogger(__name__)


class GoveeAPI(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def poller_loop(self):
        pass

    def get_device(self, device_id, model):
        _LOGGER.debug('getting device {}'.format(device_id))
        headers = self.get_headers()

        params = {
            'device': device_id,
            'model': model
        }

        try:
            r = requests.get('https://developer-api.govee.com/v1/devices/state', headers=headers, params=params)
            if r.status_code >= 400:
                _LOGGER.error('BAD RESPONSE CODE GETTING DEVICE {}'.format(device_id))
                return {}
            data = r.json()
        except:
            _LOGGER.error('ERROR GETTING DEVICE {}'.format(device_id))
            return {}

        _LOGGER.debug(data)

        device = data['data']['device']

        new_attributes = {}
        for attribute_data in data['data']['properties']:
            for key in attribute_data:
                new_attributes[key] = attribute_data[key]

        return new_attributes
    
    def normalizeBrightness(self, x: int):
        return round(x/254*100)
    
    def brightnessScale(self):
        return 255


    def get_device_list(self):
        _LOGGER.debug('getting devices list')
        headers = self.get_headers()

        try:
            r = requests.get('https://developer-api.govee.com/v1/devices', headers=headers)
            if r.status_code >= 400:
                _LOGGER.error('BAD RESPONSE CODE GETTING DEVICE LIST')
                return {}
            data = r.json()
        except:
            _LOGGER.error('ERROR GETTING DEVICE LIST')
            return {}

        _LOGGER.debug(data)
        return data['data']

 
    def get_headers(self):
        return {
            'Content-Type': "application/json",
            'Govee-API-Key': self.api_key
        }


    def send_command(self, device_id, model, cmd, value):
        data = {
            "device": device_id,
            "model": model,
            "cmd": {
                "name": cmd,
                "value": value
            },
        }

        headers = self.get_headers()
        try:
            r = requests.put('https://developer-api.govee.com/v1/devices/control', headers=headers, data=json.dumps(data))
            if r.status_code >= 400:
                _LOGGER.error('BAD RESPONSE CODE SENDING COMMAND {} {}'.format(device_id, data))
                return {}
        except:
            _LOGGER.error('ERROR SENDING DEVICE COMMAND')
            
        _LOGGER.debug(r)

class GoveeLocalAPI(object):

    def __init__(self):
        self.controller = GoveeController()
        self.controller.set_device_change_callback(self.device_changed)
        self.devices = {}
        self.poller_started = False

    def normalizeBrightness(self, x: int):
        return x
    
    def brightnessScale(self):
        return 100


    def device_changed(self, device: GoveeDevice):
        _LOGGER.debug(f"{device.device_id} state -> {device.state}")
        _LOGGER.info(f"{device.device_id} -> {device}")
        if self.devices.get(device.device_id, None) is None:
            self.devices[device.device_id] = device
        if self.devices.get(device.device_id, None) is not None and device.state is not None:
            self.devices.get(device.device_id).state = device.state
        asyncio.create_task(self.controller.update_device_state(device))


    def get_device(self, device_id, model):
        _LOGGER.debug(f"Getting device {device_id}")
        govee_device: GoveeDevice = self.devices.get(device_id)
        asyncio.create_task(self.controller.update_device_state(govee_device))
        govee_device_state: GoveeDeviceState = govee_device.state
        if govee_device_state is None:
            return {}
        _LOGGER.debug(f"state: {govee_device_state}")
        return {
            "powerState": "on" if govee_device_state.turned_on == True else "off",
            "brightness": govee_device_state.brightness_pct,
            "color": { "r": govee_device_state.color.red, "g": govee_device_state.color.green, "b": govee_device_state.color.blue},
            "availability": True,
        }

    def get_device_list(self):
        # _LOGGER.debug("Getting devices list")
        mapped = {
            "devices": map(lambda device: {
                "device": device.device_id,
                "controllable": True,
                "model": device.model,
                "deviceName":  device.lan_definition.ip_addr + " " + device.model,
                "supportCmds": []
            } , self.devices.values())
        }
        # _LOGGER.debug(mapped)
        return mapped


    def send_command(self, device_id, model, cmd, value):
        _LOGGER.info(f"Send command {device_id}: {cmd} => {value}" )
        govee_device: GoveeDevice = self.devices.get(device_id)
        task = None
        if cmd == "color":
            task = self.controller.set_color(govee_device, GoveeColor(red=value["r"], green=value["g"], blue=value["b"]))
        if cmd == "brightness":
            task = self.controller.set_brightness(govee_device, brightness_pct=value)
        if cmd == "turn":
            task = self.controller.set_power_state(govee_device, turned_on=True if value == "on" else False)
        if task is not None:
            asyncio.run(task)

    def poller_loop(self):
        if self.poller_started is False:
            self.controller.start_lan_poller()
            self.poller_started = True
        return self.controller.lan_pollers
