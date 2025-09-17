from gnuradio import gr
import pmt
from collections import deque
import threading
import time

class address_filter(gr.basic_block):
    """
    Address Filtering.
    - TX: Pass-through from upper layer to lower layer.
    - RX: Forward frames to upper layer only if dst_addr matches my_addr.
    - Frame format (PDU):
        meta: empty
        data: [msg_id, ack, emergency, src_addr, dst_addr, payload bytes (1024B)]
    """

    def __init__(self, my_addr=0):
        gr.basic_block.__init__(self, name="AddressFilter", in_sig=[], out_sig=[])

        self.my_addr = my_addr

        self.message_port_register_in(pmt.intern("in_tx"))
        self.set_msg_handler(pmt.intern("in_tx"), self.handle_in_tx)

        self.message_port_register_in(pmt.intern("in_rx"))
        self.set_msg_handler(pmt.intern("in_rx"), self.handle_in_rx)

        self.message_port_register_out(pmt.intern("out_tx"))
        self.message_port_register_out(pmt.intern("out_rx"))

        self.tx_queue = deque()
        self.rx_queue = deque()

        self.running = True
        self.tx_thread = threading.Thread(target=self.tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self.rx_loop, daemon=True)
        self.tx_thread.start()
        self.rx_thread.start()


    def handle_in_tx(self, pdu):
        if pmt.is_pair(pdu):
            self.tx_queue.append(pdu)

    def handle_in_rx(self, pdu):
        if pmt.is_pair(pdu):
            self.rx_queue.append(pdu)

    def tx_loop(self):
        while self.running:
            if self.tx_queue:
                pdu = self.tx_queue.popleft()
                self.message_port_pub(pmt.intern("out_tx"), pdu)
            else:
                time.sleep(0.01)

    def rx_loop(self):
        while self.running:
            if self.rx_queue:
                pdu = self.rx_queue.popleft()
                data = list(pmt.u8vector_elements(pmt.cdr(pdu)))
                if len(data) < 5:
                    continue
                dst_addr = data[4]
                if dst_addr == self.my_addr:
                    self.message_port_pub(pmt.intern("out_rx"), pdu)
            else:
                time.sleep(0.01)

    def stop(self):
        self.running = False
        self.tx_thread.join()
        self.rx_thread.join()
        return True