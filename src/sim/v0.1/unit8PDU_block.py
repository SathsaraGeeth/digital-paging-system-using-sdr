from gnuradio import gr
from PyQt5 import QtWidgets, QtCore
import sys
import numpy as np

class simple_uint8_probe(gr.basic_block):
    """
    UInt8 Stream Probe.
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="Tsu8 Probe",
            in_sig=[np.uint8],
            out_sig=[]
        )

        self.queue = []
        self.total_bytes = 0
        self.total_bits = 0


        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("UInt8 Probe")
        self.window.resize(400, 400)
        layout = QtWidgets.QVBoxLayout(self.window)
        self.display = QtWidgets.QTextEdit()
        self.display.setReadOnly(True)
        layout.addWidget(self.display)
        self.window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(50)

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        for val in in0:
            self.queue.append(val)
            self.total_bytes += 1
            self.total_bits += 8
        self.consume(0, len(in0))
        return 0

    def update_display(self):
        while self.queue:
            val = self.queue.pop(0)
            self.display.append(f"Value: {val} | Total Bytes: {self.total_bytes} | Total Bits: {self.total_bits}")