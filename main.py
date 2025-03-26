import pygame, math
import pygame.gfxdraw
import ctypes
import os
from numba import njit, prange
import numpy
import random
from calculation import *
from settings import *
import get_m


def update_screen():
    #vignette_shader()
    font_1 = pygame.font.SysFont("Lucida Console", round(32))
    f3menu3 = font_1.render("FPS: " + str(round(clock.get_fps())), False, [200, 200, 200])
    pygame.gfxdraw.box(screen, [user_screen.get_width() - f3menu3.get_width(), 0, f3menu3.get_width(), f3menu3.get_height()], [0, 0, 0])
    screen.blit(f3menu3, (user_screen.get_width() - f3menu3.get_width(), 0))

    if user_screen.get_width() != 1920 and user_screen.get_height() != 1080:
        v_screen = pygame.transform.scale(screen, (user_screen.get_width(), user_screen.get_height()))
    else:
        v_screen = screen


    pygame.gfxdraw.textured_polygon(user_screen, [[0, 0], [v_screen.get_width() - 1, 0],
                                                  [v_screen.get_width() - 1, v_screen.get_height()],
                                                  [0, v_screen.get_height()]], v_screen, 0, 0)

    pygame.display.flip()



def rotate_texture(image, angle):
    orig_rect = image.get_rect()
    image = pygame.transform.rotate(image, angle)
    rect = orig_rect.copy()
    rect.center = image.get_rect().center
    image = image.subsurface(rect).copy()
    texture = image.subsurface((texture_size[0] // 4, texture_size[1] // 4, texture_size[0] // 2, texture_size[1] // 2))
    return texture


def draw_button_func(x, y, text):
    button_text = my_font.render(text, True, [29, 29, 29])
    text_len_x = (((120 * scaling_w) - (len(text) * (13 * scaling_w))) // 2)
    text_len_y = (((50 * scaling_h) - (15 * scaling_h)) // 2)

    x_mouse, y_mouse = pygame.mouse.get_pos()

    button_show = pygame.Rect((x - (60 * scaling_w), y - (25 * scaling_h), (120 * scaling_w), (50 * scaling_h)))

    collide = button_show.collidepoint(x_mouse, y_mouse)

    if collide == True:
        pygame.draw.rect(screen, (80, 184, 160),(x - (60 * scaling_w), y - (25 * scaling_h), (120 * scaling_w), (50 * scaling_h)), 0, 7)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pygame.draw.rect(screen, (43, 43, 43), (x - (60 * scaling_w), y - (25 * scaling_h), (120 * scaling_w), (50 * scaling_h)), 0, 7)
                pygame.draw.rect(screen, (80, 184, 160), (x - (60 * scaling_w), y - (25 * scaling_h), (120 * scaling_w), (50 * scaling_h)), 0, 10)
                pygame.draw.rect(screen, (43, 43, 43), (x - (60 * scaling_w), y - (25 * scaling_h), (120 * scaling_w), (50 * scaling_h)), 3, 10)
                screen.blit(button_text, (text_len_x + (x - (60 * scaling_w)), ((y - (25 * scaling_h)) + text_len_y) - (3 * scaling_h)))
                return True

    else:
        pygame.draw.rect(screen, (100, 230, 200),(x - (60 * scaling_w), y - (25 * scaling_h), (120 * scaling_w), (50 * scaling_h)), 0, 7)

    screen.blit(button_text, (text_len_x + (x - (60 * scaling_w)), ((y - (25 * scaling_h)) + text_len_y) - (3 * scaling_h)))


def show_model(map, texture, ribs):

    memory_size = 20000
    aa_map = []

    #texture = rotate_texture(texture, round(i))
    #texture = texture.subsurface((texture_size[0] // 4, texture_size[1] // 4, texture_size[0] // 2, texture_size[1] // 2))
    #screen.blit(texture, [50, 50])
    #texture = [200, 120, 255]
    polygons_map = []
    shading_list = []

    for cicle in prange(len(map)):
        ch0 = triagle_hit_checking_func(x, y, a, b, a1, b1, map[cicle][0], map[cicle][1])
        ch1 = triagle_hit_checking_func(x, y, a, b, a1, b1, map[cicle][3], map[cicle][4])
        ch2 = triagle_hit_checking_func(x, y, a, b, a1, b1, map[cicle][6], map[cicle][7])

        if ch0 == True or ch1 == True or ch2 == True:
            rand = 0
            ox_0, oy_0, c0 = projection_func(x, y, angle, angle1, map[cicle][0] + rand, map[cicle][1] + rand,
                                             map[cicle][2] + rand)
            ox_1, oy_1, c1 = projection_func(x, y, angle, angle1, map[cicle][3] + rand, map[cicle][4] + rand,
                                             map[cicle][5] + rand)
            ox_2, oy_2, c2 = projection_func(x, y, angle, angle1, map[cicle][6] + rand, map[cicle][7] + rand,
                                             map[cicle][8] + rand)

            coeff = (c0 + c1 + c2) / 3
            coeff = (coeff / 30)
            if coeff > 255:
                coeff = 255
            if coeff < 0:
                coeff = 0

            polygons_map.append([ox_0, oy_0, ox_1, oy_1, ox_2, oy_2, int(coeff)])
            shading_list.append(round(255 - coeff, 1))

    polygons_map = numpy.array(polygons_map)
    shading_list = numpy.array(shading_list)
    inds = numpy.argsort(shading_list, kind='quicksort')
    polygons_map = polygons_map[inds]

    #keydict = dict(zip(polygons_map, shading_list))
    #polygons_map.sort(key=keydict.get)

    for cicle in prange(len(polygons_map)):  # начало цикла вычесления проекции и вывода

        ox_0, oy_0 = polygons_map[cicle][0], polygons_map[cicle][1]
        ox_1, oy_1 = polygons_map[cicle][2], polygons_map[cicle][3]
        ox_2, oy_2 = polygons_map[cicle][4], polygons_map[cicle][5]
        color = [0, 0, 0, polygons_map[cicle][6]]

        if (oy_0 < memory_size and oy_0 > -memory_size) and (oy_1 < memory_size and oy_1 > -memory_size) and (oy_2 < memory_size and oy_2 > -memory_size):
            if (ox_0 < memory_size and ox_0 > -memory_size) and (ox_1 < memory_size and ox_1 > -memory_size) and (ox_2 < memory_size and ox_2 > -memory_size):

                if (oy_0 < 1080 and oy_0 > 0) or (oy_1 < 1080 and oy_1 > 0) or (oy_2 < 1080 and oy_2 > 0):
                    if (ox_0 < 1920 and ox_0 > 0) or (ox_1 < 1920 and ox_1 > 0) or (ox_2 < 1920 and ox_2 > 0):

                            #if ribs == True:
                            #aa_map.append([ox_0, oy_0, ox_1, oy_1, ox_2, oy_2])

                        #texture = [round(min(abs(cicle / 2), 255)), round(min(abs(len(polygons_map) * 2), 255)), round(min(abs(cicle + oy_0 / 5), 255))]
                        #print(texture)
                        if type(texture) == list:

                            #pygame.gfxdraw.aatrigon(screen, round(ox_0), round(oy_0), round(ox_1), round(oy_1), round(ox_2), round(oy_2), (texture))
                            #pygame.gfxdraw.aatrigon(screen, round(ox_0), round(oy_0), round(ox_1), round(oy_1), round(ox_2), round(oy_2), (color))
                            #pygame.gfxdraw.aapolygon(screen, [[round(ox_0), round(oy_0)], [round(ox_1), round(oy_1)], [round(ox_2), round(oy_2)]], (texture))
                            pygame.gfxdraw.filled_polygon(screen, [[round(ox_0), round(oy_0)], [round(ox_1), round(oy_1)],[round(ox_2), round(oy_2)]], (texture))
                            #pygame.gfxdraw.aapolygon(screen, [[round(ox_0), round(oy_0)], [round(ox_1), round(oy_1)], [round(ox_2), round(oy_2)]], (texture))
                        else:
                            size_x = round(max(ox_0, ox_1, ox_2) - min(ox_0, ox_1, ox_2))
                            size_y = round(max(oy_0, oy_1, oy_2) - min(oy_0, oy_1, oy_2))
                            if size_x < 1:
                                size_x = 1
                            if size_y < 1:
                                size_y = 1
                            if size_x > display_width and size_y > display_heidth:
                                size_x = 1
                                size_y = 1

                            using = pygame.transform.scale(texture, [size_x, size_y])
                            #print(size_x, size_y)
                            pygame.gfxdraw.textured_polygon(screen, [[round(ox_0), round(oy_0)],
                                                                                [round(ox_1), round(oy_1)],
                                                                                [round(ox_2), round(oy_2)]], using, int((ox_0 + ox_1 + ox_2) / 3), int((oy_0 + oy_1 + oy_2) / 3) * -1)
                            #print("bye")
                            #pygame.gfxdraw.aatrigon(screen, round(ox_0), round(oy_0), round(ox_1), round(oy_1),round(ox_2), round(oy_2), (texture))

                        pygame.gfxdraw.filled_trigon(screen, round(ox_0), round(oy_0), round(ox_1), round(oy_1),round(ox_2), round(oy_2), color)
                        #pygame.gfxdraw.aatrigon(screen, round(ox_0), round(oy_0), round(ox_1), round(oy_1), round(ox_2), round(oy_2), ([0, 0, 0]))
    #for aa in prange(len(aa_map)):
        #pygame.gfxdraw.aatrigon(screen, round(aa_map[aa][0]), round(aa_map[aa][1]), round(aa_map[aa][2]), round(aa_map[aa][3]),
                        #round(aa_map[aa][4]), round(aa_map[aa][5]), ([0, 0, 0]))



dir = os.path.abspath(os.curdir)

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

display_width = user32.GetSystemMetrics(0)
display_heidth = user32.GetSystemMetrics(1)

if display_width > 1920:
    scaling_w = 1920 / display_width
else:
    scaling_w = display_width / 1920

if display_heidth > 1080:
    scaling_h = 1080 / display_heidth
else:
    scaling_h = display_heidth / 1080

pygame.init()

#sc_v = Vect()

flags = pygame.SCALED | pygame.DOUBLEBUF
user_screen = pygame.display.set_mode((1920, 1080), flags, vsync=1)
screen = pygame.Surface((1920, 1080))#.convert_alpha()
pygame.display.set_caption("3D Engine")

my_font = pygame.font.SysFont("System", 30)
l_font = pygame.font.SysFont("System", 30)

counter_text = l_font.render("Loading...", True, [255, 255, 255])

screen.blit(counter_text, (910, 520))


clock = pygame.time.Clock()
pygame.display.flip()



map1 = get_m.load_model()


random_gen = False

if random_gen == True:
    for rand in prange(10):
        bias_x = random.randint(600, 2000)
        bias_y = random.randint(0, 1000)
        map.append([random.randint(-50, 50) + bias_x, random.randint(-50, 50) + bias_y, random.randint(-50, 50), random.randint(-50, 50) + bias_x
                    , random.randint(-50, 50) + bias_y, random.randint(-50, 50), random.randint(-50, 50)  + bias_x, random.randint(-50, 50) + bias_y, random.randint(-50, 50)])


# mini_map_display = True
map_size = 3

Pifogor_buffer_max = 0
main_buffer_cicle = 0
buffer_update = 0
buffer_cicle = 0

iteration_cicle = 0

polygon_display = 0
flat_polygon_output = [[0, 0, 0], [0, 0, 0]]
pre_flat_polygon_color = [0, 0]

texture_size_x = 0
color = [0, 0, 0]

mini_map_display = False

check = True

running = True  # значение работы программы
move_up = False
move_down = False
move_right = False
move_left = False
move_down_z = False
move_up_z = False
camera_left = False
camera_right = False


#map = distribution_buffer_func(map1, len(map1))

m_coeff = 1
m2_coeff = 1

running = True

while running:  # начало основного цикла

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_up = True
            if event.key == pygame.K_s:
                move_down = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_q:
                camera_left = True
            if event.key == pygame.K_e:
                camera_right = True
            if event.key == pygame.K_f:
                move_down_z = True
            if event.key == pygame.K_r:
                move_up_z = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_up = False
            if event.key == pygame.K_s:
                move_down = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_q:
                camera_left = False
            if event.key == pygame.K_e:
                camera_right = False
            if event.key == pygame.K_f:
                move_down_z = False
            if event.key == pygame.K_r:
                move_up_z = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                camera_left = True
            if event.button == 3:
                camera_right = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                camera_left = False
            if event.button == 3:
                camera_right = False

    if move_up:
        x += round(xch[2] * speed)
        y += round(ych[2] * speed)
    if move_down:
        x -= round(xch[2] * speed)
        y -= round(ych[2] * speed)
    if move_left:
        x += round(xch[1] * speed * 1.2)
        y += round(ych[1] * speed * 1.2)
    if move_right:
        x += round(xch[0] * speed * 1.2)
        y += round(ych[0] * speed * 1.2)

    if camera_right:
        i += speed_rotation
        i1 += speed_rotation
        for f in range(speed_rotation):
            rotation_midle -= 1
            if rotation_midle < 0:
                rotation_midle = 359
            ll -= 1
            if ll < 0:
                ll = 359
            pp -= 1
            if pp < 0:
                pp = 359

    if camera_left:
        i -= speed_rotation
        i1 -= speed_rotation
        for f in range(speed_rotation):
            rotation_midle += 1
            if rotation_midle > 359:
                rotation_midle = 0
            ll += 1
            if ll > 359:
                ll = 0
            pp += 1
            if pp > 359:
                pp = 0

    # далее программа переводит градусы более 360 и менее нуля в стандартные

    if i >= 360:
        i -= 360

    if i < 0:
        i += 360

    if i1 >= 360:
        i1 -= 360

    if i1 < 0:
        i1 += 360

    angle = i * 3.14 / 180
    a = (lesser_hypo_of_va * math.cos(angle)) + x
    b = (lesser_hypo_of_va * math.sin(angle)) + y

    angle1 = i1 * 3.14 / 180
    a1 = (lesser_hypo_of_va * math.cos(angle1)) + x
    b1 = (lesser_hypo_of_va * math.sin(angle1)) + y

    averageX = Arithmetical_Mean_func(a=a, b=a1)
    averageY = Arithmetical_Mean_func(a=b, b=b1)

    f = find_xch_and_ych_func(rotation_midle)
    xch[2] = (-x + averageX) / semi_hypo_of_va
    ych[2] = (-y + averageY) / semi_hypo_of_va

    f = find_xch_and_ych_func(ll)
    xch[0] = f[0]
    ych[0] = f[1]

    f = find_xch_and_ych_func(pp)
    xch[1] = f[0]
    ych[1] = f[1]
    ecrx = x + xch[2] * vision_r // 4
    ecry = y + ych[2] * vision_r // 4

    if check:
        check = False
    else:
        check = True

    pygame.gfxdraw.box(screen, [[0, 0], [1920, 1080]], [0, 0, 0])

    z_shift(map1, move_up_z, move_down_z)

    show_model(map1, [255, 255, 255], True)

    if mini_map_display == True:
        f3menu1 = my_font.render("X: " + str(x), True, [200, 200, 200])
        f3menu2 = my_font.render("Y: " + str(y), True, [200, 200, 200])

        for cicle in prange(len(map)):
            pygame.gfxdraw.aapolygon(screen, [[map[cicle][6] + 100, map[cicle][7] + 100, map[cicle][3] + 100, map[cicle][4] + 100],
                                              [map[cicle][3] + 100, map[cicle][4] + 100, map[cicle][0] + 100, map[cicle][1] + 100],
                                              [map[cicle][0] + 100, map[cicle][1] + 100, map[cicle][6] + 100, map[cicle][7] + 100]], [255, 255, 255])


        pygame.gfxdraw.filled_circle(screen, round(x) // map_size, round(y) // map_size, round(8 * scaling_h),[220, 220, 220])
        pygame.gfxdraw.aacircle(screen, round(x) // map_size, round(y) // map_size, round(8 * scaling_h),[220, 220, 220])


    update_screen()  # обновление экрана

pygame.quit()