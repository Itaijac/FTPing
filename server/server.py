from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.all import *
import time
import sys
i, o, e = sys.stdin, sys.stdout, sys.stderr
sys.stdin, sys.stdout, sys.stderr = i, o, e

client_ip = ''  # The IP of the client is empty for the moment, we will fill it in later on
WINDOW_SIZE = 8


def filter_packets(packet):
    return ICMP in packet and packet[ICMP].type == 8


def sniff_packets(choosen_count, choosen_timeout=None):
    """We either sniff with a time limit or not, for example we don't want a time-limit when we look for the client but we do want a time limit when we look for packets"""
    if choosen_timeout is None:
        return sniff(count=choosen_count, lfilter=filter_packets)
    else:
        return sniff(count=choosen_count, lfilter=filter_packets, timeout=choosen_timeout)


def send_packets(data):
    request_packet = IP(dst=client_ip)/ICMP(type="echo-request")/data
    send(request_packet, verbose=False)


def get_last_valid(packets_dict):
    valid = -1
    for i in range(0, WINDOW_SIZE):
        if str(i) in packets_dict:
            valid = i
        else:
            break
    return valid + 1


def create_dict(packets, packets_dict):
    """This function returns a dict, key is the index of each packet and value is the file data"""
    for packet in packets:
        index = packet[Raw].load[:1].decode()
        data = packet[Raw].load[2:]
        packets_dict.update({index: data})
    return packets_dict


def get_parameters():
    global client_ip

    packets = sniff_packets(1)
    client_ip = packets[0][IP].src
    parameters = packets[0][Raw].load.decode().split('|')
    time.sleep(1)
    send_packets('ACK')
    return parameters[0], int(parameters[1])


def main():
    file_name, packets_amount = get_parameters()

    with open(file_name, 'wb') as f:
        while packets_amount > 0:
            packets_index = 0  # Resetting Parameters
            packets_dict = {}

            # This while loop is the core of the algorithm.
            while packets_index != WINDOW_SIZE and packets_amount - packets_index > 0:
                packets = sniff_packets(WINDOW_SIZE - packets_index, 0.1)
                packets_dict = create_dict(packets, packets_dict)
                packets_index = get_last_valid(packets_dict)
                send_packets(str(packets_index))
                print(f'Packets recieved - {packets_index}')
                print(f'Packets left - {packets_amount}')
            print('Out.')

            for key in sorted(packets_dict):  # Writes to the file
                f.write(packets_dict[key])

            packets_amount -= WINDOW_SIZE
        send_packets(str(packets_index))
        print('All data has been written. Shutting down.')


if __name__ == '__main__':
    main()
