import socket
import json
import pygame

def retrieve_keys(open_socket):
    try:
        received_data = open_socket.recv(1024)
    except BlockingIOError:
        received_data = b'{}'
    except OSError:
        received_data = b'{}'
    key_dict_raw = json.loads(received_data.decode())
    key_dict = {int(k):v for k,v in key_dict_raw.items()}
    false_dict = {i:False for i in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE, pygame.K_q] if i not in key_dict.keys()}
    key_dict.update(false_dict)
    return key_dict

def retrieve_keys2(open_socket):
    try: # also make players send a ping even if nothing was pressed, later calculate how long players have been disconnected and remove if neccessary
        received_data, sender = open_socket.recvfrom(1024)
    except BlockingIOError:
        received_data, sender = 'nothing', 'no_one'
    except OSError:
        received_data, sender = 'nothing', 'no_one'
    except TimeoutError:
        received_data, sender = 'nothing', 'no_one'
    if received_data == 'nothing':
        return received_data, sender
    else:
        key_dict_raw = json.loads(received_data.decode())
        key_dict = {int(k):v for k,v in key_dict_raw.items()}
        false_dict = {i:False for i in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE, pygame.K_q] if i not in key_dict.keys()}
        key_dict.update(false_dict)
        return key_dict, sender
