import pygame, math
import pygame.gfxdraw
import ctypes
import os
from numba import njit, prange
from settings import *
import numpy
import random


@njit(fastmath=True)
def polygon_division_func(poly_1, poly_2):
    x1_1, y1_1 = poly_1[0][0], poly_1[0][1]
    x1_2, y1_2 = poly_1[1][0], poly_1[1][1]
    x2_1, y2_1 = poly_2[0][0], poly_2[0][1]
    x2_2, y2_2 = poly_2[1][0], poly_2[1][1]
    return "none", "none"


def find_xch_and_ych_func(ll):
    answer = [0, 0]
    if ll >= 0 and ll < 90:
        answer[0] = -1 + (1 / 90) * ll
        answer[1] = 1 / 90 * ll
    elif ll >= 90 and ll < 180:
        answer[0] = (1 / 90) * (ll - 90)
        answer[1] = 1 - (1 / 90) * (ll - 90)
    elif ll >= 180 and ll < 270:
        answer[0] = 1 - (1 / 90) * (ll - 180)
        answer[1] = 0 - (1 / 90) * (ll - 180)
    elif ll >= 270 and ll < 360:
        answer[0] = 0 - (1 / 90) * (ll - 270)
        answer[1] = -1 + (1 / 90) * (ll - 270)
    return answer

@njit(fastmath=True)
def distXY_func(x, x1, y, y1):  # функция расстояний x и y между двумя оюъектами
    if x < x1:
        distX = x1 - x
    else:
        distX = x - x1
    if y < y1:
        distY = y1 - y
    else:
        distY = y - y1
    return distX, distY

@njit(fastmath=True)
def Pifogor_func(x, y):  # функция вычисления теоремы Пифагора
    Pifogor = math.sqrt(x * x + y * y)
    return Pifogor

@njit(fastmath=True)
def Perim_func(Pifogor, Pifogor1, hypo_of_va):  # функция периметра треугольника с гипотенузой в 1920
    Perim = (Pifogor + Pifogor1 + hypo_of_va) / 2
    return Perim

@njit(fastmath=True)
def Perim_half_func_ver2(Pifogor, Pifogor1, semi_hypo_of_va):  # функция периметра треугольника с гипотенузой в 960
    Perim = (Pifogor + Pifogor1 + semi_hypo_of_va) / 2
    return Perim

@njit(fastmath=True)
def Arithmetical_Mean_func(a, b):  # функция среднего арифметического
    return (a + b) / 2

