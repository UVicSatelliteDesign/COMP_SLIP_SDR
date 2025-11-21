import subprocess
import time

GNU_RADIO_VENV = "/usr/local/Cellar/gnuradio/3.10.12.0_7/libexec/venv/bin/python"

def test_sample():
    # Launch the `testing_connection` flowgraph in the background
    flowgraph = subprocess.Popen([GNU_RADIO_VENV, "flowgraphs/testing_connection.py"])
    # Wait for it to initialize
    time.sleep(3)

    # Run `send_test.py` to send `test_packets.txt` to the flowgraph
    test_script = subprocess.run(["python3", "scripts/send_test.py"])
    # Wait for it to send
    time.sleep(1)
    
    # Load test_packets as a single stream of bytes
    with open("scripts/test_packets.txt", "r") as f:
        content = f.read().replace("\n", "")
        test_packets = bytes.fromhex(content)

    # Check the output of the flowgraph
    with open("scripts/output.txt", "rb") as f:
        content = f.read()
        print("DBG")
        print(f"output.txt {content}")
        print(f"test_packets {test_packets}")
        assert content == test_packets

    flowgraph.terminate()

if __name__ == "__main__":
    print("Running test as executable")
    test_sample()
