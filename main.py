import socket
import os
import sys
import psutil
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import threading
# import yaml

assemble_wol_packet = lambda _: f"{'FF-' * 6}{(_ + '-') * 16}"
check_is_wol_packet = lambda _, __: '-'.join(f'{byte:02x}' for byte in _).upper() + '-' == __

def resource_path(relative_path: str):
    try: base_path = sys._MEIPASS
    except: base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

def get_ip_mac_address(interface_name: str) -> tuple:
    ip_addr = mac_addr = None

    for item in psutil.net_if_addrs().get(interface_name, []):
        addr = item.address

        # В IPv4-адресах разделители - точки
        if '.' in addr:
            ip_addr = addr
        # В MAC-адресах разделители либо тире, либо одинарное двоеточие.
        # Двойное двоеточие - это разделители для адресов IPv6
        elif ('-' in addr or ':' in addr) and '::' not in addr:
            # Приводим MAC-адрес к одному формату. Формат может меняться в зависимости от ОС
            mac_addr = addr.replace(':', '-').upper()

    if not ip_addr or not mac_addr or ip_addr == '127.0.0.1': return None, None

    return ip_addr, mac_addr

def main(interface_name: str, port: int, command: str):
    ip_addr, mac_addr = get_ip_mac_address(interface_name)

    if not (ip_addr and mac_addr): return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip_addr, port))
    # logger.info(f'Listening on {ip_addr}:{port}')

    assembled_wol_packet = assemble_wol_packet(mac_addr)

    thread = threading.Thread(target=icon(name='wol-shutdown', icon=Image.open(resource_path('off.ico')), 
    menu=menu(item('exit', lambda _, __: os._exit(0)))
    ).run)
    thread.start()

    while True:
        data, _ = server_socket.recvfrom(1024)

        if check_is_wol_packet(data, assembled_wol_packet): os.system(command)
            # os._exit(0)
        
if __name__ == '__main__': 
    # if os.path.exists('config.yaml'):
    #     with open('config.yaml', 'r') as f: config = yaml.load(f, Loader=yaml.FullLoader)
    #     main(config['INTERFACE_NAME'], config['PORT'])
    config = {k: int(v) if v.isdigit() else v for k, v in zip(['INTERFACE_NAME', 'PORT', 'COMMAND'], sys.argv[1:4])}
    main(config['INTERFACE_NAME'], config['PORT'], config['COMMAND'])