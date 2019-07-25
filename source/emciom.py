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
import os
import subprocess
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ***************************************************************************************
#  Global constant declarations
# ***************************************************************************************
# Program return codes.
RESULT_OK = 0
RESULT_ERROR_CONFIG_FILE_NOT_PRESENT = 1
RESULT_ERROR_CONFIG_FILE_EMPTY = 2
RESULT_ERROR_CANNOT_SEND_EMAIL = 3


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

    # Check if the configuration file is actually there
    if result == RESULT_OK:
        config_file_present = os.path.isfile(args.config_file)
        if not config_file_present:
            logging.debug('Config file is not present: {}'.format(args.config_file))
            result = RESULT_ERROR_CONFIG_FILE_NOT_PRESENT

    # Read the lines of the configuration file into a list of strings
    if result == RESULT_OK:
        # Note that the file is automatically closed when using the 'with' construct.
        with open(args.config_file) as config_file_obj:
            cmd_lines = config_file_obj.read().splitlines()
        # Check that at least some data was read from the config file.
        if not cmd_lines:
            logging.debug('No lines read from the configuration file {}'.format(args.config_file))
            result = RESULT_ERROR_CONFIG_FILE_EMPTY
        # Otherwise, remove empty lines and remove leading and trailing whitespaces from each line.
        else:
            cmd_lines = [cmd_line.strip() for cmd_line in cmd_lines if cmd_line.strip()]

    # Run the commands one at a time and capture the output.
    if result == RESULT_OK:
        cmd_output = list()
        for cmd in cmd_lines:
            # Add the command itself to the output, following by a separator line.
            cmd_output.append('================================================================================')
            cmd_output.append('Command: ' + cmd)
            cmd_output.append('--------------------------------------------------------------------------------')
            # Add the output of the actual command.
            current_cmd_output = run_command_with_output_capture(cmd)
            for output_line in current_cmd_output:
                cmd_output.append(output_line)
            # Add an end of command output separator.
            cmd_output.append('================================================================================')
            cmd_output.append('')

    # Send the captured command output by e-mail, if it is not empty.
    if result == RESULT_OK:
        if cmd_output:
            # Send the e-mail.
            if not send_email(cfg_email_to, cfg_email_from, args.email_subject, '\n'.join(cmd_output)):
                logging.debug('Unabe to send email to {}'.format(cfg_email_to))
                result = RESULT_ERROR_CANNOT_SEND_EMAIL

    # Give the exit code back to the caller
    return result


def run_command_with_output_capture(command):
    """
    Runs the command specified in the command-parameters, captures and returns the
    output that the command generated.

    :param command: The command to run, e.g. 'ls -l'.

    :returns: A list of strings with the captured output
    :rtype: list of str
    """
    result = ""
    proc_ran_okay = True

    try:
        proc = subprocess.Popen(command, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        proc.wait()
    except Exception as error:
        proc_ran_okay = False

    # Get the captured output and convert it to a list of strings.
    result = stdout.decode('utf-8').splitlines()

    # Give the result back to the caller
    return result


def send_email(recipient, sender, subject, content):
    """
    Sends an e-mail message. This assumes a mail transfer agent such as postfix is
    installed on the system.

    :param recipient: The e-mail address to send the message to.
    :param sender: The e-mail address of the sender.
    :param subject: The subject of the message.
    :param content: The content of the message.


    :returns: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Construct the message.
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(content))

    # Send the message.
    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(sender, [recipient], msg.as_string())
    except email.SMTPException:
        result = False

    # Make sure the connection is closed.
    smtp.close()

    # Give the result back to the caller.
    return result


if __name__ == '__main__':
    exit(main())


# ********************************* end of emciom.py ************************************
