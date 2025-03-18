#!/usr/bin/env python3
import json
import sys
from tkinter import SE
import pygame
import State
import SaveLoad
from pygame.locals import *
MAX_DATA_POINTS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
state = int(0)
BmiData = []
BmiData = SaveLoad.Load()
def Draw():
    try:
        # 只显示最近30个数据点
        display_data = BmiData[-MAX_DATA_POINTS:]
        
        # 计算图表参数
        max_bmi = max(display_data) if display_data else 40
        x_scale = 640 / (len(display_data)-1) if len(display_data)>1 else 0
        
        # 绘制坐标轴
        pygame.draw.line(screen, BLACK, (20, 400), (620, 400), 2)  # X轴
        pygame.draw.line(screen, BLACK, (20, 60), (20, 400), 2)     # Y轴
        
        # 绘制数据点和标签
        points = []
        for i in range(len(display_data)):
            x = 20 + i * x_scale
            y = 400 - (display_data[i]/max_bmi)*340  # 缩放至合理高度
            points.append((x, y))
            
            # 数据点标签（每5个显示一个）
            if i % 5 == 0 or i == len(display_data)-1:
                label = font.render(f"{display_data[i]:.1f}", True, BLUE)
                screen.blit(label, (x-15, y-20))
                
        if len(points) > 1:
            pygame.draw.lines(screen, BLACK, False, points, 2)
    except Exception as e:
        print("绘图错误:", e)
# 初始化 Pygame
pygame.init()

# 设置窗口大小
size = (640, 480)
screen = pygame.display.set_mode(size)
 
# 设置窗口标题名称
pygame.display.set_caption("BMI Calculator")
 
# 通过字体文件获得字体对象
font = pygame.font.Font(None, 24)
f_h = font.get_height()
 
# 设置背景
screen.fill(WHITE)
 
# 文本位置
p1 = (250, 5)
p2 = (250, f_h + 5)
p3 = (250, f_h * 2 + 5)
p4 = (250, f_h*3 + 5)
# 初始化变量
weight = 55  
height_cm = 170  
height_m = height_cm / 100
bmi = weight / (height_m ** 2)
bmi_state = ""
# 渲染初始文本
textWeight = font.render("Weight (kg): " + str(weight), True, BLUE, GREEN)
textHeight = font.render("Height (cm): " + str(height_cm), True, BLUE, GREEN)
textBMI = font.render("My BMI: " + str(round(bmi,2)), True, BLUE, GREEN)
textSurfaceObj = None
# 输入框设置
input_box = pygame.Rect(220, 100, 200, 32)
input_box2 = pygame.Rect(220, 200, 200, 32)
input_box3 = pygame.Rect(270, 300, 100, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('red')
color_weight = pygame.Color('red')
color= color_inactive
color2 = color_inactive
input_text = ''
input_text_weight = ""
 
# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                state = 1
                color = color_active
                color2 = color_inactive
            elif input_box2.collidepoint(event.pos):
                state = 2
                color2 = color_weight
                color = color_inactive
            elif input_box3.collidepoint(event.pos):
                BmiData = SaveLoad.Delete()
                color = color_inactive
                color2 = color_inactive
            else:
                state = 0
                color = color_inactive
                color2 = color_inactive
        elif event.type == KEYDOWN:
            if state == 1:
                if event.key == K_RETURN:
                    try:
                        # 尝试将输入转换为浮点数
                        new_value = float(input_text)
                        height_cm = new_value
                        height_m = height_cm / 100
                        bmi = weight / (height_m ** 2)
                        textBMI = font.render("My BMI: " + str(round(bmi,2)), True, BLUE, GREEN)
                        textHeight = font.render("Height (cm): " + str(height_cm), True, BLUE, GREEN)
                        textSurfaceObj = font.render(State.UpdateBmiState(bmi), True, BLUE, GREEN)
                        BmiData.append(bmi)
                        SaveLoad.Save(BmiData)

                    except ValueError:
                        # 输入不是有效的数字，忽略
                        pass
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
            if state == 2:
                if event.key == K_RETURN:
                    try:
                        # 尝试将输入转换为浮点数
                        new_value = float(input_text_weight)
                        weight = new_value
                        bmi = weight / (height_m ** 2)
                        textBMI = font.render("My BMI: " + str(round(bmi,2)), True, BLUE, GREEN)
                        textWeight = font.render("Weight (kg): " + str(weight), True, BLUE, GREEN)
                        textSurfaceObj = font.render(State.UpdateBmiState(bmi), True, BLUE, GREEN)
                        BmiData.append(bmi)
                        SaveLoad.Save(BmiData)
                    except ValueError:
                        # 输入不是有效的数字，忽略
                        pass
                elif event.key == K_BACKSPACE:
                    input_text_weight = input_text_weight[:-1]

                else:
                    input_text_weight += event.unicode
 
    # 更新屏幕
    screen.fill(WHITE)  # 填充背景色
    txt_surface = font.render("Height:"+input_text, True, color)  # 渲染文本
    txt_surface_weight = font.render("Weight:"+input_text_weight, True, color2)
    txt_surface_del = font.render("DeleteFile", True, pygame.Color('lightskyblue3'))
    input_box.w = max(200, txt_surface.get_width() + 10)  # 调整输入框宽度
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))  # 绘制文本到屏幕
    screen.blit(txt_surface_weight, (input_box2.x + 5, input_box2.y + 5))
    screen.blit(txt_surface_del, (input_box3.x + 5, input_box3.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)  # 绘制输入框
    pygame.draw.rect(screen, color2, input_box2, 2)  # 绘制输入框
    pygame.draw.rect(screen, pygame.Color('lightskyblue3'), input_box3, 2)
    screen.blit(textWeight, p1)
    screen.blit(textHeight, p2)
    screen.blit(textBMI, p3)
    Draw()
    if BmiData:
        avg_bmi = sum(BmiData)/len(BmiData)
        max_bmi = max(BmiData)
        min_bmi = min(BmiData)
        stats_text = f"times: {len(BmiData)} average: {avg_bmi:.1f} max: {max_bmi:.1f} min: {min_bmi:.1f}"
        stats_surface = font.render(stats_text, True, BLACK)
        screen.blit(stats_surface, (20, 420))
    if textSurfaceObj is not None:
        screen.blit(textSurfaceObj, p4)
    pygame.display.flip()  # 更新整个屏幕
 
pygame.quit()
sys.exit()
