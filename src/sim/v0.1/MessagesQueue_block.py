from gnuradio import gr
import pmt
import threading
from collections import deque
import time

class msgQueue(gr.basic_block):
    """
    Message Queue Block with Priority Handling.
    PDU format:
        meta: empty
        data (pmt.u8vector):
            [emergency(1B), src_addr(1B), dst_addr(1B), message payload bytes]
    """

    def __init__(self):
        gr.basic_block.__init__(self, name="MsgQueue", in_sig=[], out_sig=[])

        self.message_port_register_in(pmt.intern("in_tx"))
        self.set_msg_handler(pmt.intern("in_tx"), self.handle_in_tx)
        self.message_port_register_in(pmt.intern("in_rx"))
        self.set_msg_handler(pmt.intern("in_rx"), self.handle_in_rx)

        self.message_port_register_out(pmt.intern("out_tx"))
        self.message_port_register_out(pmt.intern("out_rx"))

        self.tx_emergency = deque()
        self.tx_normal = deque()
        self.rx_emergency = deque()
        self.rx_normal = deque()

        self.running = True
        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)
        self.tx_thread.start()
        self.rx_thread.start()

    def handle_in_tx(self, msg_pmt):
        if pmt.is_pair(msg_pmt):
            data_pmt = pmt.cdr(msg_pmt)
            if pmt.is_u8vector(data_pmt) and len(pmt.u8vector_elements(data_pmt)) >= 3:
                emergency_flag = bool(pmt.u8vector_elements(data_pmt)[0])
                if emergency_flag:
                    self.tx_emergency.append(msg_pmt)
                else:
                    self.tx_normal.append(msg_pmt)

    def handle_in_rx(self, msg_pmt):
        if pmt.is_pair(msg_pmt):
            data_pmt = pmt.cdr(msg_pmt)
            if pmt.is_u8vector(data_pmt) and len(pmt.u8vector_elements(data_pmt)) >= 3:
                emergency_flag = bool(pmt.u8vector_elements(data_pmt)[0])
                if emergency_flag:
                    self.rx_emergency.append(msg_pmt)
                else:
                    self.rx_normal.append(msg_pmt)

    def tx_loop(self):
        while self.running:
            msg = None
            if self.tx_emergency:
                msg = self.tx_emergency.popleft()
            elif self.tx_normal:
                msg = self.tx_normal.popleft()

            if msg is not None:
                out_pdu = pmt.cons(pmt.make_dict(), pmt.cdr(msg))
                self.message_port_pub(pmt.intern("out_tx"), out_pdu)
            else:
                time.sleep(0.01)

    def rx_loop(self):
        while self.running:
            msg = None
            if self.rx_emergency:
                msg = self.rx_emergency.popleft()
            elif self.rx_normal:
                msg = self.rx_normal.popleft()

            if msg is not None:
                out_pdu = pmt.cons(pmt.make_dict(), pmt.cdr(msg))
                self.message_port_pub(pmt.intern("out_rx"), out_pdu)
            else:
                time.sleep(0.01)

    def stop(self):
        self.running = False
        self.tx_thread.join()
        self.rx_thread.join()
        return True