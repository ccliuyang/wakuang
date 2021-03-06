# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 09:47:46 2017

@author: 310128142
"""
import datetime
import sys
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph as pg
import talib
import tushare as ts
from matplotlib.widgets import Button, RadioButtons, Slider
from pyqtgraph.Qt import QtCore, QtGui


class My_index(object):
    def __init__(self, stock_code=None, figSN=None):
        self.today = datetime.date.today()
        if stock_code is None:
            self.code = "sh"
        else:
            self.code = stock_code
        self.startDate = '2016-12-31'
        self.endDate = datetime.datetime.strftime(datetime.datetime.today(),
                                                  '%Y-%m-%d')
        self.MACD_fastperiod = 10  #MACD快速参数
        self.MACD_slowperiod = 20  #MACD慢速参数
        self.MACD_signalperiod = 9  #MACD 权重
        if figSN is None:  # figSN is figuer number
            self.fig = 1
        else:
            self.fig = figSN  # this is show which figure
        self.SN_plt = 0  # show how many
        self.df = pd.DataFrame(self.get_data_ts())

    def _get_stock_date(self):
        pass

    def get_data_ts(self):  #获取开始数据
        try:
            self.code_data = ts.get_k_data(
                self.code, self.startDate, end=self.endDate)

        except ValueError:

            print('Input code is wrong/输入代码错误.')
        else:
            self.code_data = self.code_data.sort_index(ascending=True)  # 从后倒序

            self.code_data.date = self.code_data.date.apply(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
            #self.code_data.date=self.code_data.date.apply(lambda x:matplotlib.dates.date2num(x))
            self.code_data = self.code_data.set_index('date')
            if self.endDate == '%s' % self.today:
                todat_realtime = ts.get_realtime_quotes(self.code)
                realtime_price = float(todat_realtime.price)
                realtime_high = float(todat_realtime.high)
                realtime_low = float(todat_realtime.low)
                realtime_open = float(todat_realtime.open)
                realtime_volume = float(todat_realtime.volume)

                self.code_data.loc['%s' % self.today,
                                   'code'] = '%s' % self.code
                self.code_data.loc['%s' % self.today,
                                   'volume'] = '%s' % realtime_volume
                self.code_data.loc['%s' % self.today,
                                   'open'] = '%s' % realtime_open
                self.code_data.loc['%s' % self.today,
                                   'high'] = '%s' % realtime_high
                self.code_data.loc['%s' % self.today,
                                   'low'] = '%s' % realtime_low
                self.code_data.loc['%s' % self.today, 'close'] = realtime_price
            self.df = self.code_data
            return self.code_data

    def myMACD(self):
        self.df = self.df
        price = self.df['close'].values
        ewma12 = pd.ewma(price, span=self.MACD_fastperiod)
        ewma60 = pd.ewma(price, span=self.MACD_slowperiod)
        dif = ewma12 - ewma60
        dea = pd.ewma(dif, self.MACD_signalperiod)
        bar = (dif - dea)
        #print(bar)#有些地方的bar = (dif-dea)*2，但是talib中MACD的计算是bar = (dif-dea)*1
        return dif, dea, bar

    def myMACD2(self):
        self.df = self.df
        price = self.df['close'].values
        ewma12 = pd.Series(price).rolling(window=self.MACD_fastperiod).mean()
        ewma60 = pd.Series(price).rolling(window=self.MACD_slowperiod).mean()
        dif = ewma12 - ewma60
        dea = pd.ewma(dif, self.MACD_signalperiod)
        bar = (dif - dea
               )  #有些地方的bar = (dif-dea)*2，但是talib中MACD的计算是bar = (dif-dea)*1
        self.df['macd'] = dif
        self.df['signal'] = dea
        self.df['hist'] = bar
        return dif, dea, bar

    def sma(self, tp=None): #SMA index . default  tp  is 5 days
        if tp is None:
            tp = 5
        else:
            pass
        column_name = 'sma' + str(tp)
        self.df[column_name] = talib.func.SMA(self.df.close, timeperiod=tp)
        return self.df

    def draw_macd(self):
        ax1 = self.plot_init()

        macd, signal, hist = self.myMACD()

        plt.plot(self.df.index, self.df.close, "y")
        #plt.ylim(df.close.min()-3, df.close.max()+1)

        ax2 = ax1.twinx()
        plt.plot(self.df.index, macd, 'r', label='macd dif')
        plt.plot(self.df.index, signal, 'b', label='signal dea')

    def draw_macd2(self):
        ax1 = self.plot_init()
        #macd, signal, hist = talib.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)

        macd, signal, hist = self.myMACD2()
        #ax1=plt.subplot(111)

        plt.plot(self.df.index, self.df.close, "y")
        #plt.ylim(df.close.min()-3, df.close.max()+1)

        ax2 = ax1.twinx()
        plt.plot(self.df.index, macd, 'r', label='macd dif')
        plt.plot(self.df.index, signal, 'b', label='signal dea')
        #plt.bar(df.index,hist,'g',label='hist bar')
        #plt.plot(self.code_data.index,0*df.open,'--')

    # plt.ylim(-1, 3)

    def ST_bands(self):
        '''
        upperband   , 上轨  均线加一倍标准差
        middleband  ，中轨  均线
        lowerband   ，下轨  均线减一倍标准差
    
        '''
        upperband, middleband, lowerband = talib.BBANDS(
            self.df.close.values,
            timeperiod=10,
            nbdevup=2,
            nbdevdn=2,
            matype=0)

        self.df['upperband'] = upperband
        self.df['middleband'] = middleband
        self.df['lowerband'] = lowerband
        return self.df
        #print(df)

    def draw_bands(self):
        self.ST_bands()  #运行bans 数据
        plt.plot(self.df.index, self.df.close, 'b')
        plt.plot(self.df.index, self.df.upperband, 'r')
        plt.plot(self.df.index, self.df.middleband, 'k')
        plt.plot(self.df.index, self.df.lowerband, 'r')
        plt.legend(loc='best')
        plt.grid(True)

    '''
    RSI强弱指标
    
    '''

    def RSI_cal(self, timeperiod=10):  # price 加权平均指标
        #timeperiod=1
        if self.code == 'sh':
            timeperiod = 10

        self.df['RSI'] = talib.RSI(self.df.close.values,
                                   timeperiod)  #调用RSI函数计算RSI  因子设为10

    def draw_RSI(self):  # 画加权平均指数
        self.RSI_cal(self)
        fig, ax1 = self.plot_init()

        plt.plot(self.df.index, self.df.close, "k")
        #plt.ylim(df.close.min()-3, df.close.max()+1)
        ax2 = ax1.twinx()

        plt.plot(self.df.index, self.df.RSI, '-', c='y', label='RSI')

        plt.plot(self.df.index, 0 * self.df.open + 20, '--')
        plt.plot(self.df.index, 0 * self.df.open + 50, '--')
        plt.plot(self.df.index, 0 * self.df.open + 80, '--')

        self.polt_end(fig, )


class My_plot(QtGui.QWindow):
    def __init__(self, ):
        super(My_plot, self).__init__()
        self.win = pg.GraphicsWindow(title="技术指标")
        #self.win.resize(1000,600)
        self.win.setWindowTitle('技术指标: Plotting')
        self.data = My_index()
        pg.setConfigOptions(antialias=True)

    #设置
    def setCodeDate(self, **kwds):
        for kwd, value in kwds.items():

            if kwd in ('Code', 'start', 'end'):
                if not isinstance(value, str):
                    raise ValueError("Argument '%s' must be int" % kwd)

            if kwd == 'code':
                self.data.code = value
            if kwd == 'start':
                self.data.startDate = value
            if kwd == 'end':
                self.data.endDate = value

            self.data.get_data_ts()

    def Kline_plotting(self):

        #numd=self.data.df.reset_index()
        self.numd = self.data.df.reset_index()
        x = self.numd.date.apply(
            lambda x: datetime.datetime.strftime(x, "%Y-%m-%d"))
        self.xdict = dict(x)  #转换成字符串字典
        # LABEL 10个图标
        self.maxRegion = len(self.numd.index)
        t = len(self.numd.index) // 5
        #提取坐标点
        axis_date = [(i, list(x)[i])
                     for i in range(0, len(self.numd.index), t)]

        #stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis = pg.AxisItem(orientation='bottom')  #设置横轴
        stringaxis.setTicks([axis_date, self.xdict.items()])
        stringaxis.setGrid(255)
        stringaxis.setLabel(text='Dates')
        #stringaxis.setTickSpacing(100,1)
        self.k_plot = self.win.addPlot(
            row=1, col=0, title="kline", axisItems={'bottom': stringaxis})

        self.y = self.numd.close
        self.k_plot.plot(
            x=list(self.xdict.keys()), y=self.y.values, pen=(0, 255, 255))

        self.k_plot.showGrid(x=True, y=True)
        self.region = pg.LinearRegionItem()
        self.region.setZValue(self.maxRegion / 4 * 3)
        self.region.setRegion([self.maxRegion / 4 * 3, self.maxRegion])
        self.k_plot.addItem(self.region, ignoreBounds=True)

    def update_plotting(self):

        self.update_plot = self.win.addPlot(row=2, col=0, title="布林线")
        self.update_plot.setAutoVisible(y=True)
        self.data.ST_bands()
        upprband = self.data.df.upperband
        middleband = self.data.df.middleband
        lowerband = self.data.df.lowerband
        pen_band = pg.mkPen(color=(255, 0, 0), width=2)

        self.update_plot.plot(x=self.y.index, y=upprband.values, pen=pen_band)
        self.update_plot.plot(x=self.y.index, y=middleband.values, pen='w')
        self.update_plot.plot(x=self.y.index, y=lowerband.values, pen=pen_band)
        self.update_plot.plot(
            x=self.y.index, y=self.y.values, pen=(0, 255, 255))
        self.region.sigRegionChanged.connect(self.update)
        self.update_plot.sigRangeChanged.connect(self.updateRegion)
        self.update_plot.showGrid(x=True, y=True)
        self.region.setRegion([self.maxRegion // 4 * 2, self.maxRegion])

    def macd_plotting(self):

        t = len(self.numd.index) // 10

        axis_date = [(i, list(self.xdict.values())[i])
                     for i in range(0, len(self.numd.index), t)]
        stringaxis = pg.AxisItem(orientation='bottom')  #设置横轴
        stringaxis.setTicks([axis_date, self.xdict.items()])
        #stringaxis.setGrid(255)
        stringaxis.setLabel(text='Dates')
        self.macd_plot = self.win.addPlot(
            row=1, col=1, title="MACD", axisItems={'bottom': stringaxis})

        macd, signal, hist = self.data.myMACD()
        self.macd_plot.plot(
            x=self.y.index,
            y=macd,
            pen='r',
            fillLevel=0,
            fillBrush=(255, 0, 0, 50))
        self.macd_plot.plot(
            x=self.y.index,
            y=signal,
            pen='b',
            fillLevel=0,
            fillBrush=(0, 125, 255, 126))
        self.macd_plot.plot(x=self.y.index, y=self.y.index * 0, pen='w')

        self.macd_plot.setXLink(self.update_plot)
        self.macd_plot.showGrid(x=True, y=True)

    def macd_plotting2(self):
        self.macd_type = 1
        t = len(self.numd.index) // 10

        axis_date = [(i, list(self.xdict.values())[i])
                     for i in range(0, len(self.numd.index), t)]
        stringaxis = pg.AxisItem(orientation='bottom')  #设置横轴
        stringaxis.setTicks([axis_date, self.xdict.items()])
        #stringaxis.setGrid(255)
        stringaxis.setLabel(text='Dates')
        self.macd_plot2 = self.win.addPlot(
            row=2, col=1, title="MACD2", axisItems={'bottom': stringaxis})

        macd, signal, hist = self.data.myMACD2()
        self.macd_plot2.plot(
            x=self.y.index,
            y=macd.values,
            pen='r',
            fillLevel=0,
            fillBrush=(255, 0, 0, 50))
        self.macd_plot2.plot(
            x=self.y.index,
            y=signal.values,
            pen='b',
            fillLevel=0,
            fillBrush=(0, 125, 255, 126))
        self.macd_plot2.plot(x=self.y.index, y=self.y.index * 0, pen='w')
        self.macd_plot2.setXLink(self.update_plot)
        self.macd_plot2.showGrid(x=True, y=True)

    def RSI_plotting(self):
        t = len(self.numd.index) // 10

        axis_date = [(i, list(self.xdict.values())[i])
                     for i in range(0, len(self.numd.index), t)]
        stringaxis = pg.AxisItem(orientation='bottom')  #设置横轴
        stringaxis.setTicks([axis_date, self.xdict.items()])
        # stringaxis.setGrid(255)
        stringaxis.setLabel(text='Dates')

        self.RSI_plot = self.win.addPlot(
            row=2, col=1, title="RSI", axisItems={'bottom':
                                                  stringaxis})  #计算 RSI
        self.data.RSI_cal()
        RSI_values = self.data.df.RSI.values
        pen_RSI = pg.mkPen(color=(255, 0, 0), width=2)
        self.RSI_plot.plot(x=self.y.index, y=RSI_values, pen=pen_RSI)
        self.RSI_plot.plot(
            x=self.y.index, y=RSI_values * 0 + 20, pen=(255, 255, 0))
        self.RSI_plot.plot(
            x=self.y.index, y=RSI_values * 0 + 80, pen=(255, 255, 0))
        self.RSI_plot.showGrid(x=True, y=True)
        self.RSI_plot.setXLink(self.update_plot)  # 关联到放大图

    def update(self):
        self.region.setZValue(10)
        minX, maxX = self.region.getRegion()
        self.update_plot.setXRange(minX, maxX, padding=0)

    def updateRegion(self):
        self.region.setRegion(self.update_plot.getViewBox().viewRange()[0])

    def remove_plot(self):
        self.win.removeItem(self.macd_plot)
        self.win.removeItem(self.update_plot)
        self.win.removeItem(self.k_plot)
        self.win.removeItem(self.RSI_plot)


def Draw_main():
    app = QtGui.QApplication(sys.argv)
    to_plot = My_plot()
    to_plot.setCodeDate(code='600098', start='2015-01-01', end='2018-05-03')
    to_plot.Kline_plotting()
    to_plot.update_plotting()
    to_plot.macd_plotting()
    to_plot.RSI_plotting()
    to_plot.win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.exec_()


def test_My_index():
    stock = My_index()
    return stock


if __name__ == "__main__":
    Draw_main()
    s = test_My_index()
