import pygame
import sys
import socket
import math
import random
import lan_functions

def host_server():
    pass

def client_interaction():
    pass

def translate_map_char(map_file, character): # Get all coordinates of a character in a map file
    with open(map_file) as raw_map:
        map_list = []
        row = 0
        one_tile = 25
        for lines in raw_map:
            map_list = map_list + [[col*one_tile, row*one_tile] for col, char in enumerate(lines.strip()) if char == character]
            row = row + 1
        return map_list

def parse_player_input(player_dict, keys, no_walk_list, attack_list, cur_map, armory_dict, connection_dict):
    one_tile = 25
    x, y = player_dict['coords']
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and not keys[pygame.K_SPACE]:
        if y > 0 and [x, y - one_tile] not in no_walk_list:
            y = y - one_tile
        elif str(x) + ',' + str(y - one_tile) in connection_dict.keys():
            y = y - one_tile
            print('connection')
        player_dict['facing'] = 'back'
        print(f'{x},{y}')

    if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not keys[pygame.K_SPACE]:
        if y < 475 and [x, y + one_tile] not in no_walk_list:
            y = y + one_tile
        elif str(x) + ',' + str(y + one_tile) in connection_dict.keys():
            y = y + one_tile
            print('connection')
        player_dict['facing'] = 'front'
        print(f'{x},{y}')

    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not keys[pygame.K_SPACE]:
        if x > 0 and [x - one_tile, y] not in no_walk_list:
            x = x - one_tile
        elif str(x - one_tile) + ',' + str(y) in connection_dict.keys():
            x = x - one_tile
            print('connection')
        player_dict['facing'] = 'left'
        print(f'{x},{y}')

    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not keys[pygame.K_SPACE]:
        if x < 475 and [x + one_tile, y] not in no_walk_list:
            x = x + one_tile
        elif str(x + one_tile) + ',' + str(y) in connection_dict.keys():
            x = x + one_tile
            print('connection')
        player_dict['facing'] = 'right'
        print(f'{x},{y}')

    if str(x) + ',' + str(y) in connection_dict.keys():
        connection_info = connection_dict[str(x) + ',' + str(y)]
        cur_map = connection_info[0].strip()
        coords_list = connection_info[1].split(',')
        x = int(coords_list[0].strip())
        y = int(coords_list[1].strip())
    
    if keys[pygame.K_SPACE] and player_dict['cooldown'] == 0: # if attack ready
        player_attack = {}
        player_attack['weapon'] = armory_dict[player_dict['wielding'][0]]
        player_attack['weapon_image'] = pygame.image.load('./images/' + player_attack['weapon']['image']).convert_alpha() # load image

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_attack['coords'] = [x, y - one_tile]
            player_attack['direction'] = 'up'
            print('attack up')
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_attack['coords'] = [x, y + one_tile]
            player_attack['weapon_image'] = pygame.transform.rotate(player_attack['weapon_image'], 180) # rotate weapon downwards
            player_attack['direction'] = 'down'
            print('attack down')
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_attack['coords'] = [x - one_tile, y]
            player_attack['weapon_image'] = pygame.transform.rotate(player_attack['weapon_image'], 90) # rotate weapon to the left
            player_attack['direction'] = 'left'
            print('attack left')
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_attack['coords'] = [x + one_tile, y]
            player_attack['weapon_image'] = pygame.transform.rotate(player_attack['weapon_image'], 270) # rotate weapon to the right
            player_attack['direction'] = 'right'
            print('attack right')
        if 'coords' in player_attack.keys(): # if an attack was made
            player_attack['coords_old'] = [x, y]
            player_attack['age'] = 'new'
            player_attack['attacker'] = player_dict['name']
            player_dict['cooldown'] = 8
            attack_list = attack_list + [player_attack]
    
    if keys[pygame.K_q] or player_dict['change_weapon'] == 'yes':
        if player_dict['switch_delayer'] < 6:
            player_dict['change_weapon'] = 'yes'
        if player_dict['change_weapon'] == 'yes' and player_dict['switch_delayer'] == 0:
            player_dict['wielding'] = player_dict['wielding'][1:] + [player_dict['wielding'][0]]
            player_dict['change_weapon'] = 'no'
            player_dict['switch_delayer'] = 8
    
    player_dict['coords'] = [x, y]
    return player_dict, cur_map, attack_list

