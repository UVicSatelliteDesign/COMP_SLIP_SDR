# COMP_SLIP_SDR

This repository contains the implementation of a custom data link layer protocol between a LimeSDR Mini (Ground Station) and a CC1201 transceiver (Satellite) using GNU Radio.

## Communication Overview

- **Mode:** Half-Duplex
- **Topology:** Point-to-Point
- **Bandwidth:** 1.2 Mbps
- **Frequency:** Sub-920 MHz (set at runtime)
- **Tools:** GNU Radio, LimeSuite, Python
- **Transceivers:** LimeSDR Mini (GS), CC1201 (Satellite)

---

### Packet Structure

| Field         | Size      |
|---------------|-----------|
| Preamble      | 8 bits    |
| Sync Word     | 32 bits   |
| Length Field  | 8 bits    |
| Payload       | Variable  |
| CRC           | 16 bits   |

### Payload Format

- **Payload Type:** 4 bits
- **Sequence Number:** 15 bits
- **Offset:** 17 bits (if camera data)
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
| Network       | Python 'Transceiver' class       |
| Transport     | Host-side logic in `main.py`     |

---

### 📡 Frame Synchronization & Decoding Flow (GNU Radio)

```text
[Input Source]
     ↓
[Unpack K Bits]
     ↓
[Correlate Access Code - Tag Stream]   ← detects sync
     ↓
[Pack K Bits]
     ↓
[Tagged Stream Align]                  ← aligns stream
     ↓
[Fixed Length Tagger]                  ← reads length byte
     ↓
[Tagged Stream to PDU]                 ← converts to packets
     ↓
[Message Debug / Python CRC Checker]   ← final output
```

---

### Flowgraph Testing Instructions

This test framework simulates full end-to-end message flow using GNU Radio and Python. It verifies that sample packets can be sent from a Python script, processed by the flowgraph, and parsed for validation.

### Step-by-Step Instructions

1. **Launch the Flowgraph**
   - Open the `testing_connection.grc` flowgraph in GNU Radio Companion (GRC).
   - Run the flowgraph. It will begin listening for incoming binary data over a local TCP socket via the **Socket PDU** block.

2. **Send Test Packets**
   - Make sure you have your `test_packets.txt` file ready with the desired sample packets (in hex format).
   - Run the Python script to transmit those test packets into the flowgraph:
     ```bash
     python scripts/send_test.py
     ```

3. **Parse the Output**
   - Once the packets are processed by GNU Radio, they are written into `output.txt`.
   - Run the parser script to convert and display the output in a human-readable format:
     ```bash
     python scripts/parse_output.py
     ```

### Example Testing Workflow

```bash
# Step 1 - From GNU Radio Companion, run testing_connection.grc
# Step 2 - From terminal
python scripts/send_test.py
# Step 3 - Evaluate results
python scripts/parse_output.py

