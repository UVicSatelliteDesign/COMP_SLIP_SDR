#!/usr/bin/env python
"""
from backend.pass_app_layer import (
    handle_ping,
    handle_nominal,
    handle_low_power,
    handle_telemetry,
    handle_camera1_end,
    handle_camera1_mf,
    handle_camera2_end,
    handle_camera2_mf,
    handle_req_init_transmission,
    handle_error_peripheral,
    handle_error_dup,
    handle_error_lp,
    handle_ack_camera,
    handle_ack_telemetry,
    handle_ack_status,
    handle_ack_error
)
"""
class ReceivedPacket():
    def __init__(self, data: bytes):
        '''
        Parses received binary data according to the following format:
        - First 4 bits: payload_type
        - Next bits (variable length): payload
        - Next 17 bits: offset (only for specific types)
        - Last 15 bits: sequence number
        '''
        self.payload_type = None
        self.payload = None
        self.offset = None
        self.sequence_number = None

        try:
            # Total bits in data
            total_bits = len(data) * 8

            # Ensure data length is valid (at least 4 bits payload_type + 15 bits sequence number)
            assert total_bits > 19, "Data too short for defined format"

            # Extract payload_type (first 4 bits)
            first_byte = data[0]
            self.payload_type = first_byte >> 4

            if self.payload_type in [0b0100, 0b0101, 0b0110, 0b0111]:
                # Calculate payload length in bits and bytes
                payload_bits_length = total_bits - 36  # 4 bits type + 17 offset + 15 seq
                payload_bytes_length = (payload_bits_length + 7) // 8

                if payload_bytes_length > 0:
                    payload_bits = int.from_bytes(data, 'big')
                    payload_bits >>= 32  # Strip 17 offset + 15 seq
                    payload_bits &= (1 << payload_bits_length) - 1
                    self.payload = payload_bits.to_bytes(payload_bytes_length, 'big')
                else:
                    self.payload = b''

                # Extract offset (17 bits before sequence number)
                last_four_bytes = int.from_bytes(data[-4:], 'big')
                self.offset = (last_four_bytes >> 15) & 0x1FFFF  # 17 bits

            else:
                # Only 4 bits (type) and 15 bits (seq); the rest is payload
                payload_bits_length = total_bits - 19  # 4 bits type + 15 bits seq
                payload_bytes_length = (payload_bits_length + 7) // 8

                if payload_bytes_length > 0:
                    payload_bits = int.from_bytes(data, 'big')
                    payload_bits >>= 15  # Strip 15-bit sequence number
                    payload_bits &= (1 << payload_bits_length) - 1
                    self.payload = payload_bits.to_bytes(payload_bytes_length, 'big')
                else:
                    self.payload = b''

                self.offset = None  # Offset does not exist for these types

            # Extract sequence_number (last 15 bits)
            last_two_bytes = int.from_bytes(data[-2:], 'big')
            self.sequence_number = last_two_bytes & 0x7FFF  # Mask 15 bits

        except (AssertionError, ValueError, IndexError) as e:
            print(f"Initialization error: {e}")
            self.payload_type = None
            self.payload = None
            self.offset = None
            self.sequence_number = None

    def __repr__(self):
        return (f"ReceivedPacket(payload_type={self.payload_type}, "
                f"offset={self.offset}, "
                f"sequence_number={self.sequence_number})")

    def pass_to_application(self):
        '''
        Passes payload to the application layer according to the address field (payload_type).
        '''
        if self.payload_type is None:
            print("Invalid packet. Nothing to pass to application layer.")
            return
        """
        if self.payload_type == 0b0000:
            handle_ping(self.payload) # TODO:
        elif self.payload_type == 0b0001:
            handle_nominal(self.payload) # TODO:
        elif self.payload_type == 0b0010:
            handle_low_power(self.payload) # TODO:
        elif self.payload_type == 0b0011:
            handle_telemetry(self.payload) # TODO:
        elif self.payload_type == 0b0100:
            handle_camera1_end(self.payload) # TODO:
        elif self.payload_type == 0b0101:
            handle_camera1_mf(self.payload) # TODO:
        elif self.payload_type == 0b0110:
            handle_camera2_end(self.payload) # TODO:
        elif self.payload_type == 0b0111:
            handle_camera2_mf(self.payload) # TODO:

        elif self.payload_type == 0b1000:
            handle_switch(self.payload) # This payload type is only used once to turn on the satellite # TODO:
        elif self.payload_type == 0b1001:
            handle_error_peripheral(self.payload) # Type of peripheral malfunction provided in payload in english # TODO:
        elif self.payload_type == 0b1010:
            handle_error_dup(self.payload) # TODO:
        elif self.payload_type == 0b1011:
            handle_erro_lp(self.payload) # TODO:
        elif self.payload_type == 0b1100:
            handle_ack_camera(self.payload) # TODO:
        elif self.payload_type == 0b1101:

            handle_ack_telemetry(self.payload) # TODO:
        elif self.payload_type == 0b1110:
            handle_ack_status(self.payload) # TODO:
        elif self.payload_type == 0b1111:
            handle_ack_error(self.payload) # TODO:
        else:
            print(f"Unknown address field: {self.payload}. Payload not routed.")
        """