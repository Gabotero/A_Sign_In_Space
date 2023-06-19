#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: A Sign in Space
# Author: Gabriel Otero Pérez
# Description: Demodulation of TGO message
# GNU Radio version: 3.8.2.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
import pmt
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from math import pi
import dslwp
import numpy as np
import satellites.hier

from gnuradio import qtgui

class Demod(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "A Sign in Space")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("A Sign in Space")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
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

        self.settings = Qt.QSettings("GNU Radio", "Demod")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.syncword_hex = syncword_hex = '034776C7272895B0'
        self.syncword_bits = syncword_bits = 2*np.unpackbits(np.frombuffer(bytes.fromhex(syncword_hex), dtype = 'uint8')).astype('int')-1
        self.samp_rate = samp_rate = 1e6
        self.baudrate = baudrate = 52600
        self.syncword_string = syncword_string = ''.join([str(i) for i in (syncword_bits+1)//2])
        self.subcarrier_freq = subcarrier_freq = 200000+63148
        self.samples_per_symbol = samples_per_symbol = samp_rate/baudrate
        self.PLL_Limit_Hz = PLL_Limit_Hz = 100000
        self.PLL_BW_Hz = PLL_BW_Hz = 500

        ##################################################
        # Blocks
        ##################################################
        self.satellites_rms_agc_0 = satellites.hier.rms_agc(alpha=1e-5, reference=1.0)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            100000, #size
            baudrate, #samp_rate
            "", #name
            2 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Samples', 'Correlation value', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [0, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [0, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Visualizing the specturm", #name
            2
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)



        labels = ['Before PLL', 'After PLL', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "BPSK Constellation", #name
            1 #number of inputs
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.hilbert_fc_0 = filter.hilbert_fc(65, firdes.WIN_HAMMING, 6.76)
        self.fir_filter_xxx_1 = filter.fir_filter_fff(1, syncword_bits[::-1]/syncword_bits.size)
        self.fir_filter_xxx_1.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_ccc(1, np.ones(19)/19/1.25)
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.dslwp_frame_spliter_f_0_0 = dslwp.frame_spliter_f('sync_marker', 17848)
        self.dslwp_frame_spliter_f_0 = dslwp.frame_spliter_f('sync_marker', 17848)
        self.dslwp_ccsds_turbo_decode_0 = dslwp.ccsds_turbo_decode(223, 5, 2, 2, 0.707, 1)
        self.dslwp_ccsds_pseudo_randomizer_0 = dslwp.ccsds_pseudo_randomizer(3)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_GARDNER,
            samples_per_symbol,
            0.01,
            1.0,
            1.0,
            0.01,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(0.001, 2, False)
        self.digital_correlate_access_code_tag_xx_0_0 = digital.correlate_access_code_tag_ff(syncword_string, 4, 'sync_marker')
        self.digital_correlate_access_code_tag_xx_0 = digital.correlate_access_code_tag_ff(syncword_string, 4, 'sync_marker')
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_float*1, '', "sync_marker")
        self.blocks_tag_debug_0.set_display(True)
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(-1)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_interleaved_char_to_complex_0 = blocks.interleaved_char_to_complex(False)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, '/home/gnuradio/Desktop/A_Sign_in_Space/recording/A_Sign_in_Space-GBT.sigmf-data', False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_imag_0 = blocks.complex_to_imag(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, subcarrier_freq, 1, 0, 0)
        self.analog_pll_carriertracking_cc_0 = analog.pll_carriertracking_cc(PLL_BW_Hz * 2 * pi / samp_rate, PLL_Limit_Hz * 2 * pi / samp_rate, -PLL_Limit_Hz * 2 * pi / samp_rate)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.dslwp_ccsds_pseudo_randomizer_0, 'out'), (self.dslwp_ccsds_turbo_decode_0, 'in'))
        self.msg_connect((self.dslwp_ccsds_turbo_decode_0, 'out'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.dslwp_frame_spliter_f_0, 'out'), (self.dslwp_ccsds_pseudo_randomizer_0, 'in'))
        self.msg_connect((self.dslwp_frame_spliter_f_0_0, 'out'), (self.dslwp_ccsds_pseudo_randomizer_0, 'in'))
        self.connect((self.analog_pll_carriertracking_cc_0, 0), (self.blocks_complex_to_imag_0, 0))
        self.connect((self.analog_pll_carriertracking_cc_0, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.blocks_complex_to_imag_0, 0), (self.hilbert_fc_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.digital_correlate_access_code_tag_xx_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.fir_filter_xxx_1, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_interleaved_char_to_complex_0, 0))
        self.connect((self.blocks_interleaved_char_to_complex_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.digital_correlate_access_code_tag_xx_0_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.satellites_rms_agc_0, 0))
        self.connect((self.digital_correlate_access_code_tag_xx_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.digital_correlate_access_code_tag_xx_0, 0), (self.dslwp_frame_spliter_f_0_0, 0))
        self.connect((self.digital_correlate_access_code_tag_xx_0_0, 0), (self.blocks_tag_debug_0, 1))
        self.connect((self.digital_correlate_access_code_tag_xx_0_0, 0), (self.dslwp_frame_spliter_f_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.hilbert_fc_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.satellites_rms_agc_0, 0), (self.analog_pll_carriertracking_cc_0, 0))
        self.connect((self.satellites_rms_agc_0, 0), (self.qtgui_freq_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Demod")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_syncword_hex(self):
        return self.syncword_hex

    def set_syncword_hex(self, syncword_hex):
        self.syncword_hex = syncword_hex
        self.set_syncword_bits(2*np.unpackbits(np.frombuffer(bytes.fromhex(self.syncword_hex), dtype = 'uint8')).astype('int')-1)

    def get_syncword_bits(self):
        return self.syncword_bits

    def set_syncword_bits(self, syncword_bits):
        self.syncword_bits = syncword_bits
        self.set_syncword_string(''.join([str(i) for i in (self.syncword_bits+1)//2]))
        self.fir_filter_xxx_1.set_taps(self.syncword_bits[::-1]/syncword_bits.size)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_samples_per_symbol(self.samp_rate/self.baudrate)
        self.analog_pll_carriertracking_cc_0.set_loop_bandwidth(self.PLL_BW_Hz * 2 * pi / self.samp_rate)
        self.analog_pll_carriertracking_cc_0.set_max_freq(self.PLL_Limit_Hz * 2 * pi / self.samp_rate)
        self.analog_pll_carriertracking_cc_0.set_min_freq(-self.PLL_Limit_Hz * 2 * pi / self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_baudrate(self):
        return self.baudrate

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate
        self.set_samples_per_symbol(self.samp_rate/self.baudrate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.baudrate)

    def get_syncword_string(self):
        return self.syncword_string

    def set_syncword_string(self, syncword_string):
        self.syncword_string = syncword_string
        self.digital_correlate_access_code_tag_xx_0.set_access_code(self.syncword_string)
        self.digital_correlate_access_code_tag_xx_0_0.set_access_code(self.syncword_string)

    def get_subcarrier_freq(self):
        return self.subcarrier_freq

    def set_subcarrier_freq(self, subcarrier_freq):
        self.subcarrier_freq = subcarrier_freq
        self.analog_sig_source_x_0.set_frequency(self.subcarrier_freq)

    def get_samples_per_symbol(self):
        return self.samples_per_symbol

    def set_samples_per_symbol(self, samples_per_symbol):
        self.samples_per_symbol = samples_per_symbol

    def get_PLL_Limit_Hz(self):
        return self.PLL_Limit_Hz

    def set_PLL_Limit_Hz(self, PLL_Limit_Hz):
        self.PLL_Limit_Hz = PLL_Limit_Hz
        self.analog_pll_carriertracking_cc_0.set_max_freq(self.PLL_Limit_Hz * 2 * pi / self.samp_rate)
        self.analog_pll_carriertracking_cc_0.set_min_freq(-self.PLL_Limit_Hz * 2 * pi / self.samp_rate)

    def get_PLL_BW_Hz(self):
        return self.PLL_BW_Hz

    def set_PLL_BW_Hz(self, PLL_BW_Hz):
        self.PLL_BW_Hz = PLL_BW_Hz
        self.analog_pll_carriertracking_cc_0.set_loop_bandwidth(self.PLL_BW_Hz * 2 * pi / self.samp_rate)





def main(top_block_cls=Demod, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
