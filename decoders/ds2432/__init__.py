##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2017 Kevin Redon <kingkevin@cuvoodoo.info>
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

'''
This decoder stacks on top of the 'onewire_network' PD and decodes the
Maxim DS2432 (1-Wire 1Kbit protected EEPROM with SHA-1 engine) protocol.
'''

from .pd import Decoder