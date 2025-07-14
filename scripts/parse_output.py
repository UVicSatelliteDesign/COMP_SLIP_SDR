#!/usr/bin/env python3
from receiver import ReceivedPacket

def main():
    try:
        with open("./scripts/output.txt", "rb") as f:
            while True:
                # Read the packet length prefix (if used)
                packet = f.read(18)  # Replace with the actual packet length if fixed

                if not packet:
                    break  # End of file

                # Interpret using your packet class
                pkt = ReceivedPacket(packet)
                
                print("=" * 50)
                print(f"Payload Type:       {pkt.payload_type}")
                print(f"Sequence Number:    {pkt.sequence_number}")
                print(f"Offset:             {pkt.offset}")
                print(f"Payload (hex):      {pkt.payload.hex() if pkt.payload else None}")
                print(f"Payload (utf-8?):   {pkt.payload.decode(errors='ignore') if pkt.payload else None}")
                print("=" * 50 + "\n")

    except FileNotFoundError:
        print("output.txt not found.")
    except Exception as e:
        print(f"Error reading packets: {e}")

if __name__ == "__main__":
    main()
