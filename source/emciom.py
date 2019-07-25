#!/usr/bin/env python3
"""
A program for running multiple commands, capturing their outputs, and sending the
combined outputs by e-mail.
"""
__docformat__ = 'reStructuredText'
# ***************************************************************************************
#  File Name: emciom.py
#
# ---------------------------------------------------------------------------------------
#                           C O P Y R I G H T
# ---------------------------------------------------------------------------------------
#             Copyright (c) 2019 by Frank Voorburg   All rights reserved
#
#   This software has been carefully tested, but is not guaranteed for any particular
# purpose. The author does not offer any warranties and does not guarantee the accuracy,
#    adequacy, or completeness of the software and is not responsible for any errors or
#              omissions or the results obtained from use of the software.
# ---------------------------------------------------------------------------------------
#                             L I C E N S E
# ---------------------------------------------------------------------------------------
# This file is part of borgbahm. Borgbahm is free software: you can redistribute it 
# and/or modify it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Borgbahm is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program. If not, see <http://www.gnu.org/licenses/>.
#
# ***************************************************************************************

# ***************************************************************************************
#  Imports
# ***************************************************************************************
import logging
import argparse


# ***************************************************************************************
#  Global constant declarations
# ***************************************************************************************
# Program return codes.
RESULT_OK = 0


# ***************************************************************************************
#  Implementation
# ***************************************************************************************
def main():
    """
    Entry point into the program.
    """
    # Initialize the program exit code.
    result = RESULT_OK

    # Handle command line parameters.
    parser = argparse.ArgumentParser(description="A program for running multiple commands, " +
                                     "capturing their outputs, and sending\r\nthe combined " +
                                     "outputs by e-mail. The commands to run are listed " +
                                     "on each line\r\nin /etc/emciom/emciom.conf.\r\n",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    # Add mandatory command line parameters.
    parser.add_argument('recipient', type=str, help='e-mail address to send the message to.')
    parser.add_argument('sender', type=str, help='e-mail address of the sender.')

    # Add optional command line parameters.
    parser.add_argument('-d', '--debug', action='store_true', dest='debug_enabled', default=False,
                        help='enable debug messages on the standard output.')
    parser.add_argument('-es', action='store', dest='email_subject',
                        default='Message from emciom',
                        help='subject of the e-mail message.')
    parser.add_argument('-cf', action='store', dest='config_file',
                        default='/etc/emciom/emciom.conf',
                        help='Non-default configuration file to use.')
    # Perform actual command line parameter parsing.
    args = parser.parse_args()

    # Set the configuration values that where specified on the command line.
    cfg_email_to = args.recipient
    cfg_email_from = args.sender

    # Enable debug logging level if requested.
    if args.debug_enabled:
        logging.basicConfig(level=logging.DEBUG)

    # TODO Implement program here...

    # Give the exit code back to the caller
    return result


if __name__ == '__main__':
    exit(main())


# ********************************* end of emciom.py ************************************
