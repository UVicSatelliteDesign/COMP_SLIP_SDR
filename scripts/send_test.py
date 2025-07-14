import socket
import time

HOST = '127.0.0.1'
PORT = 52001  # Match GNU Radio Socket PDU sink's port

with open("./scripts/test_packets.txt", "r") as f:
    packets = [bytes.fromhex(line.strip()) for line in f.readlines()]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

for pkt in packets:
    s.send(pkt)
    print("Sent:", pkt.hex())
    time.sleep(1)  # Delay between sends for clarity

s.close()
