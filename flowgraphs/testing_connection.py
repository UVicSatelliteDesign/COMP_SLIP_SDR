#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: degan
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
import pmt
from gnuradio import blocks, gr
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
import threading



class testing_connection(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "testing_connection")

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
        self.tcp_port = tcp_port = '52001'
        self.sync_word = sync_word = 0xD391C1E3
        self.rx_gain = rx_gain = 30
        self.preamble_byte = preamble_byte = 450
        self.payload_len = payload_len = 450
        self.mod_dev = mod_dev = 450
        self.host_ip_0 = host_ip_0 = '127.0.0.1'
        self.host_ip = host_ip = '127.0.0.1'
        self.frame_len = frame_len = 450
        self.crc_poly = crc_poly = 450

        ##################################################
        # Blocks
        ##################################################

        self.pdu_pdu_to_tagged_stream_0 = pdu.pdu_to_tagged_stream(gr.types.byte_t, 'packet_len')
        self.network_socket_pdu_0 = network.socket_pdu('TCP_SERVER', host_ip, tcp_port, 10000, False)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.cons(pmt.make_dict(), pmt.make_u8vector(4, ord('x')))
        , 1000)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)
        self.Output = blocks.file_sink(gr.sizeof_char*1, 'C:\\Users\\degan\\OneDrive\\Documents\\Work\\Projects\\UVSD\\Information\\raspiENV\\scripts\\output.txt', False)
        self.Output.set_unbuffered(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.network_socket_pdu_0, 'pdus'))
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.pdu_pdu_to_tagged_stream_0, 'pdus'))
        self.connect((self.pdu_pdu_to_tagged_stream_0, 0), (self.Output, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "testing_connection")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_tcp_port(self):
        return self.tcp_port

    def set_tcp_port(self, tcp_port):
        self.tcp_port = tcp_port

    def get_sync_word(self):
        return self.sync_word

    def set_sync_word(self, sync_word):
        self.sync_word = sync_word

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain

    def get_preamble_byte(self):
        return self.preamble_byte

    def set_preamble_byte(self, preamble_byte):
        self.preamble_byte = preamble_byte

    def get_payload_len(self):
        return self.payload_len

    def set_payload_len(self, payload_len):
        self.payload_len = payload_len

    def get_mod_dev(self):
        return self.mod_dev

    def set_mod_dev(self, mod_dev):
        self.mod_dev = mod_dev

    def get_host_ip_0(self):
        return self.host_ip_0

    def set_host_ip_0(self, host_ip_0):
        self.host_ip_0 = host_ip_0

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




def main(top_block_cls=testing_connection, options=None):

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
