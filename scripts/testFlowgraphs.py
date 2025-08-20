import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Set Qt to use offscreen rendering

import subprocess
import time
import socket
import numpy as np
import signal


# ================= Global Constants (configuration) ================= #
TX_FILE = os.path.join("scripts", "tx_baseband.cfile")
RX_OUTPUT = os.path.join("scripts", "output.txt")
HOST = '127.0.0.1'
PORT = 52001  # Must match port in Tranx.py

# Framing parameters
PREAMBLE = b"\xAA"          # 8-bit preamble 0b10101010
SYNC_WORD = 0x00000001       # 32-bit sync word value
CRC_POLY = 0x8005            # CRC-16-IBM polynomial
CRC_INIT = 0xFFFF            # CRC-16 initial value

# Test payload (raw application data)
RAW_PAYLOAD = b"TEST123"

# Placeholders (populated after helper definitions)
TEST_MESSAGE: bytes  = b""   # Full framed message populated after helpers
EXPECTED_PAYLOAD = RAW_PAYLOAD

# Multi-message test parameters
NUM_TEST_MESSAGES = 200            # Number of framed messages to send to TX socket
INTER_MESSAGE_DELAY = 0.005        # Seconds to wait between consecutive sends
TX_STARTUP_WAIT_SECONDS = 15        # Time to allow TX flowgraph to run before sending messages / shutdown
SINGLE_MESSAGE_REPEATS = 5          # How many times legacy send_test_message repeats the frame


# CRC Helper
def crc16_ibm(data: bytes, poly: int = CRC_POLY, init_val: int = CRC_INIT) -> int:
    """Compute CRC-16-IBM (a.k.a. CRC-16-ANSI) over data."""
    crc = init_val
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ poly) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

# CRC Helper
def build_frame(payload: bytes) -> bytes:
    """Build custom frame: PREAMBLE(0xAA) | SYNC(0x00000001) | LEN | PAYLOAD | CRC16.

    NOTE: LEN is payload length only (1 byte). CRC is over payload only.
    """
    preamble = PREAMBLE
    sync_word = SYNC_WORD.to_bytes(4, 'big')
    length = len(payload).to_bytes(1, 'big')
    crc_val = crc16_ibm(payload)
    crc_bytes = crc_val.to_bytes(2, 'big')
    return preamble + sync_word + length + payload + crc_bytes

# Build framed test message now that helpers exist
TEST_MESSAGE = build_frame(RAW_PAYLOAD)

# Begin executing flowgraph
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

# TODO: This function is flawed. Showed issues recognizing whether the file was written to or not. 
# That's why we created TEST_tx_baseband.py to read the file and interpret the data visually. 
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


# TODO: This function is flawed. Showed issues recognizing whether the file was written to or not. 
# That's why we created TEST_tx_baseband.py to read the file and interpret the data visually. 
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

# TODO: This function is flawed. Showed issues recognizing whether the file was written to or not. 
# That's why we created TEST_tx_baseband.py to read the file and interpret the data visually. 
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

# Connection and transfer of data function
def send_test_message():  # kept for backward compatibility / single-shot diagnostics
    """Send a few repeats of the framed test message over a single connection.

    Uses SMALL loop (SINGLE_MESSAGE_REPEATS) to generate a slightly longer .cfile
    without invoking the bulk multi-message helper.
    """
    print(f"\n[INFO] Connecting to TX socket to send {SINGLE_MESSAGE_REPEATS} repeated framed messages (legacy helper)...")
    attempts = 5
    attempt_delay = 1
    for i in range(attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                start = time.time()
                for _ in range(SINGLE_MESSAGE_REPEATS):
                    s.sendall(TEST_MESSAGE)
                elapsed = time.time() - start
                total_bytes = len(TEST_MESSAGE) * SINGLE_MESSAGE_REPEATS
                print(f"[PASS] Sent {SINGLE_MESSAGE_REPEATS} repeats -> {total_bytes} bytes in {elapsed:.3f}s")
                return
        except ConnectionRefusedError:
            print(f"[WARN] Connection attempt {i+1} failed. Retrying in {attempt_delay} seconds...")
            time.sleep(attempt_delay)
    raise ConnectionRefusedError(f"Failed to connect to {HOST}:{PORT} after {attempts} attempts.")


def send_multiple_test_messages(count=NUM_TEST_MESSAGES, delay=INTER_MESSAGE_DELAY):
    """Connect once to the TX socket and send 'count' framed test messages.

    Parameters:
        count (int): Number of messages to send.
        delay (float): Delay in seconds between each message to pace the flowgraph.
    """
    print(f"\n[INFO] Connecting to TX socket to send {count} framed test messages...")
    attempts = 5
    attempt_delay = 1
    for i in range(attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                start = time.time()
                for n in range(count):
                    s.sendall(TEST_MESSAGE)
                    if delay > 0:
                        time.sleep(delay)
                elapsed = time.time() - start
                total_bytes = len(TEST_MESSAGE) * count
                print(f"[PASS] Sent {count} messages (payload={RAW_PAYLOAD.decode()}) -> {total_bytes} bytes in {elapsed:.2f}s")
                return
        except ConnectionRefusedError:
            print(f"[WARN] Connection attempt {i+1} failed. Retrying in {attempt_delay} seconds...")
            time.sleep(attempt_delay)
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
        raise AssertionError(
            f"Expected payload {expected_bytes} in RX output, got {contents.hex()} (len={len(contents)})"
        )
    print(f"[PASS] RX output contains expected payload {expected_bytes}.")

# Execution order
if __name__ == "__main__":
    print("=== Test 1: Tranx: socket connection and .cfile generation ===")
    tx_proc = run_process("python3 flowgraphs/Tranx.py", wait=TX_STARTUP_WAIT_SECONDS)  # Extended runtime before sending
    try:
        send_multiple_test_messages()  # Send many messages to generate sufficient samples
        # wait_for_file_to_fill(TX_FILE, timeout=30, poll_interval=2) TODO: Check the validity of this function later
    finally:
        print("[INFO] Terminating TX flowgraph using pkill with SIGINT for graceful shutdown...")
        subprocess.run(["pkill", "-SIGINT", "-f", "Tranx.py"], check=False) # Safest way I could find to end the process
        try:
            tx_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("[WARN] Process did not exit in time on SIGINT; sending SIGKILL...")
            tx_proc.kill()
            tx_proc.wait()
        time.sleep(2.5) # Slightly longer delay to ensure buffers flushed for larger sample set

    check_file_exists(TX_FILE)
    check_cfile_nonzero(TX_FILE)

    print("\n=== Test 2: RX Flowgraph: decoding .cfile ===")
    rx_proc = run_process("python3 flowgraphs/rx_flowgraph.py", wait=7)
    try:
        time.sleep(7)  # time for RX flowgraph to process the file and output data
    finally:
        print("[INFO] Terminating RX flowgraph using pkill with SIGINT for graceful shutdown...")
        subprocess.run(["pkill", "-SIGINT", "-f", "rx_flowgraph.py"], check=False) # Safest way to kill the process
        try:
            rx_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("[WARN] RX process did not exit in time on SIGINT; sending SIGKILL...")
            rx_proc.kill()
            rx_proc.wait()
        time.sleep(1)  # brief delay to allow final buffers to flush

    check_file_exists(RX_OUTPUT)
    check_rx_output(EXPECTED_PAYLOAD)

    print("\nAll tests passed successfully!")
