# Copyright 2016 Autodesk Inc.
# Modifications Copyright (C) 2019 Dietzlab (TUM), Elija Feigl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module is used to store information for a DNA domain.

    A domain is a contiguous sequence of bases within a strand. They are
    bounded by single->double or double->single strand transitions, crossovers
    between helices or strand termination.
"""
__all__ = ["Domain"]

from .energymodel import energy_model, convert_temperature_K_to_C


class Domain(object):
    """ This class stores information for a DNA domain.

        Attributes:
            id (int): The domain ID.
            helix (DnaStructureHelix): The helix the domain is contained in.
            strand (DnaStrand): The strand the domain is part of.
            base_list (List[DnaBase]): The list of bases in the domain.
            _color (List[Float]): The list of three RGB values defining the
                                  domain color.
    """
    def __init__(self, id, helix, strand, bases):
        self.id = id
        self.helix = helix
        self.strand = strand
        self.base_list = bases
        self._color = None

        self.sequence = "".join([b.seq for b in self.base_list])

        self.connected_strand = -1
        self.connected_domain = -1

    @property
    def color(self):
        """ The color property is related to what Cadnano thinks the color
            should be inthe input file, or can be arbitrarily assigned. There
            is an open question as to whether this should be directly part of
            the Domain object or should be metadata connected to it."""
        if self._color is not None:
            return self._color
        elif self.strand is not None:
            return self.strand.color
        else:
            return [0.5, 0.5, 0.5]

    @color.setter
    def color(self, newval):
        self._color = newval
        # should we also set the strand's color? Or can the domain have a
        # different color from the strand?

    def get_end_points(self):
        """ Get the end coordinates of the domain. """
        base_pos = self.helix.helix_axis_coords
        base1 = self.base_list[0]
        base2 = self.base_list[-1]
        point1 = base1.coordinates
        point2 = base2.coordinates
        return point1, point2

    def melting_temperature(self):
        """ Calculate the domain melting temperature. """
        # If we are not paired, return a nonphysical melting temperature.
        if self.connected_domain == -1:
            return -500.0

        # If we have any "N" bases in our sequence, also return a nonphysical
        # melting temperature:
        if "N" in self.sequence or 'n' in self.sequence:
            return -501.0

        def rev_complement(seq):
            comp = {"G": "C", "C": "G",
                    "A": "T", "T": "A",
                    "g": "c", "c": "g",
                    "a": "t", "t": "a",
                    "N": "N", "n": "n"}
            rev = []
            for i in range(len(seq)):
                rev.append(comp[seq[len(seq) - i - 1]])
            return "".join(rev)

        _, _, dH, dS = energy_model.stack_energy(self.sequence,
                                                 rev_complement(self.sequence)
                                                 )
        melting_temp_K = energy_model.melting_temperature(dH, dS)
        return convert_temperature_K_to_C(melting_temp_K)
