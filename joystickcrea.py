"""
@file maze_game.py
@description ESP32迷宫逃脱游戏 - MicroPython版本
@author Claude
@date 2024
"""

from machine import Pin, I2C, ADC, PWM
import ssd1306
import time

# OLED显示屏设置
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# 初始化I2C
i2c = I2C(scl=Pin(22), sda=Pin(21))  # ESP32的I2C引脚
display = ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)

# 引脚定义
joystick_x = ADC(34)  # ESP32的ADC1_CH6
joystick_y = ADC(35)  # ESP32的ADC1_CH7
buzzer = PWM(Pin(25), freq=1000, duty=0)  # ESP32的GPIO25

# 摇杆阈值设置
JOYSTICK_THRESHOLD_LOW = 1000   # 低阈值
JOYSTICK_THRESHOLD_HIGH = 3000  # 高阈值
JOYSTICK_DEADZONE = 500         # 死区范围

# 游戏参数
BALL_SIZE = 4
WALL_THICKNESS = 2
START_X = 5
START_Y = 5
END_X = 120
END_Y = 55
END_SIZE = 6
ball_x = START_X
ball_y = START_Y

# 迷宫墙壁坐标 (x, y, width, height)
WALLS = [
    # 外边框
    (0, 0, 128, 2),      # 上边界
    (0, 0, 2, 64),       # 左边界
    (0, 62, 128, 2),     # 下边界
    (126, 0, 2, 64),     # 右边界
    
    # 主要障碍物
    (20, 10, 88, 2),     # 上横墙
    (20, 30, 88, 2),     # 中横墙
    (20, 50, 88, 2),     # 下横墙
    
    # 垂直障碍物
    (40, 10, 2, 20),     # 左竖墙1
    (60, 10, 2, 20),     # 中竖墙1
    (80, 10, 2, 20),     # 右竖墙1
    (40, 30, 2, 20),     # 左竖墙2
    (60, 30, 2, 20),     # 中竖墙2
    (80, 30, 2, 20),     # 右竖墙2
    (40, 50, 2, 10),     # 左竖墙3
    (60, 50, 2, 10),     # 中竖墙3
    (80, 50, 2, 10),     # 右竖墙3
]

def get_joystick_direction(x_value, y_value):
    """
    获取摇杆方向
    @param x_value: X轴值
    @param y_value: Y轴值
    @return: (dx, dy) 移动方向
    """
    dx = 0
    dy = 0
    
    # X轴方向判断
    if x_value < JOYSTICK_THRESHOLD_LOW:
        dx = -2  # 左移
    elif x_value > JOYSTICK_THRESHOLD_HIGH:
        dx = 2   # 右移
    
    # Y轴方向判断
    if y_value < JOYSTICK_THRESHOLD_LOW:
        dy = -2  # 上移
    elif y_value > JOYSTICK_THRESHOLD_HIGH:
        dy = 2   # 下移
    
    return dx, dy

def calibrate_joystick():
    """
    校准摇杆
    @return: (x_center, y_center) 中心点值
    """
    print("请将摇杆保持在中心位置...")
    time.sleep(2)
    
    # 读取10次取平均值
    x_sum = 0
    y_sum = 0
    for _ in range(10):
        x_sum += joystick_x.read()
        y_sum += joystick_y.read()
        time.sleep(0.1)
    
    x_center = x_sum // 10
    y_center = y_sum // 10
    
    print(f"校准完成 - X中心: {x_center}, Y中心: {y_center}")
    return x_center, y_center

def check_collision(x, y):
    """
    检测碰撞
    @param x: 小球X坐标
    @param y: 小球Y坐标
    @return: 是否发生碰撞
    """
    for wall in WALLS:
        if (x >= wall[0] and x <= wall[0] + wall[2] and
            y >= wall[1] and y <= wall[1] + wall[3]):
            return True
    return False

def play_collision_sound():
    """播放碰撞音效"""
    buzzer.duty(512)  # 50%占空比
    time.sleep(0.1)
    buzzer.duty(0)

def play_win_sound():
    """播放胜利音效"""
    # 播放上升音阶
    for freq in [440, 554, 659, 880]:
        buzzer.freq(freq)
        buzzer.duty(512)
        time.sleep(0.1)
        buzzer.duty(0)
        time.sleep(0.05)

def check_win():
    """
    检查是否到达终点
    @return: 是否获胜
    """
    return (abs(ball_x - END_X) < END_SIZE and 
            abs(ball_y - END_Y) < END_SIZE)

def display_win_message():
    """显示胜利信息"""
    display.fill(0)
    display.text("FINISH!", 40, 25, 1)
    display.text("Press Reset", 30, 40, 1)
    display.show()
    time.sleep(2)

def reset_game():
    """重置游戏"""
    global ball_x, ball_y
    ball_x = START_X
    ball_y = START_Y

def main():
    """主循环"""
    global ball_x, ball_y
    
    # 校准摇杆
    x_center, y_center = calibrate_joystick()
    
    while True:
        # 读取摇杆值
        x_value = joystick_x.read()
        y_value = joystick_y.read()
        
        # 获取移动方向
        dx, dy = get_joystick_direction(x_value, y_value)
        
        # 计算新位置
        new_x = ball_x + dx
        new_y = ball_y + dy
        
        # 检查碰撞
        if not check_collision(new_x, new_y):
            ball_x = new_x
            ball_y = new_y
        else:
            # 碰撞效果
            play_collision_sound()
        
        # 检查是否获胜
        if check_win():
            play_win_sound()
            display_win_message()
            reset_game()
            continue
        
        # 更新显示
        display.fill(0)  # 清屏
        
        # 绘制墙壁
        for wall in WALLS:
            display.fill_rect(wall[0], wall[1], wall[2], wall[3], 1)
        
        # 绘制终点
        display.fill_rect(END_X - END_SIZE//2, END_Y - END_SIZE//2,
                         END_SIZE, END_SIZE, 1)
        
        # 绘制小球
        display.fill_rect(ball_x - BALL_SIZE//2, ball_y - BALL_SIZE//2,
                         BALL_SIZE, BALL_SIZE, 1)
        
        display.show()
        time.sleep(0.05)

if __name__ == "__main__":
    main()