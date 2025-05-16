from machine import Pin, ADC
from time import sleep

# 設定 LED 腳位
led_up = Pin(16, Pin.OUT)    # D1
led_down = Pin(17, Pin.OUT)  # D2
led_left = Pin(18, Pin.OUT)  # D3
led_right = Pin(19, Pin.OUT) # D4

# 設定搖桿的 X/Y 軸輸入
joystick_x = ADC(34)  # X軸接A0
joystick_y = ADC(35)  # Y軸接A1（根據實際接線調整）

# 設定搖桿按鈕腳位（假設接在D5）
button = ADC(36)

# 閾值設定
CENTER = 512     # 中心值
THRESHOLD = 150  # 靈敏度範圍

def clear_leds():
    led_up.off()
    led_down.off()
    led_left.off()
    led_right.off()

def all_leds_on():
    led_up.on()
    led_down.on()
    led_left.on()
    led_right.on()

while True:
    # 檢查按鈕是否按下（低電平表示按下）
    if button.read() == 0:
        all_leds_on()
        sleep(2)      # 維持亮起2秒
        clear_leds()
        sleep(0.2)    # 防抖延遲
        continue      # 跳過本次循環剩餘部分

    # 讀取搖桿數值
    x_val = joystick_x.read()
    y_val = joystick_y.read()

    clear_leds()  # 每次循環先重置LED

    # 處理X軸左右控制
    if x_val < CENTER - THRESHOLD:
        led_left.on()
    elif x_val > CENTER + THRESHOLD:
        led_right.on()

    # 處理Y軸上下控制
    if y_val < CENTER - THRESHOLD:
        led_up.on()
    elif y_val > CENTER + THRESHOLD:
        led_down.on()

    sleep(0.1)