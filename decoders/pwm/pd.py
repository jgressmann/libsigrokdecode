##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2014 Torsten Duwe <duwe@suse.de>
## Copyright (C) 2014 Sebastien Bourdelin <sebastien.bourdelin@savoirfairelinux.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd

class Decoder(srd.Decoder):
    api_version = 3
    id = 'pwm'
    name = 'PWM'
    longname = 'Pulse-width modulation'
    desc = 'Analog level encoded in duty cycle percentage.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['pwm']
    channels = (
        {'id': 'data', 'name': 'Data', 'desc': 'Data line'},
    )
    options = (
        {'id': 'polarity', 'desc': 'Polarity', 'default': 'active-high',
            'values': ('active-low', 'active-high')},
    )
    annotations = (
        ('duty-cycle', 'Duty cycle'),
        ('period', 'Period'),
    )
    annotation_rows = (
         ('duty-cycle', 'Duty cycle', (0,)),
         ('period', 'Period', (1,)),
    )
    binary = (
        ('raw', 'RAW file'),
    )

    def __init__(self):
        self.ss_block = self.es_block = None
        self.first_samplenum = None
        self.start_samplenum = None
        self.end_samplenum = None
        self.num_cycles = 0
        self.average = 0

    def metadata(self, key, value):
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def start(self):
        self.startedge = 0 if self.options['polarity'] == 'active-low' else 1
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_binary = self.register(srd.OUTPUT_BINARY)
        self.out_average = \
            self.register(srd.OUTPUT_META,
                          meta=(float, 'Average', 'PWM base (cycle) frequency'))

    def putx(self, data):
        self.put(self.ss_block, self.es_block, self.out_ann, data)

    def putp(self, period_t):
        # Adjust granularity.
        if period_t == 0 or period_t >= 1:
            period_s = '%.1f s' % (period_t)
        elif period_t <= 1e-12:
            period_s = '%.1f fs' % (period_t * 1e15)
        elif period_t <= 1e-9:
            period_s = '%.1f ps' % (period_t * 1e12)
        elif period_t <= 1e-6:
            period_s = '%.1f ns' % (period_t * 1e9)
        elif period_t <= 1e-3:
            period_s = '%.1f μs' % (period_t * 1e6)
        else:
            period_s = '%.1f ms' % (period_t * 1e3)

        self.put(self.ss_block, self.es_block, self.out_ann, [1, [period_s]])

    def putb(self, data):
        self.put(self.num_cycles, self.num_cycles, self.out_binary, data)

    def decode(self):

        # Get the first rising edge.
        pin, = self.wait({0: 'e'})
        if pin != self.startedge:
            pin, = self.wait({0: 'e'})
        self.first_samplenum = self.samplenum
        self.start_samplenum = self.samplenum

        # Handle all next edges.
        while True:
            pin, = self.wait({0: 'e'})

            if pin == self.startedge:
                # Rising edge
                # We are on a full cycle we can calculate
                # the period, the duty cycle and its ratio.
                period = self.samplenum - self.start_samplenum
                duty = self.end_samplenum - self.start_samplenum
                ratio = float(duty / period)

                # This interval starts at this edge.
                self.ss_block = self.start_samplenum
                # Store the new rising edge position and the ending
                # edge interval.
                self.start_samplenum = self.es_block = self.samplenum

                # Report the duty cycle in percent.
                percent = float(ratio * 100)
                self.putx([0, ['%f%%' % percent]])

                # Report the duty cycle in the binary output.
                self.putb([0, bytes([int(ratio * 256)])])

                # Report the period in units of time.
                period_t = float(period / self.samplerate)
                self.putp(period_t)

                # Update and report the new duty cycle average.
                self.num_cycles += 1
                self.average += percent
                self.put(self.first_samplenum, self.es_block, self.out_average,
                         float(self.average / self.num_cycles))
            else:
                # Falling edge
                self.end_samplenum = self.ss_block = self.samplenum