def parse_mapinf(map_file, bestiary_dict):
    connection_dict = {}
    loaded_mobs = []
    with open(map_file) as map_info:
        for line in map_info:
            if line.startswith('connection:'):
                raw_connection = line.strip().replace('connection:', '')
                coords, new_loc = raw_connection.split('=')
                connection_dict[coords] = new_loc.split(':')
            if line.startswith('mob:'):
                raw_mob = line.strip().replace('mob:', '')
                mob_name, mob_coords = raw_mob.split('=')
                mob = bestiary_dict[mob_name]
                coords_list = mob_coords.split(',')
                mob['coords'] = [int(coords_list[0]), int(coords_list[1])]
                loaded_mobs = loaded_mobs + [mob.copy()] # without the copy this updates mob_list as well
    return connection_dict, loaded_mobs

def walk_mobs(mob_list, player_coords, no_walk_list, mob_delayer):
    one_tile = 25
    new_mob_list = []
    if mob_delayer == 1: # if mob is allowed to map out new directions
        for mob in mob_list:
            full_x = mob_x = mob['coords'][0]
            full_y = mob_y = mob['coords'][1]
            if mob['aggro'] == 'no':
                for player in player_coords.keys():
                    x_diff = mob_x - player_coords[player][0]
                    y_diff = mob_y - player_coords[player][1]
                    x_diff_tiles = math.sqrt(x_diff * x_diff)
                    y_diff_tiles = math.sqrt(y_diff * y_diff)
                    if (x_diff_tiles > (4 * one_tile) or y_diff_tiles > (4 * one_tile)) and (mob['aggro'] == 'no' and mob['target'] != player):
                        x_diff = [0, 0, 0, 0, 0, 0, 0, 0, 25, -25][random.randint(0, 9)]
                        y_diff = [0, 0, 0, 0, 0, 0, 0, 0, 25, -25][random.randint(0, 9)]
                    else:
                        mob['aggro'] = 'yes'
                        mob['target'] = player
                        break
            else:
                player = mob['target']
                x_diff = mob_x - player_coords[player][0]
                y_diff = mob_y - player_coords[player][1]
            if mob['x_movement'] == 'none' and mob['y_movement'] == 'none':
                if x_diff > 0:
                    full_x = mob_x - one_tile
                    mob_x = mob_x - (one_tile / 2)
                    mob['x_movement'] = 'x_minus'
                    mob['facing'] = 'left'
                elif x_diff < 0:
                    full_x = mob_x + one_tile
                    mob_x = mob_x + (one_tile / 2)
                    mob['x_movement'] = 'x_plus'
                    mob['facing'] = 'right'
                if y_diff > 0:
                    full_y = mob_y - one_tile
                    mob_y = mob_y - (one_tile / 2)
                    mob['y_movement'] = 'y_minus'
                    mob['facing'] = 'back'
                elif y_diff < 0:
                    full_y = mob_y + one_tile
                    mob_y = mob_y + (one_tile / 2)
                    mob['y_movement'] = 'y_plus'
                    mob['facing'] = 'front'
#                 if [full_x, full_y] != [player_coords[player][0], player_coords[player][1]] and [full_x, full_y] not in no_walk_list:
                if [full_x, full_y] not in no_walk_list + list(player_coords.values()):
                    if mob['coords'] in no_walk_list:
                        no_walk_list.pop(no_walk_list.index(mob['coords']))
                    mob['coords'] = [mob_x, mob_y]
                    no_walk_list = no_walk_list + [[full_x, full_y]]
                else:
                    mob['x_movement'] = mob['y_movement'] = 'none'
            new_mob_list = new_mob_list + [mob]
    else: # if only old directions are to be finished this game cycle
        for mob in mob_list:
            if mob['x_movement'] == 'x_plus':
                mob['coords'][0] = mob['coords'][0] + (one_tile / 2)
            elif mob['x_movement'] == 'x_minus':
                mob['coords'][0] = mob['coords'][0] - (one_tile / 2)
            if mob['y_movement'] == 'y_plus':
                mob['coords'][1] = mob['coords'][1] + (one_tile / 2)
            elif mob['y_movement'] == 'y_minus':
                mob['coords'][1] = mob['coords'][1] - (one_tile / 2)
            mob['x_movement'] = mob['y_movement'] = 'none'
            new_mob_list = new_mob_list + [mob]
    return new_mob_list, no_walk_list

