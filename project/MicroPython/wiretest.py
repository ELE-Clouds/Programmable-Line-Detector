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
* 文  件：wiretest.py
* 概  述：当前模块主要用于线路检测，并返回检测结果。
* 版  本：V0.10
* 作  者：Robin Chen
* 日  期：2018年7月26日
* 历  史： 日期             编辑           版本         记录
          2018年7月26日    Robin Chen      V0.10       创建文件
`
******************************************************************************'''
from time import sleep_ms

class WIRETEST:
    def __init__(self, _lIN, _lOUT):
        self.lin = _lIN
        self.lout = _lOUT

        # 接收端初始化，注意，如果实际电路中使用了外部下拉或芯片内部无内部下拉，请取消此处的下拉声明。
        for i in self.lin:
            i.init(i.IN, i.PULL_DOWN)

        # 发送端初始化
        for o in self.lout:
            o.init(o.OUT)
            o.value(0)

    '''*************************************************************************
    * 功   能：线路扫描
    * 说   明：给线路一端加高电平，检测另一端是高电平还是低电平。
    * 输入参数：
                _filName: 文件名
    * 输出参数：None
    * 返 回 值：
    *          lScan : 扫描结果，16进制形式的 tule。
    **************************************************************************'''
    def doScan(self, _filName = None):
        lScan2 = ()
        bLab = 0
        while True:
            lScan = ()
            for o in self.lout:
                o.value(1)
                iValue = 0
                for i in self.lin:
                    iValue = (iValue << 1) | i.value()
                lScan += (hex(iValue),)
                o.value(0)
            sleep_ms(10)

            # 重复扫描连续5次结果一致算通过，否则重新计数，直到满足条件为止。
            if lScan == lScan2:
                bLab += 1
            else:
                bLab = 0
            if bLab > 5:
                if _filName == None:
                    return lScan
                else:
                    # 将扫描记录写入指定的文件
                    sep = ','
                    f = open(_filName, 'w')
                    f.write(sep.join(lScan))
                    f.close()
                break
            lScan2 = lScan
        return True


    '''*************************************************************************
    * 功   能：检测线路状态
    * 说   明：
    * 输入参数：None
    * 输出参数：None
    * 返 回 值：True
    **************************************************************************'''
    def doTest(self):
        tuResult=()   # 错误信息元组格式
        lmemory = self.getLog("LineSequence.stu")
        #print('文件中提取得到的线序：', lmemory)
        lLineSeq = self.doScan()
        #print("待测线缆扫描结果（线序）：", lLineSeq)
        if lmemory == lLineSeq:
            return True, tuResult
        else:
            for j in range(len(lLineSeq)):
                if lLineSeq[j] != lmemory[j]:
                    if lLineSeq[j] == '0x0':  # 开（断）路
                        strErr = "Open circuit!"
                    elif lLineSeq[j] != '0x0' and not (lLineSeq[j] in lmemory):  # 短路
                        strErr = "Short circuit!"
                    elif lLineSeq[j] != '0x0' and (lLineSeq[j] in lmemory):  # 错序
                        strErr = "Wrong order!"
                    tuResult = tuResult + ((j+1, lLineSeq[j], strErr),)  # 结果中有问题的序号+内容组成的字典
            return False, tuResult

    '''*************************************************************************
    * 功   能：获取学习记录文件内容
    * 说   明：
    * 输入参数：
               _filName: 记录文件名
    * 输出参数：None
    * 返 回 值：
               temp：记录内容，元组。
    **************************************************************************'''
    def getLog(self, _filName):
        f = open(_filName, 'r')
        temp = f.readline()
        f.close()
        temp = tuple(temp.split(','))
        return temp


    '''*************************************************************************
    * 功   能：恢复默认设置
    * 说   明：将当前设置文件恢复到初始状态（1对1直连）
    * 输入参数：
               _filName: 记录文件名
    * 输出参数：None
    * 返 回 值：None
    **************************************************************************'''
    def setDefault(self, _filName):
        temp = ('0x80', '0x40', '0x20', '0x10', '0x8', '0x4', '0x2', '0x1')
        sep = ','
        f = open(_filName, 'w')
        f.write(sep.join(temp))
        f.close()
        return True