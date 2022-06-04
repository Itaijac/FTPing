import math
import os
import random
from scapy.layers.inet import IP, ICMP
from scapy.all import Raw, send, sniff

SERVER_IP = '10.100.102.51'
CHUNK_SIZE = 1024
WINDOW_SIZE = 8


def filter_packets(packet):
    return IP in packet and packet[IP].src == SERVER_IP and ICMP in packet and packet[ICMP].type == 8


def sniff_packets(choosen_count, choosen_timeout=None):
    """We either sniff with a time limit or not, for example we don't want a time-limit when we look for the client but we do want a time limit when we look for packets"""
    if choosen_timeout is None:
        return sniff(count=choosen_count, lfilter=filter_packets)
    else:
        return sniff(count=choosen_count, lfilter=filter_packets, timeout=choosen_timeout)


def send_packets(data, index=None):
    request_packet = IP(dst=SERVER_IP)/ICMP(type="echo-request")
    if index is None:  # If we are sending an ACK packet and not a file-data one
        request_packet = request_packet/data
    else:
        data = str(index).encode() + b'|' + data
        request_packet = request_packet/data

    send(request_packet, verbose=False)


def get_packet_index():
    packets = sniff_packets(1)
    packet = packets[0]
    return int(packet[Raw].load)


def get_ack(packets_window):
    packet_index = get_packet_index()
    while packet_index != WINDOW_SIZE:
        # Re-send missing packets to the server
        for missing_packet in range(packet_index, WINDOW_SIZE):
            send_packets(packets_window[missing_packet], missing_packet)
        packet_index = get_packet_index()


def get_final_ack(packets_window):
    """This method is used to verify that the last 8 or less packets were recieved"""
    packet_index = get_packet_index()
    while packet_index != len(packets_window):
        for missing_packet in range(packet_index, len(packets_window)):
            send_packets(packets_window[missing_packet], missing_packet)
        packet_index = get_packet_index()


def read_in_chunks(file_object):
    """Lazy function (generator) to read a file piece by piece."""
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            break
        yield data


def send_file(file_path):
    with open(file_path, 'rb') as f:
        packets_window = []
        for piece in read_in_chunks(f):
            if len(packets_window) == WINDOW_SIZE:
                get_ack(packets_window)
                packets_window = []
            # This if statement is made to test the message-ACK algorithm. It is not actually needed.
            if random.randrange(3, 10) != 5:
                send_packets(piece, len(packets_window))
            packets_window.append(piece)
        get_final_ack(packets_window)
    print('All packets have been sent. Shutting down.')


def send_syn(file_name, packets_amount):
    """This function simulates a part of TCP's three-way-handshake by sending a SYN message with arguments and waiting for an ack packet in return."""
    send_packets(f'{file_name}|{packets_amount}')
    packets = sniff_packets(1, 10)
    if len(packets) == 1 and packets[0][Raw].load == b'ACK':
        print('Got ACK, starting to send the file.')
        return
    raise Exception('Server is off.')


def launch(file_path, file_name):
    packets_amount = math.ceil(os.path.getsize(file_path) / CHUNK_SIZE)
    send_syn(file_name, packets_amount)
    send_file(file_path)
