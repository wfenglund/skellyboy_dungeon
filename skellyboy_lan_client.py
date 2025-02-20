import socket
import pygame
import json
import time

host = "127.0.0.1"
port = 6666

run = True

def translate_keys(keys):
    key_dict = {}
    if keys[pygame.K_UP]:
        key_dict[pygame.K_UP] = True
    if keys[pygame.K_DOWN]:
        key_dict[pygame.K_DOWN] = True
    if keys[pygame.K_LEFT]:
        key_dict[pygame.K_LEFT] = True
    if keys[pygame.K_RIGHT]:
        key_dict[pygame.K_RIGHT] = True
    if keys[pygame.K_w]:
        key_dict[pygame.K_w] = True
    if keys[pygame.K_s]:
        key_dict[pygame.K_s] = True
    if keys[pygame.K_a]:
        key_dict[pygame.K_a] = True
    if keys[pygame.K_d]:
        key_dict[pygame.K_d] = True
    if keys[pygame.K_SPACE]:
        key_dict[pygame.K_SPACE] = True
    if keys[pygame.K_q]:
        key_dict[pygame.K_q] = True
    return key_dict

client_socket = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

# while True:
#     data, addr = sock.recvfrom(32) # buffer size is 1024 bytes
#     print("received message: ", data)

pygame.init()
game_window = pygame.display.set_mode((500, 500))
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()
    key_dict = translate_keys(keys)
    if len(key_dict.keys()) > 0:
        key_dump = json.dumps(key_dict)
        print(key_dump.encode())
        client_socket.sendto(key_dump.encode(), (host, port))
        time.sleep(0.001)
#     received_data = client_socket.recv(1024)
#             pygame.time.delay(300)
#         client_socket.sendall(input('> ').encode())
#         print(received_data)
client_socket.close()
