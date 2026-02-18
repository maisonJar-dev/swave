import sounddevice as sd

# Get all host APIs available on your machine
host_apis = sd.query_hostapis()

found_wasapi = False
for api in host_apis:
    if "WASAPI" in api['name']:
        print(f"✅ WASAPI Found! (Index: {api['name']})")
        print(f"   Default Input Device ID: {api['default_input_device']}")
        print(f"   Default Output Device ID: {api['default_output_device']}")
        found_wasapi = True

if not found_wasapi:
    print("❌ WASAPI not detected. Are you on Mac or Linux?")

if found_wasapi:
    print("🎧 Supported Devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        # We look for output devices (max_output_channels > 0) 
        # that are handled by the WASAPI host API
        host_api_name = sd.query_hostapis(dev['hostapi'])['name']
        
        if host_api_name == "Windows WASAPI" and dev['max_output_channels'] > 0:
            print(f"\tID {i}: {dev['name']} [LOOPBACK CAPABLE]")