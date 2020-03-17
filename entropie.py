#!/usr/bin/env python
# -*- encoding: utf8 -*-
#
#  entropie.py : Tool to calculate entropy on files
#
#  (C) Copyright 2011 Olivier Delhomme
#  e-mail : olivier.delhomme@free.fr
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

__author__ = "Olivier Delhomme <olivier.delhomme@free.fr>"
__date__ = "28.09.2016"
__version__ = "Revision: 0.0.2"


import sys
import getopt
import math


class Options:
    """A class to manage command line options

    line : says wether the entropy should be calculated line by line
    base : the base to calculate the shannon entropy
    files : the files to operate onto
    method : global to consider the whole file as a set and each block or lines
            as subsets
    size : block size to read (in block mode)
    output : Says wether we want a simple output (True) or a detailed one (default)
    """

    args = ''           # Command line arguments
    opts = ''           # Command line options
    line = False
    block = False
    base = 2
    size = 16
    files = []
    method = 'local'
    output = False

    def __init__(self):
        """Init function
        """

        self.line = False
        self.block = False
        self.base = 2
        self.files = []
        self.method = 'local'
        self.output = False
        self.parse_command_line()

    # Help message for main program
    def usage(self, exit_value):
        print("""
  NAME
      entropie.py

  SYNOPSIS
      entropie.py [OPTIONS] FILE1 FILE2...

  DESCRIPTION
      Calculates the shannon entropy of a file.

  OPTIONS
      -h, --help
        This Help

      -l, --line
        Calculates the entropy of each line

      -b, --block
        Calculates the entropy of each bloc (16 bytes by default)

      -s SIZE, --size=SIZE
        Sets the block size to SIZE in bytes (16 bytes by default)

      -m METHOD, --method=METHOD
        Determines how to calculate the probabilities of the elements. METHOD
        can be 'local' or 'global'. If set to local (default) the probabilities
        are evaluated at each calculation. If set to global the probabilities
        are evaluated once with the whole file.

      -e, --entropy
        Outputs only the entropy (the number)


  EXAMPLES
      entropie.py -l entropie.py
      entropie.py -s 32 -b -m local entropie.py
        """)
        sys.exit(exit_value)

    # End of function usage()


    def transform_to_int(self, opt, arg):
        """transform 'arg' argument from the command line to an int where
        possible

        >>> my_opts = Options()
        >>> my_opts.transform_to_int('', '2')
        2
        """

        try:
            arg = int(arg)
        except:
            print("Error (%s), NUM must be an integer. Here '%s'" % (str(opt), str(arg)))
            sys.exit(2)

        if arg > 0:
            return arg
        else:
            print("Error (%s), NUM must be positive. Here %d" % (str(opt), arg))
            sys.exit(2)

    # End of transform_to_int function


    def parse_command_line(self):
        """Parses command line's options and arguments
        """

        short_options = "hlbes:m:"
        long_options = ['help', 'list', 'block', 'entropy', 'size=', 'method=']

        # Read options and arguments
        try:
            opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
        except getopt.GetoptError as err:
            # print help information and exit with error :
            print("%s" % str(err))
            self.usage(2)

        for opt, arg in opts:

            if opt in ('-h', '--help'):
                self.usage(0)
            elif opt in ('-l', '--line'):
                self.line = True
            elif opt in ('-b', '--block'):
                self.block = True
            elif opt in ('-m', '--method'):
                self.method = arg.lower()
            elif opt in ('-s', '--size'):
                self.size = self.transform_to_int(opt, arg)
            elif opt in ('-e', '--entropy'):
                self.output = True

        self.files = args

    # End function parse_command_line()
# End of Class Options


def buffer_shannon_entropy(buffer, buffer_size, probability, my_opts):
    return buffer_shannon_entropy_subset(buffer, buffer_size, probability, probability, my_opts)

# End of buffer_shannon_entropy function


def buffer_shannon_entropy_subset(buffer, buffer_size, probability, histogram, my_opts):

    entropie = 0.0
    # Calculating entropy on each {x1,... xn} from the buffer

    for key in histogram.keys():

        p = probability[key]

        # if p == 0 is is admitted that 0 * logn(0) = 0 so nothing has to be done
        if p != 0.0:
            entropie += p * math.log(p, my_opts.base)

    if entropie > 0:
        return entropie
    else:
        return -entropie

# End of buffer_shannon_entropy_subset() function