def attack_overlap(coords1, coords2):
    one_tile = 25

    if coords1[0] == coords2[0]:
        diff = coords1[1] - coords2[1]
        positive_diff = math.sqrt(diff * diff)
        if positive_diff < one_tile:
            return True
        else:
            return False
    elif coords1[1] == coords2[1]:
        diff = coords1[0] - coords2[0]
        positive_diff = math.sqrt(diff * diff)
        if positive_diff < one_tile:
            return True
        else:
            return False
    else:
        return False

def calculate_bounce(cur_victim, cur_attack, no_walk_list):
    old_x, old_y = cur_victim['coords']
    atk_x, atk_y = cur_attack['coords_old']
    bounce_back = cur_attack['weapon']['bounce']
    x_bounce, y_bounce = [0, 0]
    while bounce_back > 0:
        if [old_x + x_bounce + (old_x - atk_x), old_y + y_bounce + (old_y - atk_y)] not in no_walk_list:
            x_bounce = x_bounce + (old_x - atk_x)
            y_bounce = y_bounce + (old_y - atk_y)
        bounce_back = bounce_back - 1
    return [old_x + int(x_bounce), old_y + int(y_bounce)] # return new coordinates

def maintain_mob(game_window, mob_list, player_coords, attack_list, no_walk_list):
    one_tile = 25

    for cur_attack in attack_list: # for every attack
        new_mob_list = []
        for mob in mob_list:
            if attack_overlap(mob['coords'], cur_attack['coords']) and cur_attack['attacker'] != 'mob':
                mob['status'] = 'attacked'
                mob['aggro'] = 'yes'
                mob['target'] = cur_attack['attacker']
                if cur_attack['weapon']['dmg'] < mob['hitpoints']:
                    mob['damage'] = cur_attack['weapon']['dmg']
                else:
                    mob['damage'] = mob['hitpoints']
                mob['hitpoints'] = mob['hitpoints'] - cur_attack['weapon']['dmg']

                # make mobs bounce back from being hit but not into walls:
                mob['coords'] = calculate_bounce(mob, cur_attack, no_walk_list)
            new_mob_list = new_mob_list + [mob]
        mob_list = new_mob_list
 
    new_mob_list = []
    for mob in mob_list:
        # draw mob:
#         pygame.draw.rect(game_window, (255, 255, 255), (mob['coords'][0], mob['coords'][1], one_tile, one_tile))
        if mob['facing'] == 'left':
            mob_image = pygame.image.load('./images/' + mob['left_img']).convert_alpha() # load image
        elif mob['facing'] == 'right':
            mob_image = pygame.image.load('./images/' + mob['right_img']).convert_alpha() # load image
        elif mob['facing'] == 'back':
            mob_image = pygame.image.load('./images/' + mob['back_img']).convert_alpha() # load image
        elif mob['facing'] == 'front':
            mob_image = pygame.image.load('./images/' + mob['front_img']).convert_alpha() # load image
        else:
            mob_image = pygame.image.load('./images/' + mob['front_img']).convert_alpha() # load image
        game_window.blit(mob_image, (mob['coords'][0], mob['coords'][1])) # draw image
        
        # add hitpoints bar:
        pygame.draw.rect(game_window, (255, 0, 0), (mob['coords'][0], mob['coords'][1], one_tile, one_tile / 10))
        pygame.draw.rect(game_window, (0, 255, 0), (mob['coords'][0], mob['coords'][1], one_tile * (mob['hitpoints'] / mob['max_hp']), one_tile / 10))

        if mob['status'] == 'attacked': # do something if mob is attacked
            hit_font = pygame.font.SysFont('Comic Sans MS', 30)
            hit_surface = hit_font.render('-' + str(mob['damage']), False, (255, 0, 0)) # draw hitsplat
            game_window.blit(hit_surface, (mob['coords'][0], mob['coords'][1]))
