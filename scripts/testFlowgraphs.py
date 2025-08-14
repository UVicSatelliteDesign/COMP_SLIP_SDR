import subprocess
import os
import time
import socket
import numpy as np

# File names & connection settings
TX_FILE = os.path.join("scripts", "tx_baseband.cfile")
RX_OUTPUT = os.path.join("scripts", "output.txt")
HOST = '127.0.0.1'
PORT = 52001  # Must match the TX flowgraph socket port
TEST_MESSAGE = b"TEST123"  # Test message to send over the socket

def run_process(command, wait=0):
    """Start a process with the given command and return the Popen object."""
    print(f"\n[RUN] {command}")
    proc = subprocess.Popen(command, shell=True)
    time.sleep(wait)
    return proc

def check_file_exists(path):
    """Check that a file exists and is non-empty."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    size = os.path.getsize(path)
    if size == 0:
        raise ValueError(f"{path} is empty.")
    print(f"[PASS] {path} exists, size: {size} bytes")

def check_cfile_nonzero(path):
    """Check that .cfile contains non-zero complex data."""
    # The TX file is assumed to have complex64 samples
    data = np.fromfile(path, dtype=np.complex64)
    if data.size == 0:
        raise ValueError(f"{path} contains no samples.")
    if not np.any(data):
        raise ValueError(f"{path} contains only zeros.")
    print(f"[PASS] {path} contains {len(data)} complex samples.")

def send_test_message():
    """Connect to the TX socket and send a test message."""
    print("\n[INFO] Connecting to TX socket to send test data...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wait a short time to ensure TX flowgraph is listening
        time.sleep(1)
        s.connect((HOST, PORT))
        s.send(TEST_MESSAGE)
        print(f"[PASS] Sent test message: {TEST_MESSAGE.decode()}")

def check_rx_output(expected_bytes):
    """Check that the RX output contains the expected message."""
    if not os.path.exists(RX_OUTPUT):
        raise FileNotFoundError(f"{RX_OUTPUT} not found.")
    with open(RX_OUTPUT, "rb") as f:
        contents = f.read().strip()
    # For debugging, print the hex output
    print(f"[INFO] RX output (hex): {contents.hex()}")
    # Here we assume that the RX flowgraph recovers the original payload exactly.
    if expected_bytes not in contents:
        raise AssertionError(f"Expected {expected_bytes} in RX output, got {contents}.")
    print(f"[PASS] RX output contains the expected message.")

if __name__ == "__main__":
    ### Test 1: TX flowgraph – send data over socket and check .cfile generated ###
    print("=== Test 1: TX Flowgraph: socket connection and .cfile generation ===")
    # Update command to point to the correct file location:
    tx_proc = run_process("python flowgraphs/tx_flowgraph.py", wait=3)
    try:
        send_test_message()  # Send the test message over TX socket

        # Allow some time for the flowgraph to process and write to file
        time.sleep(3)
    finally:
        print("[INFO] Terminating TX flowgraph...") 
        tx_proc.terminate()
        tx_proc.wait()

    check_file_exists(TX_FILE)
    check_cfile_nonzero(TX_FILE)

    ### Test 2: RX flowgraph – decode the .cfile and verify decoded output ###
    print("\n=== Test 2: RX Flowgraph: decoding .cfile ===")
    rx_proc = run_process("python flowgraphs/rx_flowgraph.py", wait=3)
    try:
        # Allow time for the RX flowgraph to read the file and output data
        time.sleep(3)
    finally:
        print("[INFO] Terminating RX flowgraph...")
        rx_proc.terminate()
        rx_proc.wait()

    check_file_exists(RX_OUTPUT)
    check_rx_output(TEST_MESSAGE)

    print("\n✅ All tests passed successfully!")
