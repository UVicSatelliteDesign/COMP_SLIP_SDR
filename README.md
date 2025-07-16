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
| Network       | Python 'Tranceiver' class        |
| Transport     | Host-side logic in `main.py`     |

---