#             pygame.draw.rect(game_window, (255, 0, 0), (mob['coords'][0], mob['coords'][1], one_tile, one_tile))
            mob['status'] = 'normal'
        if mob['hitpoints'] > 0:
            if mob['cooldown'] > 0:
                mob['cooldown'] = mob['cooldown'] - 1
            new_mob_list = new_mob_list + [mob]
    return new_mob_list

def maintain_player(player_dict, attack_list, no_walk_list):
    x, y = player_dict['coords']
    for cur_attack in attack_list:
        if attack_overlap([x, y], cur_attack['coords']) and cur_attack['attacker'] == 'mob':
            player_dict['hitpoints'] = player_dict['hitpoints'] - cur_attack['weapon']['dmg']
            player_dict['coords'] = calculate_bounce(player_dict, cur_attack, no_walk_list)
            print('hit')
    return player_dict
        
def draw_all_coor(game_window, map_file, character, color, choice):
    one_tile = 25
    if choice == 'color':
        for xcoor, ycoor in translate_map_char(map_file, character): # for every instance of 'character'
            pygame.draw.rect(game_window, color, (xcoor, ycoor, one_tile, one_tile))
    if choice == 'picture':
        tile_test = pygame.image.load(color).convert() # load image
        for xcoor, ycoor in translate_map_char(map_file, character): # for every instance of 'character'
            game_window.blit(tile_test, (xcoor, ycoor))

def draw_player(game_window, player_dict):
    coord_tuple = tuple(player_dict['coords'])
    if player_dict['facing'] == 'back':
        player_image = pygame.image.load('./images/' + 'player_back.png').convert_alpha() # load image
        game_window.blit(player_image, coord_tuple)
    if player_dict['facing'] == 'front':
        player_image = pygame.image.load('./images/' + 'player_front.png').convert_alpha() # load image
        game_window.blit(player_image, coord_tuple)
    if player_dict['facing'] == 'left':
        player_image = pygame.image.load('./images/' + 'player_left.png').convert_alpha() # load image
        game_window.blit(player_image, coord_tuple)
    if player_dict['facing'] == 'right':
        player_image = pygame.image.load('./images/' + 'player_right.png').convert_alpha() # load image
        game_window.blit(player_image, coord_tuple)

def determine_mob_attacks(mob_list, player_dict, attack_list, armory_dict):
    one_tile = 25
    for mob in mob_list: # determine mob attacks
        if mob['aggro'] == 'yes' and mob['cooldown'] == 0 and (mob['x_movement'] == 'none' and mob['y_movement'] == 'none'):
            mob_x, mob_y = mob['coords']
            x, y = player_dict[mob['target']]
            x_diff = mob_x - x
            y_diff = mob_y - y
            new_attack = {}
            new_attack['weapon'] = armory_dict[mob['wields']] # get weapon info
            new_attack['weapon_image'] = pygame.image.load('./images/' + new_attack['weapon']['image']).convert_alpha() # load image
            if y_diff > 0:
                new_attack['coords'] = [mob_x, mob_y - one_tile]
                new_attack['direction'] = 'up'
            elif y_diff < 0:
                new_attack['coords'] = [mob_x, mob_y + one_tile]
                new_attack['weapon_image'] = pygame.transform.rotate(new_attack['weapon_image'], 180) # rotate weapon downwards
                new_attack['direction'] = 'down'
            elif x_diff > 0:
                new_attack['coords'] = [mob_x - one_tile, mob_y]
                new_attack['weapon_image'] = pygame.transform.rotate(new_attack['weapon_image'], 90) # rotate weapon downwards
                new_attack['direction'] = 'left'
            elif x_diff < 0:
                new_attack['coords'] = [mob_x + one_tile, mob_y]
                new_attack['weapon_image'] = pygame.transform.rotate(new_attack['weapon_image'], 270) # rotate weapon downwards
                new_attack['direction'] = 'right'
            if 'coords' in new_attack.keys(): # if an attack was made
                mob['cooldown'] = 8
                new_attack['coords_old'] = [mob_x, mob_y]
                new_attack['age'] = 'new'
                new_attack['attacker'] = 'mob'
                attack_list = attack_list + [new_attack]
    return attack_list

