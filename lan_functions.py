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