def vignette_shader():
    coeff = 2
    for i in prange(1920):
        for j in prange(1080):
            if i < 255:
                pygame.gfxdraw.pixel(screen, i, j, [0, 0, 0, (255 - int(i)) // coeff])
            elif i > 1920 - 255:
                pygame.gfxdraw.pixel(screen, i, j, [0, 0, 0, (255 - int(1920 - i)) // coeff])
            if j < 255:
                pygame.gfxdraw.pixel(screen, i, j, [0, 0, 0, (255 - int(j)) // coeff])
            elif j > 1080 - 255:
                pygame.gfxdraw.pixel(screen, i, j, [0, 0, 0, (255 - int(1080 - j)) // coeff])

@njit(fastmath=True)
def triagle_hit_checking_func(x, y, a, b, a1, b1, nx, ny):
    chk1 = (x - nx) * (b - y) - (a - x) * (y - ny)
    chk2 = (a - nx) * (b1 - b) - (a1 - a) * (b - ny)
    chk3 = (a1 - nx) * (y - b1) - (x - a1) * (b1 - ny)

    if chk1 > 0 and chk2 > 0 and chk3 > 0:
        return True

    return False

@njit(fastmath=True)
def projection_func(x, y, angle, angle1, nx, ny, nz):

    distXX, distYY = distXY_func(x=x, x1=nx, y=y, y1=ny)
    Pifogor_dist = Pifogor_func(x=distXX, y=distYY)

    lesser_hypo_of_va = 1.413 * Pifogor_dist
    semi_hypo_of_va = Pifogor_dist
    hypo_of_va = Pifogor_dist * 2

    a = (lesser_hypo_of_va * math.cos(angle)) + x
    b = (lesser_hypo_of_va * math.sin(angle)) + y

    a1 = (lesser_hypo_of_va * math.cos(angle1)) + x
    b1 = (lesser_hypo_of_va * math.sin(angle1)) + y


    averageX = Arithmetical_Mean_func(a=a, b=a1)
    averageY = Arithmetical_Mean_func(a=b, b=b1)
    distXX, distYY = distXY_func(x=x, x1=nx, y=y,y1=ny)
    dist_against_fisheye1, dist_against_fisheye2 = distXY_func(x=averageX,x1=nx,y=averageY,y1=ny)

    Pifogor_dist = Pifogor_func(x=distXX, y=distYY)
    Pifogor_against_fisheye = Pifogor_func(x=dist_against_fisheye1, y=dist_against_fisheye2)
    Perim_against_fisheye = Perim_half_func_ver2(Pifogor=Pifogor_against_fisheye, Pifogor1=Pifogor_dist, semi_hypo_of_va=semi_hypo_of_va)

    if Perim_against_fisheye * (Perim_against_fisheye - semi_hypo_of_va) * (Perim_against_fisheye - Pifogor_dist) * (Perim_against_fisheye - Pifogor_against_fisheye) >= 0:
        h_fe = numpy.sqrt(Perim_against_fisheye * (Perim_against_fisheye - semi_hypo_of_va) * (Perim_against_fisheye - Pifogor_dist) * (Perim_against_fisheye - Pifogor_against_fisheye)) * (2 / semi_hypo_of_va)
    else:
        h_fe = 0

    if Pifogor_dist >= h_fe:
        Pifogor_Answer_Fisheye = numpy.sqrt(Pifogor_dist * Pifogor_dist - h_fe * h_fe)
    else:
        Pifogor_Answer_Fisheye = numpy.sqrt(h_fe * h_fe - Pifogor_dist * Pifogor_dist)


    length_lines_for_projection = Pifogor_func(x=Pifogor_Answer_Fisheye, y=Pifogor_Answer_Fisheye)

    dist_to_left_x, dist_to_left_y = distXY_func(x=a, x1=nx, y=b,y1=ny)
    dist_to_right_x, dist_to_right_y = distXY_func(x=a1, x1=nx, y=b1, y1=ny)

    pif_to_left = Pifogor_func(x=dist_to_left_x, y=dist_to_left_y)
    pif_to_right = Pifogor_func(x=dist_to_right_x, y=dist_to_right_y)

    if pif_to_right < pif_to_left:
        a_projection = (length_lines_for_projection * math.cos(angle)) + x
        b_projection = (length_lines_for_projection * math.sin(angle)) + y

        line_projection_x, line_projection_y = distXY_func(x=a_projection, x1=nx, y=b_projection, y1=ny)
        final_length_line_for_projection = Pifogor_func(x=line_projection_x, y=line_projection_y)
        x_display_output = (final_length_line_for_projection) * (960 / Pifogor_Answer_Fisheye)
    else:
        a_projection = (length_lines_for_projection * math.cos(angle1)) + x
        b_projection = (length_lines_for_projection * math.sin(angle1)) + y

        line_projection_x, line_projection_y = distXY_func(x=a_projection, x1=nx, y=b_projection, y1=ny)
        final_length_line_for_projection = Pifogor_func(x=line_projection_x, y=line_projection_y)
        x_display_output = 1920 - ((final_length_line_for_projection) * (960 / Pifogor_Answer_Fisheye))



    z_size = (210000 / (Pifogor_Answer_Fisheye))

    answ = x_display_output
    answ1 = (540 + (nz * 0.01 * (z_size / 2)))
    answ3 = Pifogor_func(Pifogor_dist, abs(nz))

    return answ, answ1, answ3


def z_shift(map, down, up):
    if down == True:
        for iterator in prange(len(map)):
            map[iterator][2] += speed
            map[iterator][5] += speed
            map[iterator][8] += speed
    elif up == True:
        for iterator in prange(len(map)):
            map[iterator][2] -= speed
            map[iterator][5] -= speed
            map[iterator][8] -= speed

    return map