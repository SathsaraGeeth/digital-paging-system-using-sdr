from collections import deque
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import zlib
import time
import threading
import sys



class Node:
    def __init__(self, ID, key, verbose = False): # key must be 16 bytes, ID 0-255
        self.ID = ID
        self.key = key
        
        # format [dest, src, payload]
        self.Uqueue_tx = deque()
        self.Uqueue_rx = deque()
        
        # format [CRC32, ACK?, num, dest, src, payload] num = SN or RN
        self.Lqueue_tx = deque()
        self.Lqueue_txACK = deque() # payload = None as we not doing piggybacking currently
        self.Lqueue_rx = deque()


        # FSM states for ARQ
        self.peerIDt = None
        self.peerIDr = None
        self.peers = {}
        self._packetinTX = None

        # MAC - ALOHA
        self.aloha_hold = None
        self.aloha_min = 0.01
        self.aloha_max = 0.2
        
        self._arq_thread = threading.Thread(target=self._StopWaitARQ, daemon=True)
        self._arq_thread.start()
        self._log = threading.Thread(target=self._log_loop, daemon=True) # deamon??
        if verbose: self._log.start()

    def enqueueMsgTX(self, dest, msg):    # dest/ID: int, msg: string
        encrypted = self._encrypt(msg)
        packet = [dest, self.ID] + list(encrypted)
        self.Uqueue_tx.append(packet)
    
    def dequeMsgRX(self):
        if self.Uqueue_rx:
            packet = self.Uqueue_rx.popleft()
            # dest = packet[0]
            src = packet[1]
            payload_bytes = bytes(packet[2:])
            decrypted_msg = self._decrypt(payload_bytes)
            return src, decrypted_msg # src, decrypted msg
            # return src, payload_bytes
        else:
            return None

    # Without MAC - multiple access control
