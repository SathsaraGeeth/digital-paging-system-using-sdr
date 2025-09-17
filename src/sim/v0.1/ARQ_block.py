from gnuradio import gr
import pmt
import threading
from collections import deque
import time

class ARQ(gr.basic_block):
    """
    ARQ Transport Layer.
    Stop-and-Wait ARQ with msg_id, ACKs, and emergency prioritization.

    Upper layer PDU:
        meta: empty
        data: [emergency(1B), src_addr(1B), dst_addr(1B), payload bytes]

    Lower layer PDU:
        meta: empty
        data: [msg_id(1B), ack(1B), emergency(1B), src_addr(1B), dst_addr(1B), payload bytes (fixed 1024B)]
    """
    def __init__(self, retransmit_delay=0.2, max_retries=5):
        gr.basic_block.__init__(self, name="Framing & ARQ", in_sig=[], out_sig=[])

        self.payload_len = 1024
        self.retransmit_delay = retransmit_delay
        self.max_retries = max_retries

        self.message_port_register_in(pmt.intern("in_tx"))
        self.set_msg_handler(pmt.intern("in_tx"), self.handle_in_tx)
        self.message_port_register_in(pmt.intern("in_rx"))
        self.set_msg_handler(pmt.intern("in_rx"), self.handle_in_rx)
        self.message_port_register_out(pmt.intern("out_tx"))
        self.message_port_register_out(pmt.intern("out_rx"))

        self.tx_emergency = deque()
        self.tx_normal = deque()
        self.rx_queue = deque()

        self.pending_ack = {} 
        self.next_msg_id = 0

        self.last_delivered = {}

        self.running = True
        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)
        self.tx_thread.start()
        self.rx_thread.start()

    def handle_in_tx(self, pdu):
        if pmt.is_pair(pdu):
            data = list(pmt.u8vector_elements(pmt.cdr(pdu)))
            emergency = bool(data[0])
            if emergency:
                self.tx_emergency.append(pdu)
            else:
                self.tx_normal.append(pdu)

    def handle_in_rx(self, pdu):
        if pmt.is_pair(pdu):
            self.rx_queue.append(pdu)

    def tx_loop(self):
        while self.running:
            pdu = None
            if self.tx_emergency:
                pdu = self.tx_emergency.popleft()
            elif self.tx_normal:
                pdu = self.tx_normal.popleft()

            if pdu:
                data = list(pmt.u8vector_elements(pmt.cdr(pdu)))
                emergency, src, dst = data[:3]
                payload = data[3:]

                if len(payload) < self.payload_len:
                    payload += [0]*(self.payload_len - len(payload))
                elif len(payload) > self.payload_len:
                    payload = payload[:self.payload_len]

                msg_id = self.next_msg_id
                self.next_msg_id = (self.next_msg_id + 1) % 256

                lower_data = [msg_id, 0, emergency, src, dst] + payload
                lower_pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(lower_data), lower_data))

                self.pending_ack[msg_id] = (lower_pdu, time.time(), 1)
                self.message_port_pub(pmt.intern("out_tx"), lower_pdu)

            now = time.time()
            to_remove = []
            for mid, (frame, ts, retries) in self.pending_ack.items():
                if now - ts > self.retransmit_delay:
                    if retries >= self.max_retries:
                        to_remove.append(mid)
                    else:
                        self.pending_ack[mid] = (frame, now, retries+1)
                        self.message_port_pub(pmt.intern("out_tx"), frame)
            for mid in to_remove:
                del self.pending_ack[mid]

            time.sleep(0.01)

    def rx_loop(self):
        while self.running:
            if self.rx_queue:
                pdu = self.rx_queue.popleft()
                data = list(pmt.u8vector_elements(pmt.cdr(pdu)))
                if len(data) < 5:
                    continue
                msg_id, ack_flag, emergency, src, dst = data[:5]
                payload = data[5:]

                if ack_flag:
                    if msg_id in self.pending_ack:
                        del self.pending_ack[msg_id]
                    continue

                ack_data = [msg_id, 1, emergency, src, dst] + [0]*self.payload_len
                ack_pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(ack_data), ack_data))
                self.message_port_pub(pmt.intern("out_tx"), ack_pdu)

                key = (src, dst)
                if self.last_delivered.get(key) != msg_id:
                    self.last_delivered[key] = msg_id
                    payload_stripped = [b for b in payload if b != 0]
                    upper_data = [emergency, src, dst] + payload_stripped
                    upper_pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(upper_data), upper_data))
                    self.message_port_pub(pmt.intern("out_rx"), upper_pdu)
            else:
                time.sleep(0.01)

    def stop(self):
        self.running = False
        self.tx_thread.join()
        self.rx_thread.join()
        return True