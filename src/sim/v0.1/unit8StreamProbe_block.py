from gnuradio import gr
import pmt
from PyQt5 import QtWidgets, QtCore
import sys

class pdu_probe_qt(gr.basic_block):
    """
    PDU unit8 Probe.
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="PDU-u8 Probe",
            in_sig=[],
            out_sig=[]
        )
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_rx)
        self.pdu_queue = []

        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("PDU Probe")
        self.window.resize(800, 600)
        self.layout = QtWidgets.QVBoxLayout(self.window)
        self.display = QtWidgets.QTextEdit()
        self.display.setReadOnly(True)
        self.layout.addWidget(self.display)
        self.window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(50)

    def handle_rx(self, pdu_msg):
        if pmt.is_pair(pdu_msg):
            self.pdu_queue.append(pdu_msg)

    def update_display(self):
        while self.pdu_queue:
            pdu_msg = self.pdu_queue.pop(0)
            meta = pmt.car(pdu_msg)
            data = pmt.cdr(pdu_msg)

            if meta == pmt.PMT_NIL:
                meta_str = "None"
            else:
                meta_str = str(meta)

            if data == pmt.PMT_NIL:
                data_str = "None"
            elif pmt.is_u8vector(data):
                data_str = str(list(pmt.u8vector_elements(data)))
            elif pmt.is_c32vector(data):
                data_str = str(list(pmt.c32vector_elements(data)))
            else:
                data_str = str(data)

            self.display.append(f"Meta: {meta_str}\nData: {data_str}\n{'-'*60}")