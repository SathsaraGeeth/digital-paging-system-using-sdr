from gnuradio import gr
import pmt
from PyQt5 import QtWidgets, QtCore
from collections import deque
from datetime import datetime

ADDRESS_MAP = {"userA": 0x00, "userB": 0x01, "userC": 0x02}
NAME_MAP = {v: k for k, v in ADDRESS_MAP.items()}


class gui_io(gr.basic_block):
    """
    GUI Chat Window.
    """
    def __init__(self, my_name="userA"):
        gr.basic_block.__init__(self, name="Messages App", in_sig=[], out_sig=[])
        self.my_name = my_name
        self.tx_queue = deque()

        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_rx)
        self.message_port_register_out(pmt.intern("out"))

        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self.window = ChatWindow(self, self.tx_queue)
        self.window.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.process_tx)
        self.timer.start(50)

    def handle_rx(self, msg_pmt):
        if pmt.is_pair(msg_pmt):
            data = list(pmt.u8vector_elements(pmt.cdr(msg_pmt)))
            if len(data) < 3:
                return
            emergency = bool(data[0])
            src_addr = data[1]
            dst_addr = data[2]
            msg_bytes = data[3:]
            msg_str = bytes(msg_bytes).decode('utf-8', errors='ignore')
            src_name = NAME_MAP.get(src_addr, f"Unknown({src_addr})")
            dst_name = NAME_MAP.get(dst_addr, f"Unknown({dst_addr})")

            self.window.new_message_signal.emit(msg_str, emergency, src_name, dst_name)

    def process_tx(self):
        while self.tx_queue:
            msg, emergency, src, dst = self.tx_queue.popleft()
            dst_addr = ADDRESS_MAP.get(dst, 0xFF)
            data_list = [int(emergency), ADDRESS_MAP[self.my_name], dst_addr] + list(msg.encode('utf-8'))
            out_pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(data_list), data_list))
            self.message_port_pub(pmt.intern("out"), out_pdu)

    def stop(self):
        self.window.close()
        return True


class ChatWindow(QtWidgets.QWidget):
    new_message_signal = QtCore.pyqtSignal(str, bool, str, str)

    def __init__(self, block, tx_queue):
        super().__init__()
        self.block = block
        self.tx_queue = tx_queue

        self.new_message_signal.connect(self.add_message_bubble)

        self.setWindowTitle(f"Messages: {self.block.my_name}")
        self.setStyleSheet("background-color: #e6f0f8;")
        self.resize(700, 500)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { 
                border: 1px solid #c0c0c0; 
                border-radius: 8px; 
                background-color: #ffffff;
            }
        """)
        self.chat_container = QtWidgets.QWidget()
        self.chat_container.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        self.chat_layout = QtWidgets.QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch(1)
        self.scroll_area.setWidget(self.chat_container)
        self.layout.addWidget(self.scroll_area)

        input_group = QtWidgets.QFrame()
        input_group.setStyleSheet("""
            QFrame { 
                background-color: #f0f4f8; 
                border-radius: 8px; 
            }
        """)
        input_layout = QtWidgets.QHBoxLayout(input_group)
        input_layout.setContentsMargins(8, 5, 8, 5)
        input_layout.setSpacing(5)

        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setPlaceholderText("Text Message . ")
        self.input_line.setStyleSheet("padding: 5px; font-size: 12pt;")
        input_layout.addWidget(self.input_line, 3)

        self.dst_line = QtWidgets.QLineEdit()
        self.dst_line.setPlaceholderText("To")
        self.dst_line.setFixedWidth(120)
        self.dst_line.setStyleSheet("padding: 5px; font-size: 12pt;")
        input_layout.addWidget(self.dst_line, 1)

        self.emergency_checkbox = QtWidgets.QCheckBox("Emergency")
        self.emergency_checkbox.setStyleSheet("font-size: 11pt; padding: 3px;")
        input_layout.addWidget(self.emergency_checkbox)

        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton { 
                background-color: #4a90e2; 
                color: white; 
                font-size: 12pt; 
                padding: 6px 12px; 
                border-radius: 6px; 
            }
            QPushButton:hover { background-color: #357ab7; }
        """)
        input_layout.addWidget(self.send_button)

        self.layout.addWidget(input_group)

        self.send_button.clicked.connect(self.queue_message)
        self.input_line.returnPressed.connect(self.queue_message)

    def queue_message(self):
        msg = self.input_line.text()
        dst_name = self.dst_line.text()
        if msg and dst_name in ADDRESS_MAP:
            emergency_flag = self.emergency_checkbox.isChecked()
            self.tx_queue.append((msg, emergency_flag, self.block.my_name, dst_name))
            self.new_message_signal.emit(msg, emergency_flag, self.block.my_name, dst_name)
            self.input_line.clear()
            self.dst_line.clear()
            self.emergency_checkbox.setChecked(False)

    def add_message_bubble(self, msg, emergency, src, dst):
        bubble = QtWidgets.QFrame()
        bubble.setMaximumWidth(400)
        bubble_layout = QtWidgets.QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 8)
        bubble_layout.setSpacing(2)

        msg_label = QtWidgets.QLabel(msg)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 12pt;")
        bubble_layout.addWidget(msg_label)

        other_name = dst if src == self.block.my_name else src
        timestamp = datetime.now().strftime("%H:%M:%S")
        footer_label = QtWidgets.QLabel(f"{other_name} | {timestamp}")
        footer_label.setStyleSheet("font-size: 8pt; color: #555555;")
        bubble_layout.addWidget(footer_label)

        if emergency:
            bubble.setStyleSheet("background-color: #ffcccc; border-radius: 10px;")
        else:
            if src == self.block.my_name:
                bubble.setStyleSheet("background-color: #cce5ff; border-radius: 10px;")
            else:
                bubble.setStyleSheet("background-color: #d9f2d9; border-radius: 10px;")

        h_layout = QtWidgets.QHBoxLayout()
        if src == self.block.my_name:
            h_layout.addStretch()
            h_layout.addWidget(bubble)
        else:
            h_layout.addWidget(bubble)
            h_layout.addStretch()

        self.chat_layout.insertLayout(self.chat_layout.count()-1, h_layout)
        QtCore.QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()))