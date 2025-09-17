# Digital-Paging-System-Using-SDR

Here we implement a two-way digital messaging system using Software Defined Radios (SDRs).  
The system allows short text messages to be sent and received between devices with proper addressing, acknowledgment, and error detection mechanisms.

## Features
- Reliable message delivery using digital modulation QPSK.
- Unique addressing for each receiver and transmitter.
- CRC-based error detection to discard corrupted messages.
- Stop and wait ARQ scheme for error correction.
- Basic user interface to compose and send messages.
- AES128 encryption, priority-based message handling.
