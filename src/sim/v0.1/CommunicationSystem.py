#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: CDP
# Author: Geeth Sathsara
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import digital
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
import CommunicationSystem_epy_block_0 as epy_block_0  # embedded python block
import CommunicationSystem_epy_block_0_0 as epy_block_0_0  # embedded python block
import CommunicationSystem_epy_block_1 as epy_block_1  # embedded python block
import CommunicationSystem_epy_block_1_0 as epy_block_1_0  # embedded python block
import CommunicationSystem_epy_block_2 as epy_block_2  # embedded python block
import CommunicationSystem_epy_block_2_0 as epy_block_2_0  # embedded python block
import CommunicationSystem_epy_block_4 as epy_block_4  # embedded python block
import CommunicationSystem_epy_block_4_0 as epy_block_4_0  # embedded python block
import CommunicationSystem_epy_block_7 as epy_block_7  # embedded python block
import CommunicationSystem_epy_block_7_0 as epy_block_7_0  # embedded python block
import CommunicationSystem_epy_block_8 as epy_block_8  # embedded python block
import CommunicationSystem_epy_block_8_0 as epy_block_8_0  # embedded python block



class CommunicationSystem(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "CDP", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("CDP")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "CommunicationSystem")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 4
        self.qpsk = qpsk = digital.constellation_rect([0.707+0.707j, -0.707+0.707j, -0.707-0.707j, 0.707-0.707j], [0, 1, 2, 3],
        4, 2, 2, 1, 1).base()
        self.nfilts = nfilts = 32
        self.access_key = access_key = '11100001010110101110100010010011'
        self.variable_adaptive_algorithm_0 = variable_adaptive_algorithm_0 = digital.adaptive_algorithm_cma( qpsk, .0001, 4).base()
        self.time_offset = time_offset = 1
        self.thresh = thresh = 1
        self.samp_rate = samp_rate = 48000
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(nfilts, nfilts, 1.0/float(sps), 0.35, 11*sps*nfilts)
        self.phase_bw = phase_bw = 0.0628
        self.noise_volt = noise_volt = 0
        self.hdr_format = hdr_format = digital.header_format_default(access_key, 0)
        self.freq_offset = freq_offset = 0
        self.excess_bw = excess_bw = 0.35
        self.delay = delay = 50

        ##################################################
        # Blocks
        ##################################################

        self.pdu_tagged_stream_to_pdu_0_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.pdu_tagged_stream_to_pdu_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_0_1 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_0_0_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_0_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.epy_block_8_0 = epy_block_8_0.crc_block()
        self.epy_block_8 = epy_block_8.crc_block()
        self.epy_block_7_0 = epy_block_7_0.address_filter_block(my_addr=0x01)
        self.epy_block_7 = epy_block_7.address_filter_block(my_addr=0x00)
        self.epy_block_4_0 = epy_block_4_0.ARQ(retransmit_delay=0.2, max_retries=50)
        self.epy_block_4 = epy_block_4.ARQ(retransmit_delay=0.2, max_retries=50)
        self.epy_block_2_0 = epy_block_2_0.msgQueue()
        self.epy_block_2 = epy_block_2.msgQueue()
        self.epy_block_1_0 = epy_block_1_0.aes128_block(key=b'mysecretkey12345' )
        self.epy_block_1 = epy_block_1.aes128_block(key=b'mysecretkey12345' )
        self.epy_block_0_0 = epy_block_0_0.gui_io(my_name="userB")
        self.epy_block_0 = epy_block_0.gui_io(my_name="userA")
        self.digital_protocol_formatter_async_0_0 = digital.protocol_formatter_async(hdr_format)
        self.digital_protocol_formatter_async_0 = digital.protocol_formatter_async(hdr_format)
        self.digital_pfb_clock_sync_xxx_0_0 = digital.pfb_clock_sync_ccf(sps, phase_bw, rrc_taps, nfilts, (nfilts/2), 1.5, 2)
        self.digital_pfb_clock_sync_xxx_0 = digital.pfb_clock_sync_ccf(sps, phase_bw, rrc_taps, nfilts, (nfilts/2), 1.5, 2)
        self.digital_map_bb_0_0 = digital.map_bb([0,1,2,3])
        self.digital_map_bb_0 = digital.map_bb([0,1,2,3])
        self.digital_linear_equalizer_0_0 = digital.linear_equalizer(15, 2, variable_adaptive_algorithm_0, True, [ ], 'corr_est')
        self.digital_linear_equalizer_0 = digital.linear_equalizer(15, 2, variable_adaptive_algorithm_0, True, [ ], 'corr_est')
        self.digital_diff_decoder_bb_0_0 = digital.diff_decoder_bb(4, digital.DIFF_DIFFERENTIAL)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(4, digital.DIFF_DIFFERENTIAL)
        self.digital_costas_loop_cc_0_0 = digital.costas_loop_cc(phase_bw, 4, False)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(phase_bw, 4, False)
        self.digital_correlate_access_code_xx_ts_0_0 = digital.correlate_access_code_bb_ts("11100001010110101110100010010011",
          thresh, 'packet_len')
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts("11100001010110101110100010010011",
          thresh, 'packet_len')
        self.digital_constellation_modulator_0_0 = digital.generic_mod(
            constellation=qpsk,
            differential=True,
            samples_per_symbol=sps,
            pre_diff_code=True,
            excess_bw=excess_bw,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=qpsk,
            differential=True,
            samples_per_symbol=sps,
            pre_diff_code=True,
            excess_bw=excess_bw,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_decoder_cb_0_0 = digital.constellation_decoder_cb(qpsk)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(qpsk)
        self.channels_channel_model_0_0 = channels.channel_model(
            noise_voltage=noise_volt,
            frequency_offset=freq_offset,
            epsilon=time_offset,
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=noise_volt,
            frequency_offset=freq_offset,
            epsilon=time_offset,
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.blocks_unpack_k_bits_bb_0_0 = blocks.unpack_k_bits_bb(2)
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(2)
        self.blocks_tagged_stream_mux_0_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_repack_bits_bb_1_0_0_0 = blocks.repack_bits_bb(1, 8, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_1_0_0 = blocks.repack_bits_bb(1, 8, "packet_len", False, gr.GR_MSB_FIRST)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.digital_protocol_formatter_async_0, 'header'), (self.pdu_pdu_to_tagged_stream_0_0, 'pdus'))
        self.msg_connect((self.digital_protocol_formatter_async_0, 'payload'), (self.pdu_pdu_to_tagged_stream_0_0_0, 'pdus'))
        self.msg_connect((self.digital_protocol_formatter_async_0_0, 'payload'), (self.pdu_pdu_to_tagged_stream_0_0_0_0, 'pdus'))
        self.msg_connect((self.digital_protocol_formatter_async_0_0, 'header'), (self.pdu_pdu_to_tagged_stream_0_0_1, 'pdus'))
        self.msg_connect((self.epy_block_0, 'out'), (self.epy_block_1, 'in_tx'))
        self.msg_connect((self.epy_block_0_0, 'out'), (self.epy_block_1_0, 'in_tx'))
        self.msg_connect((self.epy_block_1, 'out_rx'), (self.epy_block_0, 'in'))
        self.msg_connect((self.epy_block_1, 'out_tx'), (self.epy_block_2, 'in_tx'))
        self.msg_connect((self.epy_block_1_0, 'out_rx'), (self.epy_block_0_0, 'in'))
        self.msg_connect((self.epy_block_1_0, 'out_tx'), (self.epy_block_2_0, 'in_tx'))
        self.msg_connect((self.epy_block_2, 'out_rx'), (self.epy_block_1, 'in_rx'))
        self.msg_connect((self.epy_block_2, 'out_tx'), (self.epy_block_4, 'in_tx'))
        self.msg_connect((self.epy_block_2_0, 'out_rx'), (self.epy_block_1_0, 'in_rx'))
        self.msg_connect((self.epy_block_2_0, 'out_tx'), (self.epy_block_4_0, 'in_tx'))
        self.msg_connect((self.epy_block_4, 'out_rx'), (self.epy_block_2, 'in_rx'))
        self.msg_connect((self.epy_block_4, 'out_tx'), (self.epy_block_7, 'in_tx'))
        self.msg_connect((self.epy_block_4_0, 'out_rx'), (self.epy_block_2_0, 'in_rx'))
        self.msg_connect((self.epy_block_4_0, 'out_tx'), (self.epy_block_7_0, 'in_tx'))
        self.msg_connect((self.epy_block_7, 'out_rx'), (self.epy_block_4, 'in_rx'))
        self.msg_connect((self.epy_block_7, 'out_tx'), (self.epy_block_8, 'in_tx'))
        self.msg_connect((self.epy_block_7_0, 'out_rx'), (self.epy_block_4_0, 'in_rx'))
        self.msg_connect((self.epy_block_7_0, 'out_tx'), (self.epy_block_8_0, 'in_tx'))
        self.msg_connect((self.epy_block_8, 'out_tx'), (self.digital_protocol_formatter_async_0, 'in'))
        self.msg_connect((self.epy_block_8, 'out_rx'), (self.epy_block_7, 'in_rx'))
        self.msg_connect((self.epy_block_8_0, 'out_tx'), (self.digital_protocol_formatter_async_0_0, 'in'))
        self.msg_connect((self.epy_block_8_0, 'out_rx'), (self.epy_block_7_0, 'in_rx'))
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0, 'pdus'), (self.epy_block_8, 'in_rx'))
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0_0, 'pdus'), (self.epy_block_8_0, 'in_rx'))
        self.connect((self.blocks_repack_bits_bb_1_0_0, 0), (self.pdu_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_repack_bits_bb_1_0_0_0, 0), (self.pdu_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.blocks_tagged_stream_mux_0_0, 0), (self.digital_constellation_modulator_0_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0_0, 0), (self.digital_correlate_access_code_xx_ts_0_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.digital_pfb_clock_sync_xxx_0_0, 0))
        self.connect((self.channels_channel_model_0_0, 0), (self.digital_pfb_clock_sync_xxx_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0_0, 0), (self.digital_diff_decoder_bb_0_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.digital_constellation_modulator_0_0, 0), (self.channels_channel_model_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_repack_bits_bb_1_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0_0, 0), (self.blocks_repack_bits_bb_1_0_0_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0, 0), (self.digital_constellation_decoder_cb_0_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.digital_map_bb_0, 0))
        self.connect((self.digital_diff_decoder_bb_0_0, 0), (self.digital_map_bb_0_0, 0))
        self.connect((self.digital_linear_equalizer_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self.digital_linear_equalizer_0_0, 0), (self.digital_costas_loop_cc_0_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.digital_map_bb_0_0, 0), (self.blocks_unpack_k_bits_bb_0_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.digital_linear_equalizer_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0_0, 0), (self.digital_linear_equalizer_0_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0_0_0, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.pdu_pdu_to_tagged_stream_0_0_0_0, 0), (self.blocks_tagged_stream_mux_0_0, 1))
        self.connect((self.pdu_pdu_to_tagged_stream_0_0_1, 0), (self.blocks_tagged_stream_mux_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "CommunicationSystem")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), 0.35, 11*self.sps*self.nfilts))

    def get_qpsk(self):
        return self.qpsk

    def set_qpsk(self, qpsk):
        self.qpsk = qpsk
        self.digital_constellation_decoder_cb_0.set_constellation(self.qpsk)
        self.digital_constellation_decoder_cb_0_0.set_constellation(self.qpsk)

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), 0.35, 11*self.sps*self.nfilts))

    def get_access_key(self):
        return self.access_key

    def set_access_key(self, access_key):
        self.access_key = access_key
        self.set_hdr_format(digital.header_format_default(self.access_key, 0))

    def get_variable_adaptive_algorithm_0(self):
        return self.variable_adaptive_algorithm_0

    def set_variable_adaptive_algorithm_0(self, variable_adaptive_algorithm_0):
        self.variable_adaptive_algorithm_0 = variable_adaptive_algorithm_0

    def get_time_offset(self):
        return self.time_offset

    def set_time_offset(self, time_offset):
        self.time_offset = time_offset
        self.channels_channel_model_0.set_timing_offset(self.time_offset)
        self.channels_channel_model_0_0.set_timing_offset(self.time_offset)

    def get_thresh(self):
        return self.thresh

    def set_thresh(self, thresh):
        self.thresh = thresh

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.digital_pfb_clock_sync_xxx_0.update_taps(self.rrc_taps)
        self.digital_pfb_clock_sync_xxx_0_0.update_taps(self.rrc_taps)

    def get_phase_bw(self):
        return self.phase_bw

    def set_phase_bw(self, phase_bw):
        self.phase_bw = phase_bw
        self.digital_costas_loop_cc_0.set_loop_bandwidth(self.phase_bw)
        self.digital_costas_loop_cc_0_0.set_loop_bandwidth(self.phase_bw)
        self.digital_pfb_clock_sync_xxx_0.set_loop_bandwidth(self.phase_bw)
        self.digital_pfb_clock_sync_xxx_0_0.set_loop_bandwidth(self.phase_bw)

    def get_noise_volt(self):
        return self.noise_volt

    def set_noise_volt(self, noise_volt):
        self.noise_volt = noise_volt
        self.channels_channel_model_0.set_noise_voltage(self.noise_volt)
        self.channels_channel_model_0_0.set_noise_voltage(self.noise_volt)

    def get_hdr_format(self):
        return self.hdr_format

    def set_hdr_format(self, hdr_format):
        self.hdr_format = hdr_format

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.channels_channel_model_0.set_frequency_offset(self.freq_offset)
        self.channels_channel_model_0_0.set_frequency_offset(self.freq_offset)

    def get_excess_bw(self):
        return self.excess_bw

    def set_excess_bw(self, excess_bw):
        self.excess_bw = excess_bw

    def get_delay(self):
        return self.delay

    def set_delay(self, delay):
        self.delay = delay




def main(top_block_cls=CommunicationSystem, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