##    def TXPacket(self):
##        if self.Lqueue_txACK:
##            return self.Lqueue_txACK.popleft()
##        elif self.Lqueue_tx:
##            return self.Lqueue_tx.popleft()
##        else:
##            return None

    # with MAC - ALOHA
    def TXPacket(self):
        if self.aloha_hold:
            pkt, t_send = self.aloha_hold
            if time.time() >= t_send:
                self.aloha_hold = None
                return pkt
            else:
                return None

        # ACK goes through
        if self.Lqueue_txACK:
            return self.Lqueue_txACK.popleft()

        # MSG transmitt with some random delay to reduce collisions
        if self.Lqueue_tx:
            pkt = self.Lqueue_tx.popleft()
            delay = random.uniform(self.aloha_min, self.aloha_max)
            t_send = time.time() + delay
            self.aloha_hold = (pkt, t_send)
            return None
        else:
            return None
    
        
        
    def RXPacket(self, packet):
        self.Lqueue_rx.append(packet)


    ########################### Helper Methods ###########################

    def _StopWaitARQ(self):
        done = True
        while True:
            # tx details
            if self.Uqueue_tx and done:
                self.packetinTX = self.Uqueue_tx.popleft()
                self.peerIDt = self.packetinTX[0]
                self._ensure_peer(self.peerIDt)
                done = False

            if self.peerIDt is not None and self.packetinTX:
                peer = self.peers[self.peerIDt]

                if peer["SNt"] == 0 or peer["RNt"] > peer["SNt"]:
                    self._packetinTX = self._appendCRC([0] + [peer["SNt"]] + self.packetinTX) # not an ACK, SN?
                    self.Lqueue_tx.append(self._packetinTX)
                    peer["timer"] = 0
                    peer["SNt"] += 1
                    done = True
                else:
                    ack_peer = None
                    if self.peerIDr is not None:
                        ack_peer = self.peers.get(self.peerIDr, None)
                    if ack_peer and ack_peer["ACKt"] == 111 and self.peerIDr == self.peerIDt:
                        self.Lqueue_tx.append(self._packetinTX)
                        peer["timer"] = 0
                    elif peer["timer"] > 5:
                        self.Lqueue_tx.append(self._packetinTX)
                        peer["timer"] = 0
                    else:
                        # wait for ACK and noop until timer runs out
                        peer["timer"] += 1

            # rx + ACK details
            if self.Lqueue_rx:
                _packetinRX = self.Lqueue_rx.popleft()
                src_peerID = _packetinRX[7]
                self._ensure_peer(src_peerID)
                self.peerIDr = src_peerID
                peer = self.peers[self.peerIDr]
                packetinRX = self._checkCRC(_packetinRX)
                if packetinRX:  # CRC pass?
                    peer["ACKt"] = packetinRX[0]
                    if peer["ACKt"] != 0:  # an ACK
                        peer["RNt"] = packetinRX[1]
                    else:  # a msg
                        peer["SNr"] = packetinRX[1]
                        if peer["SNr"] == peer["RNr"]:
                            peer["RNr"] += 1
                            self.Uqueue_rx.append(packetinRX[2:])
                            ACKpacket = self._appendCRC([1, peer["RNr"], self.peerIDr, self.ID])
                            self.Lqueue_txACK.append(ACKpacket)
                else:  # CRC fail; NACK
                    NACKpacket = self._appendCRC([111, peer["RNr"], self.peerIDr, self.ID])
                    self.Lqueue_txACK.append(NACKpacket)

            time.sleep(0.1)

    def _ensure_peer(self, peerID):
        if peerID not in self.peers:
            self.peers[peerID] = {
                "SNt": 0,
                "RNt": 0,
                "RNr": 0,
                "SNr": 0,
                "ACKt": 0,
                "packetinTX": None,
                "timer": 0
            }

    def _encrypt(self, msg):
        data = msg.encode('utf-8')
        pad_len = 16 - (len(data) % 16)
        padded = data + bytes([pad_len]) * pad_len
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(padded)

        return iv + ciphertext
    
    def _decrypt(self, encrypted_bytes):
        if isinstance(encrypted_bytes, list):
            encrypted_bytes = bytes(encrypted_bytes)

        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext)
        pad_len = padded_plaintext[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("Invalid padding")
        plaintext = padded_plaintext[:-pad_len]
        return plaintext.decode('utf-8')

    def _appendCRC(self, packet): # packet = [ack, num, dest, src, payload...]
        ack = packet[0]
        num = packet[1]
        dest = packet[2]
        src = packet[3]
        payload = packet[4:]
        payload_bytes = bytes(payload)
        data = bytes([ack, num, dest, src]) + payload_bytes
        crc = zlib.crc32(data)
        crc = [(crc >> 24) & 0xFF, (crc >> 16) & 0xFF, (crc >> 8) & 0xFF, crc & 0xFF]

        return crc + [ack, num, dest, src] + payload
    
    def _checkCRC(self, packet): # [CRC0, CRC1, CRC2, CRC3, ack, num, dest, src, payload...]
        crc_recv = ((packet[0] << 24) | (packet[1] << 16) | (packet[2] << 8) | packet[3])
        ack  = packet[4]
        num  = packet[5]
        dest = packet[6]
        src  = packet[7]
        payload = packet[8:]
        payload_bytes = bytes(payload)
        data = bytes([ack, num, dest, src]) + payload_bytes
        crc_calc = zlib.crc32(data)
        if crc_calc == crc_recv:
            return [ack, num, dest, src] + payload
        else:
            return False
    
    def _log_loop(self):
            while True:
                self.print_status()
                time.sleep(.01)

    def print_status(self):
        print(f"Node ID: {self.ID}")
        print(f"Uqueue_tx: {list(self.Uqueue_tx)}")
        print(f"Uqueue_rx: {list(self.Uqueue_rx)}")
        print(f"Lqueue_tx: {list(self.Lqueue_tx)}")
        print(f"Lqueue_txACK: {list(self.Lqueue_txACK)}")
        print(f"Lqueue_rx: {list(self.Lqueue_rx)}")
        print(f"peerIDt: {self.peerIDt}")
        print(f"peerIDr: {self.peerIDr}")
        print("peer States:", self.peers)
        print("--------------------------------------------------")
