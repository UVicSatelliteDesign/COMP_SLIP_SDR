# COMP_SLIP_SDR

This repository contains the code for the Ground Station (GS) side of a custom data link layer protocol between a LimeSDR Mini and a CC1201 transceiver on the satellite side using GNU Radio.

## Communication Overview

- **Mode:** Half-Duplex (Due to CC1201 constraints)
- **Topology:** Point-to-Point
- **Bandwidth:** 30.72e6
- **Frequency:** Sub-920 MHz (set at runtime)
- **Tools:** GNU Radio, LimeSuite, Python
- **Transceivers:** LimeSDR Mini (GS), CC1201 (Satellite)

---

### Packet Structure

| Field         | Size      |
|---------------|-----------|
| Preamble      | 1 byte    |
| Sync Word     | 4 bytes   |
| Length Field  | 1 byte    |
| Payload       | 120 bytes |
| CRC           | 2 bytes   |

### Payload Format

- **Payload Type:** 1 byte
- **Sequence Number:** 2 bytes
- **Offset:** 3 bytes (if camera data otherwise 0 bits)
- **Data:** Variable-length (depends on payload type)

---

## Communication Reliability Features

- **ARQ:** Automatic Repeat Request  
  - ACK/NACK handling  
  - Lost-state ping recovery
- **CRC:** 16-bit checksum

---

### OSI Layer Mapping

| OSI Layer     | Implementation                   |
|---------------|----------------------------------|
| Physical      | LimeSDR RF front-end             |
| Data Link     | GNU Radio custom framing         |
| Network       | Python `Receiver` class          |
| Network       | Python `Transceiver` class       |
| Transport     | Host-side logic in `main.py`     |

---

## Current Development Status

We have implemented a **full offline TX/RX testing pipeline** in GNU Radio to validate framing, modulation, and decoding without requiring live RF hardware.

**TX Flowgraph:**
- Starts with `Message Strobe` + `Socket to PDU`
- Encodes and modulates packets
- Ends in `File Sink` writing **`tx_baseband.cfile`** (raw complex baseband samples)

**RX Flowgraph:**
- Starts with `File Source` reading **`tx_baseband.cfile`**
- Demodulates and decodes packets
- Ends in `File Sink` writing **`output.txt`** (decoded messages)

**Testing Progress:**
- [PASS] TX connects via socket (TX Flowgraph)
- [PASS] TX generates `.cfile` with valid, non-zero IQ samples (TX Flowgraph)  
- [PASS] `.cfile` contains correct modulation pattern for known test messages (File Integrity)  
- [PENDING] Feeding `.cfile` into RX produces correct packet decoding in `output.txt` (RX Loopback)  
- [PENDING] Frame validation (preamble + sync word detection) pending (Frame Validation)  
- [PENDING] CRC error handling pending (CRC Error Handling)  
- [PENDING] Max payload size test pending (Payload Size)  
- [PENDING] Min payload size test pending (Minimum Payload)  
- [PENDING] End-to-end integration pending (End-to-End Integration)  

---

### TX

```text
[Message Strobe]                # Periodically sends a predefined test message (payload)
     ↓
[Socket to PDU]                 # Receives PDUs (Protocol Data Units) over TCP/UDP socket
     ↓
[PDU to Tagged Stream]          # Converts discrete PDUs into a continuous stream with length tags
     ↓
[GFSK Mod]                      # Performs Gaussian Frequency Shift Keying modulation
     ↓
[Soapy LimeSDR Sink]            # Sends modulated baseband samples to the LimeSDR for RF transmission

```

---

### RX

```text
[Soapy LimeSDR Source]          # Captures baseband IQ samples from the LimeSDR
     ↓
[GFSK Demod]                    # Demodulates the GFSK-modulated signal into a bitstream
     ↓
[Throttle]                      # Limits sample rate for consistency
     ↓
[Unpack K bits]                 # Splits bytes into individual bits for processing
     ↓
[Correlate Access Code - Tag Stream]  # Detects sync word/preamble and tags packet start
     ↓
[Pack K bits]                   # Groups bits back into bytes after sync detection
     ↓
[Tagged Stream Align]           # Ensures byte alignment in the tagged stream
     ↓
[Tagged Stream to PDU]          # Converts tagged byte stream into PDUs
     ↓
[CRC Check]                     # Verifies packet integrity using CRC-16
     ↓
[Socket To PDU]                 # Sends recovered PDUs to a host application over TCP/UDP         
  ```