def draw_attacks(attack_list):
    pass

def update_attacks(game_window, attack_list):
    one_tile = 25
    new_attack_list = []
    for cur_attack in attack_list:
        attack_coords = cur_attack['coords']
        game_window.blit(cur_attack['weapon_image'], (attack_coords[0], attack_coords[1]))
        if cur_attack['weapon']['type'] == 'projectile' and cur_attack['age'] == 'old':
            if cur_attack['direction'] == 'up':
                attack_coords[1] = attack_coords[1] - one_tile
            elif cur_attack['direction'] == 'down':
                attack_coords[1] = attack_coords[1] + one_tile
            elif cur_attack['direction'] == 'left':
                attack_coords[0] = attack_coords[0] - one_tile
            elif cur_attack['direction'] == 'right':
                attack_coords[0] = attack_coords[0] + one_tile
            if attack_coords[0] > 0 and attack_coords[0] < 500 and attack_coords[1] > 0 and attack_coords[1] < 500:
                cur_attack['coords_old'] = cur_attack['coords']
                cur_attack['coords'] = attack_coords
                new_attack_list = new_attack_list + [cur_attack]
        elif cur_attack['age'] == 'new': # if attack was initiated this cycle
            cur_attack['age'] = 'old'
            new_attack_list = new_attack_list + [cur_attack]
    return new_attack_list

def draw_icons(game_window, player_dict, armory_dict):
    weapon_display_image = pygame.image.load('./images/' + armory_dict[player_dict['wielding'][0]]['image']).convert_alpha() # load current weapon image
    game_window.blit(weapon_display_image, (0, 475))
    hp_font = pygame.font.SysFont('Comic Sans MS', 25)
    hp_surface = hp_font.render(str(player_dict['hitpoints']) + '/' + str(player_dict['max_hp']), False, (255, 0, 0)) # draw hitsplat
    game_window.blit(hp_surface, (0, 0))

def get_polygon(mltp, x, y):
    x_p = x - ((7*mltp - 25) / 2)
    y_p = y - ((3*mltp - 25) / 2)
    polygon_coords = ((x_p, y_p), (x_p + mltp, y_p), (x_p + mltp, y_p - mltp), (x_p + 2*mltp, y_p - mltp), (x_p + 2*mltp, y_p - 2*mltp), (x_p + 5*mltp, y_p - 2*mltp), (x_p + 5*mltp, y_p - mltp), (x_p + 6*mltp, y_p - mltp), (x_p + 6*mltp, y_p), (x_p + 7*mltp, y_p), (x_p + 7*mltp, y_p + 3*mltp), (x_p + 6*mltp, y_p + 3*mltp), (x_p + 6*mltp, y_p + 4*mltp), (x_p + 5*mltp, y_p + 4*mltp), (x_p + 5*mltp, y_p + 5*mltp), (x_p + 2*mltp, y_p + 5*mltp), (x_p + 2*mltp, y_p + 4*mltp), (x_p + mltp, y_p + 4*mltp), (x_p + mltp, y_p + 3*mltp), (x_p, y_p + 3*mltp))
    return polygon_coords

