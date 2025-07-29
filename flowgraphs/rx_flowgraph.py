#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
import pmt
from gnuradio import blocks, gr
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import gr, pdu
from gnuradio import network
from gnuradio import soapy
import satellites
import threading



class rx_flowgraph(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rx_flowgraph")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 450
        self.tcp_port = tcp_port = '52001'
        self.sync_word = sync_word = 1
        self.samp_rate = samp_rate = 30.72M
        self.preamble = preamble = 0b10101010
        self.payload_len = payload_len = 128
        self.host_ip = host_ip = '127.0.0.1'
        self.frame_len = frame_len = 450
        self.crc_poly = crc_poly = 0x8005
        self.center_freq = center_freq = 915e6
        self.RF_gain = RF_gain = 30
        self.K = K = 8
        self.Bandwith = Bandwith = 30.72M

        ##################################################
        # Blocks
        ##################################################

        self.soapy_limesdr_source_0 = None
        dev = 'driver=lime'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_limesdr_source_0 = soapy.source(dev, "fc32", 1, 'driver=lime',
                                  stream_args, tune_args, settings)
        self.soapy_limesdr_source_0.set_sample_rate(0, samp_rate)
        self.soapy_limesdr_source_0.set_bandwidth(0, Bandwith)
        self.soapy_limesdr_source_0.set_frequency(0, center_freq)
        self.soapy_limesdr_source_0.set_frequency_correction(0, 0)
        self.soapy_limesdr_source_0.set_gain(0, min(max(RF_gain, -12.0), 61.0))
        self.satellites_crc_check_0 = satellites.crc_check(16, crc_poly, 0xFFFFFFFF, 0xFFFFFFFF, True, True, False, False, 0)
        self.pdu_tagged_stream_to_pdu_0 = pdu.tagged_stream_to_pdu(gr.types.byte_t, 'packet_len')
        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.network_socket_pdu_0_0 = network.socket_pdu('TCP_SERVER', host_ip, tcp_port, 10000, False)
        self.network_socket_pdu_0 = network.socket_pdu('TCP_SERVER', '', '52001', 1500, False)
        self.digital_gfsk_demod_0 = digital.gfsk_demod(
            samples_per_symbol=4,
            sensitivity=1,
            gain_mu=0.175,
            mu=0.5,
            omega_relative_limit=0.005,
            freq_error=0.0,
            verbose=False,
            log=True)
        self.digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts('10101010',
          threshold, 'packet_len')
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(K)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_char*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_tagged_stream_align_0 = blocks.tagged_stream_align(gr.sizeof_char*1, 'packet_len')
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(K)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.cons(pmt.make_dict(), pmt.make_u8vector(4, ord('x')))
        , 1000)
        self.blocks_message_debug_0_0 = blocks.message_debug(True, gr.log_levels.err)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)
        self.Output = blocks.file_sink(gr.sizeof_char*1, 'C:\\Users\\degan\\OneDrive\\Documents\\Work\\Projects\\UVSD\\Information\\raspiENV\\scripts\\output.txt', False)
        self.Output.set_unbuffered(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.network_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.blocks_message_debug_0, 'print_pdu'))
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.pdu_tagged_stream_to_pdu_0, 'pdus'), (self.satellites_crc_check_0, 'in'))
        self.msg_connect((self.satellites_crc_check_0, 'fail'), (self.blocks_message_debug_0_0, 'log'))
        self.msg_connect((self.satellites_crc_check_0, 'ok'), (self.network_socket_pdu_0, 'pdus'))
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_tagged_stream_align_0, 0))
        self.connect((self.blocks_tagged_stream_align_0, 0), (self.pdu_tagged_stream_to_pdu_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.digital_correlate_access_code_xx_ts_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.digital_gfsk_demod_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.Output, 0))
        self.connect((self.soapy_limesdr_source_0, 0), (self.digital_gfsk_demod_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "rx_flowgraph")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_tcp_port(self):
        return self.tcp_port

    def set_tcp_port(self, tcp_port):
        self.tcp_port = tcp_port

    def get_sync_word(self):
        return self.sync_word

    def set_sync_word(self, sync_word):
        self.sync_word = sync_word

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.soapy_limesdr_source_0.set_sample_rate(0, self.samp_rate)

    def get_preamble(self):
        return self.preamble

    def set_preamble(self, preamble):
        self.preamble = preamble

    def get_payload_len(self):
        return self.payload_len

    def set_payload_len(self, payload_len):
        self.payload_len = payload_len

    def get_host_ip(self):
        return self.host_ip

    def set_host_ip(self, host_ip):
        self.host_ip = host_ip

    def get_frame_len(self):
        return self.frame_len

    def set_frame_len(self, frame_len):
        self.frame_len = frame_len

    def get_crc_poly(self):
        return self.crc_poly

    def set_crc_poly(self, crc_poly):
        self.crc_poly = crc_poly

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.soapy_limesdr_source_0.set_frequency(0, self.center_freq)

    def get_RF_gain(self):
        return self.RF_gain

    def set_RF_gain(self, RF_gain):
        self.RF_gain = RF_gain
        self.soapy_limesdr_source_0.set_gain(0, min(max(self.RF_gain, -12.0), 61.0))

    def get_K(self):
        return self.K

    def set_K(self, K):
        self.K = K

    def get_Bandwith(self):
        return self.Bandwith

    def set_Bandwith(self, Bandwith):
        self.Bandwith = Bandwith
        self.soapy_limesdr_source_0.set_bandwidth(0, self.Bandwith)




def main(top_block_cls=rx_flowgraph, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

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
