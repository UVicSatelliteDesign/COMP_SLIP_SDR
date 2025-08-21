#!/usr/bin/env python

class ReceivedPacket():
    def __init__(self, data: bytes):
        '''
        Parses received binary data according to the following format:
        - First 8 bits (1 byte): payload_type
        - Next bytes (variable length): payload
    - Next 24 bits (3 bytes): offset (only for specific payload types)
        - Last 16 bits (2 bytes): sequence number

        Assumptions (can be adjusted): payload types 0b0100 through 0b0111 (4..7) include an offset.
        '''
        self.payload_type: int | None = None
        self.payload: bytes | None = None
        self.offset: int | None = None
        self.sequence_number: int | None = None
        self.payload_length: int = 0

        try:
            assert isinstance(data, (bytes, bytearray)), "data must be bytes-like"
            length = len(data)
            assert length >= 3, "Data too short (need at least type + seq)"

            self.payload_type = data[0]

            # Define which payload types contain an offset (adjust if spec changes)
            types_with_offset = {0b0100, 0b0101, 0b0110, 0b0111}

            if self.payload_type in types_with_offset:
                # Need at least 6 bytes: 1 (type) + 3 (offset) + 2 (seq)
                assert length >= 6, "Data too short for packet with offset"
                # Sequence number: last 2 bytes
                self.sequence_number = int.from_bytes(data[-2:], 'big')
                # Offset: 3 bytes before sequence
                self.offset = int.from_bytes(data[-5:-2], 'big')  # 24 bits
                # Payload: bytes between type and offset
                self.payload = data[1:-5]
            else:
                # Sequence number: last 2 bytes
                self.sequence_number = int.from_bytes(data[-2:], 'big')
                self.offset = None
                # Payload: bytes between type and sequence number
                self.payload = data[1:-2]

            self.payload_length = len(self.payload)

        except (AssertionError, ValueError, IndexError) as e:
            print(f"Initialization error: {e}")
            self.payload_type = None
            self.payload = None
            self.offset = None
            self.sequence_number = None
            self.payload_length = 0

    def __repr__(self):
        return (f"ReceivedPacket(payload_type={self.payload_type}, length={self.payload_length}, "
                f"offset={self.offset}, sequence_number={self.sequence_number})")
