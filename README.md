# Fork of Govee2MQTT with Local API support

This uses the `govee_led_wez` library to enable local mqtt control of Govee devices.

Ensure the `Local API` is enabled.

To trigger `local` mode - ensure the `config.yaml` file you are using only has:

```yaml
govee:
```

Do not include the `api_key` - as this will trigger the remote http API. 

See the file `config.yaml.sample` for the basic config options / examples. 

# Run the docker image detached:

Ensure you pass the path of your actual `config.yaml` (not the sample file) to the command below. 

```
docker run -d --name govee2mqtt --rm -v "$(pwd)/config.yaml.sample":/config/config.yaml:ro --net=host ghcr.io/mindstorms6/govee2mqtt:main
```

If you're a NixOS person:

```
virtualisation = {
    podman = {
      enable = true;
      dockerCompat = true;
    };
    containerd = {
      enable = true;
    };
    oci-containers = {
      backend = "podman";
      containers.govee2mqtt = {
        image = "ghcr.io/mindstorms6/govee2mqtt:sha-229d4ddf14fb8be9457f6b3e346cd1fe36f16d69";
        autoStart = true;
        extraOptions = [ "--net=host" "--privileged" ];
        volumes = [ "/home/breland/config.yaml:/config/config.yaml"];
      };
    };
  };
```


---

# Old Readme:

Govee recently released a public API to control their WiFi light strips, among other things.

I've created govee2mqtt (with homeassistant discovery) to integrate these devices.

This is very early code with little documentation. However, if you're interested, please give it a spin and feel free to submit PRs to help finish the feature set.

A few notes:
* Govee's API is SLOW. Not only does each request take longer than it should, it takes, sometimes, 3 to 4 seconds for the command to reach the light strip. Hopefully, they'll speed this up as time goes on.
* I only have model H6159. I've not tested with anything else though, in theory, it should work.
* Support is there for power on/off, brightness, and rgb_color. White Temperature is next in my list.

# Getting Started
## Direct Install
```bash
git clone https://github.com/dlashua/govee2mqtt.git
cd govee2mqtt
pip3 install -r ./requirements.txt
cp config.yaml.sample config.yaml
vi config.yaml
python3 ./app.py -c ./
```

## Docker
For `docker-compose`, use the [configuration included](https://github.com/dlashua/govee2mqtt/blob/master/docker-compose.yaml) in this repository.

An docker image is available at `dlashua/govee2mqtt:latest`. Mount your configuration volume at `/config`.


# Getting an API KEY
* Open the Govee App
* Tap on the "profile" icon (bottom right)
* Tap on "about us"
* Tap on "Apply for API Key"
* Get the API key via email within minutes

