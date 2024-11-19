import cv2
import numpy
import libadb
import logging
import time
from time import sleep
import math
import sys
from datetime import timedelta

# 设置日志记录器
logger = logging.getLogger(__name__)
# 定义每个区块的大小
block_size = 55
def format_timedelta(td):
    td = timedelta(seconds=td)
    # 将timedelta对象格式化为日小时分钟秒的字符串
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}:{hours}:{minutes}:{seconds}"
# 计算给定区域中黑色像素的百分比
def get_black_percent(mat, x0, x1, y0, y1):
    num = 0
    for x in range(x0, x1):
        for y in range(y0, y1):
            color_data = mat[x][y]
            # 如果RGB值都小于或等于120，则认为是黑色
            if color_data[0] <= 120 and color_data[1] <= 120 and color_data[2] <= 120:
                 num += 1
    # 返回黑色像素的百分比
    return num / ((x1 - x0) * (y1 - y0))

# 计算给定区域中特定颜色像素的百分比
def get_color_percent(mat, color):
    num = 0
    for line in mat:
        for pixel in line:
            color_data = pixel
            # 如果RGB值都大于或等于指定颜色，则认为是目标颜色
            if (color_data[0] >= color[0]) and (color_data[1] >= color[1]) and (color_data[2] >= color[2]):
                 num += 1
    # 返回目标颜色像素的百分比
    return num / 3200

if __name__ == "__main__":
    # 设置日志级别为DEBUG
    logger.setLevel(logging.DEBUG)
    # 创建adb对象并连接到设备
    d = libadb.adb()
    d.connect("127.0.0.1:16384")
    # 初始化变量
    count_ctx = False
    all = 0
    starttime = time.time()
    lasttime = time.time()
    
    # 进入主循环
    while True:
        sleep(1)
        # 捕获屏幕截图
        img_pil = d.screencap()
        # 将截图转换为OpenCV格式
        img_cv2 = cv2.cvtColor(numpy.asarray(img_pil), cv2.COLOR_RGB2BGR)

        matrix_tag = img_cv2[355:415, 100:185]  # 用于检测特定颜色的区域
        # cv2.imshow('img3', matrix_tag)
        # cv2.waitKey(1)
        # 计算特定颜色（品红色）的百分比
        magenta_percent = get_color_percent(matrix_tag, (98, 44, 188))
        # 如果品红色百分比小于0.8，则跳过本次循环
        if magenta_percent >= 0.8 and count_ctx is False:
            count_ctx = True
        elif magenta_percent < 0.8 and count_ctx:
            count_ctx = False
            continue
        else:
            # print(f"未知情况：{magenta_percent,count_ctx}")
            continue
        sleep(1)
        
        # 获取图像的尺寸
        height, width, _ = img_cv2.shape
        # print(height, width)
        # 从截图中提取两个区域
        py = -25
        matrix_1 = img_cv2[253+py:543+py, 185:475]
        matrix_2 = img_cv2[600-5:890-5, 177:467]
        # cv2.imshow('img1', matrix_1)
        # cv2.imshow('img2', matrix_2)
        


            
        # 将两个区域相加
        imgadd = cv2.add(matrix_1,matrix_2)
        # 转换为灰度图
        img_gray = cv2.cvtColor(imgadd,cv2.COLOR_RGB2GRAY)
        # 转换回BGR格式
        img_rgb = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2BGR)
        # 应用阈值处理得到二值图像
        ret,thresh = cv2.threshold(img_rgb,250,255,cv2.THRESH_BINARY)
        # cv2.imshow('img', thresh)
        # 初始化跳过循环的标志
        
        # 初始化存储每个区块黑色百分比的矩阵
        matrix = []
        for x in range(0, 5):
            row = []
            for y in range(0, 5):
                # 定义每个区块的坐标
                rect_x1 = 15 + x * block_size
                rect_x2 = 50 + x * block_size
                rect_y1 = 15 + y * block_size
                rect_y2 = 50 + y * block_size
                # 在二值图像上绘制矩形框
                cv2.rectangle(thresh, (rect_x1,rect_y1), (rect_x2, rect_y2), (0, 255, 0), 0)
                # 计算当前区块的黑色百分比
                black_percent = get_black_percent(thresh, rect_x1, rect_x2, rect_y1, rect_y2)
                # 将结果添加到行中
                row.append(black_percent)
            matrix.append(row)

        # 计算非零区块的数量
        count = 0
        for row in matrix:
            for block in row:
                if block != 0.0:
                    count += 1

        # print('tap: clear')
        d.tap(729, 1145)  # 清除
        # print(count)
        # 根据count的值执行相应的点击操作
        for i in str(count):
            match i:
                case '0':
                    # print('tap: 0')
                    d.tap(208, 1138)
                case '1':
                    # print('tap: 1')
                    d.tap(107, 1274)
                case '2':
                    # print('tap: 2')
                    d.tap(287, 1274)
                case '3':
                    # print('tap: 3')
                    d.tap(460, 1274)
                case '4':
                    # print('tap: 4')
                    d.tap(640, 1274)
                case '5':
                    # print('tap: 5')
                    d.tap(808, 1274)
                case '6':
                    # print('tap: 6')
                    d.tap(206, 1397)
                case '7':
                    # print('tap: 7')
                    d.tap(381, 1395)
                case '8':
                    # print('tap: 8')
                    d.tap(550, 1390)
                case '9':
                    # print('tap: 9')
                    d.tap(725, 1401)
            # 等待100毫秒
            cv2.waitKey(100)
        thistime = time.time()
        mytime = thistime - lasttime #本轮运行时间
        runtime = thistime - starttime #总运行时间
        lasttime = thistime #上次时间
        # 显示处理后的图像
        # cv2.imshow('img', thresh)
        # cv2.waitKey(200)
        all += 1
        # print(f"└┈ {all} 轮output 用时{mytime:.2f}s")
        temp = pow(10,math.floor(math.log10(all))+1)
        sy = (temp-all)*mytime
        # 计算当前进度百分比  
        progress = (all / temp) * 100  
        # 估算剩余时间（基于当前进度和已用时间）  
        if progress > 0:  
            estimated_remaining_time = sy 
        else:  
            estimated_remaining_time = 0  # 如果进度为0，则剩余时间为0  
        # 清除当前行（为了在同一行更新进度条）  
        # 注意：在Windows上可能需要使用'\r'而不是'\r\n'  
        sys.stdout.write('\r')  
        # 显示进度条  
        intpro = int(progress / 2)
        # 使用50个字符的宽度来显示进度，可以根据需要调整  
        progress_bar = '[' + '=' * intpro + ' ' * (50 - intpro) + ']'  
        # 注意：这里的'/2'是为了让进度条更紧凑，因为我们要用50个字符表示100%的进度  
  
        # 格式化并打印进度、时间和剩余时间  
        print(f'{all}=>{temp}|{progress_bar}{progress:.2f}%|运行:{format_timedelta(runtime)}|剩余:{format_timedelta(estimated_remaining_time)}     ', end='')  
        sys.stdout.flush()
