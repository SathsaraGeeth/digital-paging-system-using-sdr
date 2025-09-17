from gnuradio import gr
import pmt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import threading
from collections import deque

class aes128_block(gr.basic_block):
    """
    AES-128 Encrypt/Decrypt.

    Input TX:  PDU = pmt.cons(meta, data)
        meta: empty
        data: pmt.u8vector [emergency(1B), src_addr(1B), dst_addr(1B), plaintext message bytes]
    Output TX: PDU with encrypted payload (IV + ciphertext), first 3 bytes unchanged

    Input RX:  PDU with encrypted payload
    Output RX: PDU with decrypted payload, first 3 bytes unchanged
    """

    def __init__(self, key=b'0123456789abcdef'):
        gr.basic_block.__init__(self, name="Encrypt/Decrypt", in_sig=[], out_sig=[])

        self.message_port_register_in(pmt.intern("in_tx"))
        self.set_msg_handler(pmt.intern("in_tx"), self.handle_tx)
        self.message_port_register_in(pmt.intern("in_rx"))
        self.set_msg_handler(pmt.intern("in_rx"), self.handle_rx)
        self.message_port_register_out(pmt.intern("out_tx"))
        self.message_port_register_out(pmt.intern("out_rx"))

        if len(key) != 16:
            raise ValueError("AES-128 requires 16-byte key")
        self.key = key

        self.tx_queue = deque()
        self.rx_queue = deque()

        self.running = True
        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)
        self.tx_thread.start()
        self.rx_thread.start()

    def handle_tx(self, msg_pmt):
        if pmt.is_pair(msg_pmt):
            self.tx_queue.append(msg_pmt)

    def handle_rx(self, msg_pmt):
        if pmt.is_pair(msg_pmt):
            self.rx_queue.append(msg_pmt)

    def tx_loop(self):
        while self.running:
            if self.tx_queue:
                msg_pdu = self.tx_queue.popleft()
                data_pmt = pmt.cdr(msg_pdu)
                if pmt.is_u8vector(data_pmt):
                    data_bytes = list(pmt.u8vector_elements(data_pmt))
                    if len(data_bytes) < 3:
                        continue
                    header = data_bytes[:3]
                    payload = data_bytes[3:]

                    cipher = AES.new(self.key, AES.MODE_CBC)
                    ct_bytes = cipher.iv + cipher.encrypt(pad(bytes(payload), AES.block_size))

                    out_bytes = header + list(ct_bytes)
                    out_pmt = pmt.init_u8vector(len(out_bytes), out_bytes)
                    out_pdu = pmt.cons(pmt.make_dict(), out_pmt)
                    self.message_port_pub(pmt.intern("out_tx"), out_pdu)
            else:
                threading.Event().wait(0.01)

    def rx_loop(self):
        while self.running:
            if self.rx_queue:
                msg_pdu = self.rx_queue.popleft()
                data_pmt = pmt.cdr(msg_pdu)
                if pmt.is_u8vector(data_pmt):
                    data_bytes = list(pmt.u8vector_elements(data_pmt))
                    if len(data_bytes) < 3 + 16:  # header + IV
                        continue
                    header = data_bytes[:3]
                    ct_bytes = bytes(data_bytes[3:])
                    iv = ct_bytes[:16]
                    ct = ct_bytes[16:]
                    cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
                    try:
                        pt_bytes = unpad(cipher.decrypt(ct), AES.block_size)
                        out_bytes = header + list(pt_bytes)
                        out_pmt = pmt.init_u8vector(len(out_bytes), out_bytes)
                        out_pdu = pmt.cons(pmt.make_dict(), out_pmt)
                        self.message_port_pub(pmt.intern("out_rx"), out_pdu)
                    except ValueError:
                        continue
            else:
                threading.Event().wait(0.01)

    def stop(self):
        self.running = False
        self.tx_thread.join()
        self.rx_thread.join()
        return True