def draw_torchlight(game_window, player_dict, light_setting, max_shadow):
    one_tile = 25
    light_intensity = light_setting
    x, y = player_dict['coords']
    for i in range(1, light_intensity):
        shadow_layer = pygame.Surface((500, 500))
        shadow_layer.fill((0, 0, 0))
        mltp = light_setting * i
        pygame.draw.polygon(shadow_layer, (0, 0, 1), get_polygon(mltp, x, y))
        shadow_layer.fill((0, 0, 1), rect = pygame.Rect(0, 0, 9 * one_tile, one_tile))
        shadow_layer.fill((0, 0, 1), rect = pygame.Rect(0, 475, 9 * one_tile, one_tile))
        pygame.Surface.set_colorkey(shadow_layer, (0, 0, 1))
        shadow_layer.set_alpha(max_shadow / light_intensity - 1)
        game_window.blit(shadow_layer, (0, 0))

def start_game():
    # Initiate game:
    pygame.init()
    game_window = pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Skellyboy Dungeon")
    pygame.font.init()

    # Assign variables:
    one_tile = 25 # determine fundamental unit of measurement
    run = True
#     prev_x = x
#     prev_y = y
    cur_map = 'map1' # prefix name of the starting map
    old_map = ''
    attack_list = []
    twelve_seconds = 0
    mob_list = []
    mob_delayer = 1
    host_server = True
#     host_server = False
    socket_players = {} # create list to hold players who connect using UDP

    # Open socket:
    if host_server == True:
        host = sys.argv[1]
        port = int(sys.argv[2])
        open_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        open_socket.bind((host, port))
        open_socket.settimeout(0.00001)

    # Create player:
    player_dict = {}
    player_dict['name'] = 'local'
    player_dict['starting_coords'] = [250, 475] # x, y
    player_dict['coords'] = player_dict['starting_coords']
    player_dict['cooldown'] = 0 # attack cooldown
    player_dict['change_weapon'] = 'no' # if player has chosen to change weapon
    player_dict['switch_delayer'] = 0 # delay for switching weapon
    player_dict['max_hp'] = 20
    player_dict['hitpoints'] = player_dict['max_hp']
    player_dict['facing'] = 'front'
    player_dict['wielding'] = ['basic sword', 'basic bow']
    player_copy = player_dict.copy()

    # Load weapons:
    armory_dict = {}
    with open("armory.data") as armory:
        for row in armory:
            weapon = eval(row.strip())
            armory_dict[weapon['name']] = weapon

    # Load mobs:
    bestiary_dict = {}
    with open("bestiary.data") as mobs:
        for row in mobs:
            mob = eval(row.strip())
            bestiary_dict[mob['name']] = mob

    # Start game loop:
    while run:
        pygame.time.delay(75) # determine game speed
        twelve_seconds = twelve_seconds + 75

        for event in pygame.event.get():  # for all events
            if event.type == pygame.QUIT: # check if game window gets closed
                run = False  # end game loop
                print('Game Closed')
        
        # Parse map information:
        connection_dict, loaded_mobs = parse_mapinf('./maps/' + cur_map + '.mapinf', bestiary_dict)
        if old_map != cur_map: # if entering a new map
            mob_list = loaded_mobs # update mobs
        old_map = cur_map
        
        # Create no walk list:
        no_walk_list = translate_map_char('./maps/' + cur_map + '.maplay', '#') # find unwalkable tiles
        no_walk_list = no_walk_list + [i['coords'] for i in mob_list]

        # Parse player input:
        keys = pygame.key.get_pressed()
        if host_server == True:
#             keys = lan_functions.retrieve_keys(open_socket) # control player via UDP-socket
            keys2 = ''
            while keys2 != 'nothing':
                keys2, sender = lan_functions.retrieve_keys2(open_socket) # control player via UDP-socket
                if keys2 != 'nothing':
                    if sender[0] not in socket_players.keys():
                        player_copy['name'] = sender[0] # give the player a name
                        socket_players[sender[0]] = [player_copy, keys2]
                    else:
                        socket_players[sender[0]][1] = keys2
        print(socket_players)

        player_dict, cur_map, attack_list = parse_player_input(player_dict, keys, no_walk_list, attack_list, cur_map, armory_dict, connection_dict)

        coords_dict = {}
        coords_dict[player_dict['name']] = player_dict['coords']
        for user_key in socket_players.keys(): # handle socket connected players
            socket_players[user_key][0], cur_map, attack_list = parse_player_input(socket_players[user_key][0], socket_players[user_key][1], no_walk_list, attack_list, cur_map, armory_dict, connection_dict)
            # Reset keys for player:
            socket_players[user_key][1] = {i:False for i in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE, pygame.K_q]}
            coords_dict[socket_players[user_key][0]['name']] = socket_players[user_key][0]['coords']
        
        # Determine if mobs are walking this game cycle and update no walk list:
        mob_list, no_walk_list = walk_mobs(mob_list, coords_dict, no_walk_list, mob_delayer)

        # Draw game window:
        game_window.fill((0,0,0))  # fill screen with black