def buffer_histogram_dict(buffer, buffer_size, histogram):

    # Filling the dictionary with the values
    for i, value in enumerate(buffer):
    #i = 0
    #while i < buffer_size:
        #value = buffer[i]

        if value in histogram:
            histogram[value] += 1
        else:
            histogram[value] = 1

        #i += 1

    return histogram

# End of buffer_histogram_dict() function


def probability_on_histogram(histogram, buffer_size):

    probability = dict()

    # Calculating the probability
    for key,hist in histogram.items():
        probability[key] = float(hist) / float(buffer_size)
        # print('%s : %s' % (key, probability[key]))

    return probability

# End of probability_on_histogram() function


def buffer_probability_dict(buffer, buffer_size):

    histogram = dict()

    histogram = buffer_histogram_dict(buffer, buffer_size, histogram)

    return probability_on_histogram(histogram, buffer_size)

# End of buffer_probability_dict() function


def open_file(filename, my_opts):
    """Opens a file in binary mode if block mode is selected or in text mode if
    line mode is selected
    """

    if my_opts.block:
        size = my_opts.size
        
        a_file = open(filename, 'rb')
        read_from_file = lambda a_file: read_block_from_file(a_file,size)
    else:
        a_file = open(filename, 'r')
        read_from_file = read_line_from_file

    return a_file , read_from_file

# End of open_file() function


def read_line_from_file(a_file):
    """Reads one line from an opened file (in text mode) strip the trailing
    \n and returns it
    """

    line = a_file.readline()
    if len(line) == 0:
        len_line = None
    else:
        line = line.strip()
        len_line = len(line)
    
    return (line, len_line)

def read_block_from_file(a_file, size):
    """ Reads one block from an opened file (in binary mode)
        and returns it
    """

    buffer = a_file.read(size)
    len_buffer = len(buffer)
    return (buffer, len_buffer if len_buffer > 0  else None)

# End of read_from_file() function


def entropy_local(a_file, read_from_file, my_opts):
    (buffer, length) = read_from_file(a_file)
    i = 0
    while length is not None:
        if length >  0:
            # Creating our probability vector
            probability = buffer_probability_dict(buffer, length)
            
            entropy_str = str(buffer_shannon_entropy(buffer, length, probability, my_opts))
            if not my_opts.output:
                elem = str(i)  if my_opts.block  else  buffer
                print(elem + ' : ' + entropy_str)
            else:
                print(entropy_str)

        (buffer, length) = read_from_file(a_file)
        i = i + 1

# End of entropy_local() function


def entropy_global(a_file, read_from_file, my_opts):
    # Calculating the global probabilities
    histogram = dict()
    total = 0

    (buffer, length) = read_from_file(a_file)

    while length is not None:
        total = total + length
        histogram = buffer_histogram_dict(buffer, length, histogram)
        (buffer, length) = read_from_file(a_file)

    probability = probability_on_histogram(histogram, total)
    a_file.seek(0)

    # Calculating some sort of shannon entropy
    (buffer, length) = read_from_file(a_file)
    i = 0
    while length is not None:

        # Calculating the histogram (we only need the key to get the subset
        # from which we want to have the entropy)
        if length > 0:
            histogram_slice = dict()
            histogram_slice = buffer_histogram_dict(buffer, length, histogram_slice)
            
            entropy_str = str(buffer_shannon_entropy_subset(buffer, length, probability, histogram_slice, my_opts))
            if not my_opts.output:
                elem = str(i)  if my_opts.block  else  buffer
                print(elem + ' : ' + entropy_str)
            else:
                print(entropy_str)

            histogram_slice.clear()
        (buffer, length) = read_from_file(a_file)
        i = i + 1

# End of entropy_global() function 


def entropy(my_opts):
    """Calculates the entropy on each line of the files
    """

    for filename in my_opts.files:
        if not my_opts.output:
            print('Calculating {0} {1} entropy on file "{2}"'.format('block'  if my_opts.block  else 'line',my_opts.method,filename))
        
        a_file , read_from_file = open_file(filename, my_opts)
        if my_opts.method == 'local':
            entropy_local(a_file, read_from_file , my_opts)
        else:
            entropy_global(a_file, read_from_file , my_opts)
            
        a_file.close()

# End of entropy() function


def main():

    my_opts = Options()

    entropy(my_opts)

# End of main() function


if __name__=="__main__" :
    main()
