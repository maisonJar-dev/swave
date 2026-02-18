import pyaudiowpatch as pyaudio
import numpy as np
# Made with the help of AI cause system audio stuff turns out to be a real bitch and I don't have time for it :(
# So Vibe Coding cause fuck my degree :|

#Audio frames read at one time. Basically Buffer Size
CHUNK = 1024

class AudioEngine:
    def __init__(self):
        self.loopback_index = None
        self._running = True
        self.magnitudes = np.zeros(CHUNK // 2 + 1)
        self.rms = 0.0
        self.device_info = None

    #PyAudio is created insdie run() using a with plack so the instance is needed as a parameter
    def _get_default_loopback_index(self, p: pyaudio.PyAudio) -> int:
        #Gets windows default output and lowercases for easier handling
        out = p.get_default_output_device_info()
        out_name = out["name"].lower()

        #Exposes a generator of all WASAPI (Windows Audio Session API) loopback devices
        #Generator in python is lazy, produces values one at a time instead of all at once,
        # Wrapping it in a list forces it to evaluate everything immediately so we cann loop over 
        # it multiple times
        loopbacks = list(p.get_loopback_device_info_generator())
        if not loopbacks:
            raise RuntimeError("No loopback devices detected (WASAPI loopback unavailable).")

        # Best-effort name match
        for d in loopbacks:
            if out_name in d["name"].lower() or d["name"].lower() in out_name:
                return d["index"]

        # Fallback: pick the first loopback device
        return loopbacks[0]["index"]

    def run(self):
        #Makes sure that resources are properly cleaned up using with block
        with pyaudio.PyAudio() as p:
            self.loopback_index = self._get_default_loopback_index(p)

            dev = p.get_device_info_by_index(self.loopback_index)
            self.device_info = dev
            rate = int(dev["defaultSampleRate"])
            #Pythonic trick - (Says Claude), is maxInputChannels is 0 or falsy, or 2 kicks in and 
            # defualts to 2, basically java ternary (Yay Java!)
            channels = int(dev["maxInputChannels"]) or 2

            print("Default output loopback:", dev["name"])
            print(f"rate={rate}  channels={channels}")
            print("Play audio now... (Ctrl+C to stop)")

            with p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=self.loopback_index,
                frames_per_buffer=CHUNK,
            ) as stream:
                while self._running:
                    #stream.read() returns raw bytes
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    #np.frombuffer() interprets those bytes as a numpy array of 32-bit floats, this shit is RAW DATA BABYYYY
                    x = np.frombuffer(data, dtype=np.float32)
                    #Complex Numbers Based on Amplitude and Phase (where it is in time) 
                    fft = np.fft.rfft(x) 
                    #Throw away phase, puts us back to floats for Visualization data
                    self.magnitudes = np.abs(fft)
                    #RMS (Root Mean Square) is a measure of audio loudness
                    rms = float(np.sqrt(np.mean(x * x))) if x.size else 0.0
                    self.rms = rms
                    print(f"RMS: {rms:.6f}", end="\r")

    def start(self):
        import threading
        threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        self._running = False

if __name__ == "__main__":
    engine = AudioEngine()
    engine.start()
    try:
        import time
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        engine.stop()
        print("\nStopped cleanly.")