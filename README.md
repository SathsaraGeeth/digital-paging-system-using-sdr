# Digital-Paging-System-Using-SDR

Two-way digital messaging system using Software Defined Radios (SDRs) for **EN2130 Communication Design Project**.  
Supports reliable text messaging with addressing, acknowledgments, and error detection.

---

## Features
- **Reliable messaging:** QPSK digital modulation  
- **Unique addressing** for each device  
- **Error detection:** CRC-based  
- **Error correction:** Stop-and-wait ARQ  
- **User interface:** Compose and send messages  
- **Security & priority:** AES128 encryption and priority-based handling  

---

## Implementation
- Written in **Python**
- Uses **deque** for queues, **threading** for ARQ state machine  
- Includes **AES encryption**, **CRC32 error detection**, and **ALOHA MAC**
- Testable between SDR devices (or simulation environment)
