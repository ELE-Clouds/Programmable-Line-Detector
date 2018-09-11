# -*- coding:UTF-8 -*-

'''
MIT License
Copyright (c) 2018 Robin Chen
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

'''
******************************************************************************
* 文  件：GUI.py
* 概  述：当前模块主要用于OLED(SSD1306)屏画面显示。
* 版  本：V0.10
* 作  者：Robin Chen
* 日  期：2018年7月26日
* 历  史： 日期             编辑           版本         记录
          2018年7月26日    Robin Chen      V0.10       创建文件
`
******************************************************************************'''
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from time import sleep_ms
i2c = I2C(scl= Pin("C2"), sda= Pin("C3"))
oled = SSD1306_I2C(128, 64, i2c)

oled.text("Hellow MicroPython!", 0, 30)
oled.show()
sleep_ms(1000)
oled.fill(0)
oled.show()

'''*************************************************************************
* 功   能：图示显示
* 说   明：报告（包括问题报告与学习报告）界面图示显示。
* 输入参数：
          x: 横坐标
          y: 纵坐标
          l: 显示图形的二进制制编码，通常用16进制形式表示。
* 输出参数：None
* 返 回 值：True
**************************************************************************'''
def dhView(x, y, l):
    l = int(l)    # 将字符串型16进制数转换为整型16进制数
    # ll = list(bin(1 << 8 | l)[3:])[::-1]
    ll = bin(1 << 8 | l)[3:]
    #print('ll = ',ll)
    oled.framebuf.fill_rect(x, y, 108, 8, 0)
    for i in range(8):
        if ll[i] == '1':
            oled.framebuf.fill_rect((x + 14 * i), y, 8, 8, 1)
        else:
            oled.framebuf.rect((x + 14 * i), y, 8, 8, 1)
    oled.show()

'''*************************************************************************
* 功   能：报告显示
* 说   明：根据提供的参数，判断当前当部属于哪种类型，并返回错误提示。
* 输入参数：
          l1: 源线号,整型值，1~8
          l2: 待测线路显示位，二进制处理，16进制表示。
          x:  图形区域的起始位置x坐标
          y:  图形区域的起始位置y坐标
          cont: 位置图示闪烁次数，为 -1 时一直闪烁，为 0 时不闪烁。
* 输出参数：None
* 返 回 值：True
**************************************************************************'''
def oledFlash(l1, l2, x=20, y=0, cont = 1):
    n = 128 >> (int(l1) - 1)
    oled.framebuf.fill_rect(0, 0, 128, 35, 0)
    oled.text("S:", 0, y)
    oled.text("T:", 0, (y+14))
    oled.framebuf.hline(0, (y + 26), 128, 1)
    while cont:
        dhView(x, y, 0x00)
        dhView(x, (y + 14), 0x00)
        sleep_ms(500)
        dhView(x, y, n)
        dhView(x, (y + 14), l2)
        sleep_ms(500)
        cont -= 1


'''*************************************************************************
* 名    称：问题信息显示
* 说    明：显示错误信息（线路号和故障原因（开路、短路、错序））
* 输入参数：
          znum：总页数
          nonum：当前页码
          err：错误内容
          _line：线号
* 输出参数：None
* 返 回 值：True
**************************************************************************'''
def viewReportText(strTitle, strR1, strR2):
    oled.framebuf.fill_rect(0, 35, 128, 29, 0)
    oled.text(strTitle, 0, 35)
    oled.text(strR1, 10, 45)
    oled.text(strR2, 10, 56)
    oled.show()



'''*************************************************************************
* 名    称：菜单显示与处理
* 说    明：在屏幕上显示菜单，并根据按键的操作来显示不同的菜单界面。
* 输入参数：
         _lmenu:菜单内容，tule格式，0位为菜单标题。
         _gb: 光标所在行号，默认为None(不显示)。
* 输出参数：None
* 返 回 值：True
**************************************************************************'''
def oledView(_lmenu, _gb = None):
    oled.fill(0)
    oled.text(_lmenu[0], ((128 - (len(_lmenu[0])*8)) // 2), 5)
    oled.framebuf.hline(0, 20, 128, 1)
    for i in range(len(_lmenu))[1:]:
        oled.text(_lmenu[i], ((128 - (len(_lmenu[i])*8)) // 2), (i*10+15))
    if _gb != None:
        if _gb == 0:
            _gb += 1
        oled.text(">", (((128 - (len(_lmenu[_gb])*8)) // 2) - 16), (_gb * 10 + 15))
        oled.text("<", (((128 - (len(_lmenu[_gb]) * 8)) // 2) + (len(_lmenu[_gb]) * 8) + 8), (_gb * 10 + 15))
    oled.show()


'''*************************************************************************
* 名    称：报告显示与翻页效果
* 说    明：在报告页面按下翻页按钮后，报告将向后轮循翻页，同时适用检测报告与学习报告
* 输入参数：
         _drReport:报告内容，包含线号、报告内容、报告说明。格式为：((linenumber,0x00, "note"), (linenumber,0x00, "note"),...)
         _gb: 报告页码，整型，值为 1~ max
         ty：报告类型，字符串型，通常为 'ERR' 或 'STU'
* 输出参数：None
* 返 回 值：None
**************************************************************************'''
def repView(_drReport, _gb, ty = 'ERR'):
    l1 = _drReport[_gb][0]
    l2 = _drReport[_gb][1]
    strTitle = ty + ' ' + str(len(_drReport)) + '-' + str(_gb + 1) + '     >>'
    strR1 = 'Line ' + str(_drReport[_gb][0])
    strR2 = _drReport[_gb][2]
    viewReportText(strTitle, strR1, strR2)
    oledFlash(l1, l2, cont=3)
    return True



