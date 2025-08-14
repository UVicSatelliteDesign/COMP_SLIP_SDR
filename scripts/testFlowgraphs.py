import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Set Qt to use offscreen rendering

import subprocess
import time
import socket
import numpy as np
import signal

# File names & connection settings
TX_FILE = os.path.join("scripts", "tx_baseband.cfile")
RX_OUTPUT = os.path.join("scripts", "output.txt")
HOST = '127.0.0.1'
PORT = 52001  # Changed port for testing; update Tranx.py accordingly if you make this change
TEST_MESSAGE = b"TEST123"  # Test message to send over the socket

def run_process(command, wait=0):
    """
    Start a process with the given command and return the Popen object
    (process open), using modified environment.
    """
    print(f"\n[RUN] {command}")
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    proc = subprocess.Popen(command, shell=True, env=env)
    time.sleep(wait)
    return proc

def check_file_exists(path):
    """
    Check that a file exists and is non-empty.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found.")
    size = os.path.getsize(path)
    if size == 0:
        raise ValueError(f"{path} is empty.")
    print(f"[PASS] {path} exists, size: {size} bytes")

def check_cfile_nonzero(path):
    """
    Check that .cfile contains non-zero complex data.
    """
    data = np.fromfile(path, dtype=np.complex64)
    if data.size == 0:
        raise ValueError(f"{path} contains no samples.")
    if not np.any(data):
        raise ValueError(f"{path} contains only zeros.")
    print(f"[PASS] {path} contains {len(data)} complex samples.")

def wait_for_file_to_fill(filepath, timeout=30, poll_interval=1):
    """
    Wait until the file exists and its size is non-zero, or until timeout.

    TODO: Created to handle difficulties with terminating one flowgraph and plugging output
    into another
    """
    print(f"[INFO] Waiting for {filepath} to be filled with data...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            print(f"[PASS] {filepath} is filled with data.")
            return
        time.sleep(poll_interval)
    raise TimeoutError(f"Timeout: {filepath} did not fill with data within {timeout} seconds.")

def send_test_message():
    """
    Connect to the TX socket and send a test message
    """
    print("\n[INFO] Connecting to TX socket to send test data...")
    attempts = 5
    delay = 1  # seconds between attempts
    for i in range(attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.send(TEST_MESSAGE)
                print(f"[PASS] Sent test message: {TEST_MESSAGE.decode()}")
                return
        except ConnectionRefusedError:
            print(f"[WARN] Connection attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise ConnectionRefusedError(f"Failed to connect to {HOST}:{PORT} after {attempts} attempts.")

def check_rx_output(expected_bytes):
    """
    Check that the RX output contains the expected message.
    """
    if not os.path.exists(RX_OUTPUT):
        raise FileNotFoundError(f"{RX_OUTPUT} not found.")
    with open(RX_OUTPUT, "rb") as f:
        contents = f.read().strip()
    print(f"[INFO] RX output (hex): {contents.hex()}")
    if expected_bytes not in contents:
        raise AssertionError(f"Expected {expected_bytes} in RX output, got {contents}.")
    print(f"[PASS] RX output contains the expected message.")

if __name__ == "__main__":
    print("=== Test 1: Tranx: socket connection and .cfile generation ===")
    # Launch the TX flowgraph (make sure its port matches PORT)
    tx_proc = run_process("python3 flowgraphs/Tranx.py", wait=7)  # Allow for startup
    try:
        send_test_message()  # Send the test message over TX socket
        # Wait until the file is populated.
        wait_for_file_to_fill(TX_FILE, timeout=30, poll_interval=2)
    finally:
        print("[INFO] Terminating TX flowgraph using SIGTERM for graceful shutdown...")
        tx_proc.terminate()  # Send SIGTERM TODO: Find better solution
        try:
            tx_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("[WARN] Process did not exit in time on SIGTERM; sending SIGKILL...")
            tx_proc.kill()
            tx_proc.wait()
        time.sleep(2) # Delay for process to output data

    check_file_exists(TX_FILE)
    check_cfile_nonzero(TX_FILE)

    ### Test 2: RX flowgraph – decode the .cfile and verify decoded output ###
    print("\n=== Test 2: RX Flowgraph: decoding .cfile ===")
    rx_proc = run_process("python3 flowgraphs/rx_flowgraph.py", wait=7)
    try:
        time.sleep(7)  # time for RX flowgraph to process the file and output data
    finally:
        print("[INFO] Terminating RX flowgraph...")
        rx_proc.terminate()
        rx_proc.wait()

    check_file_exists(RX_OUTPUT)
    check_rx_output(TEST_MESSAGE)

    print("\nAll tests passed successfully!")
