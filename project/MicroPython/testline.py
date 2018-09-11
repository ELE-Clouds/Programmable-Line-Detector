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

'''******************************************************************************
* 文  件：testline.py
* 概  述：当前模块主要用于测试调用调用相关模块或程序完成相应动作。
* 版  本：V0.10
* 作  者：Robin Chen
* 日  期：2018年7月26日
* 历  史： 日期             编辑           版本         记录
          2018年7月26日    Robin Chen      V0.10       创建文件

******************************************************************************'''
from wiretest import WIRETEST
from GUI import *
from machine import Pin
from pyb import Timer
from time import sleep_ms
from keyboard import KEYBOARD

lin = (Pin('C1'), Pin('C0'), Pin('C13'), Pin('C5'), Pin('C4'), Pin('A6'), Pin('A5'),  Pin('A4'))
lout = (Pin('A13'), Pin('A14'), Pin('A15'), Pin('B4'), Pin('B1'), Pin('B0'), Pin('B12'), Pin('B9'))
wt = WIRETEST(lin, lout)

# 按键引脚
p = Pin('B3')

# 定时器,按键时钟使用
s = Timer(1)

# 经过处理的测试记录
tuTest = ()

# 经过处理的学习记录
tuStu = ()

bLab = 0         # 按键点击状态标志字
guangbiao = 1    # 光标位置计数


# 菜单的字典格式
diMenu = {'WCSD': ('WCSD MENU', 'TEST', 'STUDAY', 'VIEW', 'ABOUT'), 'VIEW': ('VIEW MENU', 'TEST LOG', 'STUDAY LOG', 'BACK'), 'ABOUT': ('ABOUT', '', 'Wire Connecting', 'State Detector', 'V 1.00')}

# 主菜单与子菜单标题元组
lMenu = ('WCSD', 'VIEW', 'ABOUT')

# 主菜单标题
menu = diMenu['WCSD']

# 学习函数
def stu():
    doView("Studaying...", 10, 30)
    wt.doScan("LineSequence.stu")
    doReportGo('STULOG')
    return True

# 测试函数
def test():
    global tuTest
    tuTest = ()
    doView('Test Start....', 10, 30)
    bTets, tuTest = wt.doTest()
    if not bTets:
        sleep_ms(3000)
        return False
    else:
        doView("PASS!!!.", 10, 30)
        sleep_ms(3000)
        return True

# 长按按键事件
def evn_long():
    global bLab
    bLab = 3

# 在指定位置显示文字
def doView(text, x, y):
    oled.fill(0)
    oled.text(text, x, y)
    oled.show()

# 连续点击事件
def evn_con(con):
    global bLab
    if con == 1:
        bLab = 1
    elif con == 2:
        bLab = 2


'''
*************************************************************************
* 名    称：报告显示与查阅
* 说    明：
* 输入参数：
         sta:报告阅读状态标志字，通常为 TESTLOG：测试报告    STULOG: 学习报告（记录）
* 输出参数：None
* 返 回 值：None
**************************************************************************'''
def doReportGo(sta):
    global bLab, tuStu
    mjs = 0
    bLab = 0
    if sta == 'TESTLOG':
        if tuTest == ():
            doView("No have Log!", 10, 30)
            sleep_ms(3000)
        else:
            repView(tuTest, mjs % len(tuTest), ty='ERR')
    elif sta == 'STULOG':
        tuStu = ()
        tempStu = wt.getLog("LineSequence.stu")
        for i in range(len(tempStu)):
            tuStu = tuStu + ((i + 1, tempStu[i], ''),)
        if tuStu == ():
            doView("No have Log!", 10, 30)
            sleep_ms(3000)
        else:
            repView(tuStu, mjs % len(tuStu), ty='STU')
    while True:
        if bLab == 1:
            mjs += 1
            if sta == 'TESTLOG':
                repView(tuTest, mjs % len(tuTest), ty='ERR')
            elif sta == 'STULOG':
                repView(tuStu, mjs % len(tuStu), ty='STU')
            bLab = 0
        elif bLab == 2:
            bLab = 0
            break


sw = KEYBOARD(p, s, 0, evn_long, evn_con, "UP")
oledView(menu, 1)
menuLab = 'MENU'
tuStu = wt.getLog("LineSequence.stu")
while True:
    if bLab == 1:    # 检测到按钮当前单击
        if menu[0] != 'ABOUT':
            # 光标循环处理
            guangbiao = (guangbiao + 1)%len(menu)
            if guangbiao == 0:
                guangbiao = 1
            oledView(menu, guangbiao)
        bLab = 0
        #oledMenu(menunum, guangbiao)
    elif bLab == 2:
        if menu[guangbiao] in lMenu:               # 如果当前菜单项下有子菜单
            menu = diMenu[menu[guangbiao]]
            if menu[0] == "ABOUT":
                oledView(menu)
            else:
                guangbiao = 1
                oledView(menu, guangbiao)
        else:
            if menu[guangbiao] == 'TEST':           # 测试问题线路
                test()
                menuLab = 'TESTLOG'
                if tuTest:
                    doReportGo(menuLab)
                menuLab = 'MENU'
            elif menu[guangbiao] == 'STUDAY':       # 学习、记忆标准线路
                stu()
                menuLab = 'STULOG'
                if tuStu:
                    doReportGo(menuLab)
                menuLab = 'MENU'
            elif menu[guangbiao] == 'TEST LOG':     # 查看测试报告
                # 此处由代码演示按钮翻页效果
                menuLab = 'TESTLOG'
                if tuTest:
                    doReportGo(menuLab)
                else:
                    doView("No have Log!", 10, 30)
                    sleep_ms(3000)
                menuLab = 'MENU'
            elif menu[guangbiao] == 'STUDAY LOG':    # 查看学习记录
                menuLab = 'STULOG'
                if tuStu:
                    doReportGo(menuLab)
                else:
                    doView("Studaying...", 10, 30)
                menuLab = 'MENU'
            elif menu[guangbiao] == 'BACK':          # 返回上一层菜单
                menu = diMenu[lMenu[0]]
                guangbiao = 3
            else:
                menu = diMenu[lMenu[0]]
            oledView(menu, guangbiao)
        bLab = 0
    # 为防止误操作将已学习的记录覆盖或损坏，在此增加长按3秒恢复默认设置（即一对一直连模式）
    elif bLab == 3:
        print("开始恢复默认设置！")
        wt.setDefault("LineSequence.stu")
        print("当前设置已恢复默认设置！")
        doView("Default Seted!...", 10, 30)
        sleep_ms(1500)
        bLab = 0