#         draw_all_coor(game_window, 'map1.txt', '0', (128,128,128), 'color') # draw all '0' characters as dark gray
        draw_all_coor(game_window, './maps/' + cur_map + '.maplay', '0', ('./images/' + 'tile_test.png'), 'picture') # draw all '0' characters as test tile
#         pygame.draw.rect(game_window, (255,0,0), (x, y, one_tile, one_tile))  # draw player
        draw_player(game_window, player_dict)
        for user_key in socket_players.keys(): # handle socket connected players
            draw_player(game_window, socket_players[user_key][0])
        
        # Add new mob attacks:
        attack_list = determine_mob_attacks(mob_list, coords_dict, attack_list, armory_dict)

        # Draw attacks:
#         draw_attacks(game_window, attack_list)
        
        # Update current attacks:
        attack_list = update_attacks(game_window, attack_list)
        
        # Maintain mobs and players:
        mob_list = maintain_mob(game_window, mob_list, player_dict['coords'], attack_list, no_walk_list)
        player_dict = maintain_player(player_dict, attack_list, no_walk_list) # determine if player is hit
        for user_key in socket_players.keys(): # handle socket connected players
            socket_players[user_key][0] = maintain_player(socket_players[user_key][0], attack_list, no_walk_list)

        # Draw icons:
        draw_icons(game_window, player_dict, armory_dict)

        # Draw torchlight:
#         raw_torchlight(game_window, player_dict, 10, 800) # hard
        max_shadow = 800 / (len(socket_players.keys()) + 1)
        draw_torchlight(game_window, player_dict, 15, max_shadow) # normal
        for user_key in socket_players.keys(): # handle socket connected players
            draw_torchlight(game_window, socket_players[user_key][0], 15, max_shadow)

        # Update screen:
        pygame.display.update()
        
        # Handle and update values:
        mob_delayer = mob_delayer + 1
        if mob_delayer > 3:
            mob_delayer = 1
        if player_dict['hitpoints'] <= 0: # if player is out of hitpoints, reset to start position
            old_map = ''
            cur_map = 'map1'
            player_dict['coords'] = player_dict['starting_coords']
            player_dict['hitpoints'] = player_dict['max_hp']
        if player_dict['cooldown'] > 0: # decrease cooldown if relevant
            player_dict['cooldown'] = player_dict['cooldown'] - 1
        if player_dict['switch_delayer'] > 0: # decrease weapon switch delayer if relevant
            player_dict['switch_delayer'] = player_dict['switch_delayer'] - 1
        for user_key in socket_players.keys(): # handle socket connected players
            if socket_players[user_key][0]['cooldown'] > 0:
                socket_players[user_key][0]['cooldown'] = socket_players[user_key][0]['cooldown'] - 1
            if socket_players[user_key][0]['switch_delayer'] > 0:
                socket_players[user_key][0]['switch_delayer'] = socket_players[user_key][0]['switch_delayer'] - 1
        if twelve_seconds >= 12000: # if ~1200 milliseconds have passed
            if player_dict['hitpoints'] < player_dict['max_hp']: # if not full hp
                player_dict['hitpoints'] = player_dict['hitpoints'] + 1 # increase hp by one
            twelve_seconds = 0 # reset timer
        
        # store current x and y as previous x and y:
#         prev_x = x
#         prev_y = y
    open_socket.close()
    pygame.quit()

start_game()
