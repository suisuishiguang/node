# 克隆自聚宽文章：https://www.joinquant.com/post/1511
# 标题：RSI衍生指标择时，轮动A股ETF
# 作者：JimZ

import numpy as np
import pandas as pd
import talib
import datetime
####带了止盈止损
####此函数在每个周期开始时用来设置buyableList####=====================
def set_buyableList(context):
    #选出上市时间超过g.onMarketDays天的ETF
    etfList = get_all_securities(['etf'], (context.current_dt - datetime.timedelta(g.onMarketDays)).date())
    etfList = list(etfList.index)
    #判断大盘强势程度，大盘强势时，向eftList加入分级b基金
    daPanHis = attribute_history('000300.XSHG', 100, '1d', 'close', df = False)
    daPan = daPanHis['close']
    upperband, middleband, lowerband = talib.BBANDS(daPan, timeperiod = 5, nbdevup = 1, nbdevdn = 1, matype = 0)
    #大盘昨收盘价站上布林线上轨时才确认大盘强势
    if daPan[-1] >= upperband[-1]:
        fjbList = get_all_securities(['fjb'], (context.current_dt - datetime.timedelta(g.onMarketDays)).date())
        fjbList = list(fjbList.index)
        etfList = etfList + fjbList
    #剔除标的为债券、黄金、港股的那部分
    etfList = [ security for security in etfList 
    if '港' not in get_security_info(security).display_name
    and '恒生' not in get_security_info(security).display_name
    and '纳' not in get_security_info(security).display_name 
    and '黄金' not in get_security_info(security).display_name
    and '债' not in get_security_info(security).display_name
    and 'MSCI' not in get_security_info(security).display_name ]
    #计算etfList中的etf过去g.period4Check4Money天平均成交金额，
    #取排名前百分之十，且至少取十只
    #第一步，取etfList中etf过去几天平均成交金额组成array
    money4CheckArray = np.array([])
    for security in etfList:
        his = attribute_history(security, g.period4Check4Money, '1d', ('money'), df = False)
        moneyArray = his['money']
        moneyAvg = np.sum(moneyArray) / g.period4Check4Money
        money4CheckArray = np.append(money4CheckArray, moneyAvg)
    #第二步，用etfList做index，上述array做列，构建一个series，
    #按照高到低排序，取前poolSize名
    money4CheckSeries = pd.Series(money4CheckArray, index = np.array(etfList))
    money4CheckSeries.sort(ascending = False)
    poolSize = int( len(etfList) / 10) + 1
    if poolSize < 10:
        poolSize = 10
    money4CheckSeries = money4CheckSeries[0 : poolSize]
    #取平均成交金额大于等于昨天我的总资产的100倍的那些etf
    #print money4CheckSeries
    money4CheckSeries = money4CheckSeries[money4CheckSeries >= 100*context.portfolio.portfolio_value]
    etfList = list(money4CheckSeries.index)
    #print etfList
    #计算etfList中的etf过去g.period4Check4Ret天的累积收益率比日收益标准差
    #返回比值最大的那只，存入etfList
    ret4CheckArray = np.array([])
    for security in etfList:
        his = attribute_history(security, g.period4Check4Ret + 1, '1d', ('close'), df = False)
        closeArray = his['close']
        tempRet = 100 * (closeArray[-1]/closeArray[0] - 1)
        real = talib.ROC(closeArray, timeperiod = 1)
        real = real[-g.period4Check4Ret:]
        std = np.std(real)
        ret = tempRet / std
        ret4CheckArray = np.append(ret4CheckArray, ret)
    #构建series，取收益比标准差最大那只etf，代码存入etfList
    ret4CheckSeries = pd.Series(ret4CheckArray, index = np.array(etfList))
    ret4CheckSeries.sort(ascending = False)
    etfList = list(ret4CheckSeries.index)[0:1]
    g.buyableList = etfList
    
####各种初始化####=====================================================
def initialize(context):
    set_option('use_real_price', True)
    set_benchmark('000300.XSHG')
    set_commission(PerTrade(buy_cost = 0.0003, sell_cost = 0.0003, min_cost = 0))
    log.set_level('order', 'error')
    set_universe([])
    #每天09:20用来储存买卖股票和目标value的dict
    g.sellDict = {}
    g.buyDict = {}
    ####每周期开始的那天的09:20，获取这一周期内能买的股票####
    ####将它们保存在context.buyableList中####
    run_daily(set_buyableList, 'before_open')
    ####每周期开始那天09:20选股所用参数，后面的灰色数字为初试参数####
    g.period4Check4Money = 18 # 
    g.period4Check4Ret = 6 #
    g.onMarketDays = 146 #146 * (250/365) = 100保证上市时间足够长
    ####每天09:20择时所用参数####
    g.nRSI = 6 #计算gapRSI所用天数
    g.buyThreshold = 40 #买入的阈值
    g.sellThreshold = 55 #卖出的阈值
    g.ma = 12 #12用这么多日均线判断强弱市，昨收在均线上说明是强市
    #用k线实体长度占总长度的比例来判断是否是变盘点，当比例小于
    #g.bian时，表示k线形态为十字星，表示将要变盘
    #g.bian1和g.bian2分别是弱市和强市情况下的变盘阈值             
    g.bian1 , g.bian2 = 0.8, 0.6

####每天开盘前用于判断某一只etf今日该买还是该卖的函数####============
####此函数输入为一个股票代码，应卖出时输出-1，应买进时输出1####
def buyOrSellCheck(security, context):
    panduan = 0
    his = attribute_history(security, 100, '1d', ('open', 'low', 'close', 'high'), df = False)
    closeArray = his['close']
    highArray = his['high']
    openArray = his['open']
    lowArray = his['low']
    ####计算MA####
    MAArray = talib.EMA(closeArray, g.ma)
    ####a用来计算k线的实体部分长度占总长度的比例
    #a越小，说明是十字星形状的k线，说明要变盘####
    a = (openArray[-1] - closeArray[-1]) / (highArray[-1] - lowArray[-1])
    a = abs(a)
    ####计算择时主要指标jump-RSI####
    #jumpArray = talib.LN(closeArray / highArray)
    jumpArray = talib.LN(closeArray / highArray)
    RSIArray = talib.RSI(jumpArray, g.nRSI)
    ####买卖逻辑####
    if RSIArray[-1] <= g.buyThreshold:#RSI低于买入阈值
        if closeArray[-1] > MAArray[-1]:#判断强弱市
            panduan = 1
        elif a <= g.bian1:#弱市状态下，需要确认有变盘信号才买进
            panduan = 1
    elif RSIArray[-1] >= g.sellThreshold:#RSI高于卖出阈值
        if closeArray[-1] <= MAArray[-1]:
            panduan = -1
        elif a <= g.bian2:#强市状态下，需要确认有变盘信号才卖出
            panduan = -1
    ####止盈止损####
    if security in context.portfolio.positions.keys():
        avgCost = context.portfolio.positions[security].avg_cost
        if closeArray[-1]/avgCost - 1 < -0.1:
            panduan = -1
        if closeArray[-1]/avgCost - 1 > 0.1:
            panduan = -1
    
    return panduan
                
####每天开盘前####====================================================
def before_trading_start(context):
    #初始化买卖dict，键为股票代码，值为调仓的target_value
    g.sellDict = {}
    g.buyDict = {}
    #现持仓为空
    if context.portfolio.positions.keys() == []:
        security = g.buyableList[0]
        if buyOrSellCheck(security, context) == 1:
            g.buyDict[security] = context.portfolio.portfolio_value
    #现持仓不为空且现持仓就是今能买
    elif context.portfolio.positions.keys() == g.buyableList:
        security = g.buyableList[0]
        #判断现持仓需要卖吗
        if buyOrSellCheck(security, context) == -1:
            g.sellDict[security] = 0
    else:#现持仓不为空，且现持仓不等于今能买
        security1 = g.buyableList[0]
        security2 = context.portfolio.positions.keys()[0]
        #如果今能买需要买，果断抛光现持仓，换入今能买
        if buyOrSellCheck(security1, context) == 1:
            g.sellDict[security2] = 0
            g.buyDict[security1] = 1.1*context.portfolio.portfolio_value
        #如果今能买不需要买，那么判断现持仓需要卖不？
        elif buyOrSellCheck(security2, context) == -1:
            g.sellDict[security2] = 0
     
    if g.sellDict != {}:
        message = '卖 ' + g.sellDict.keys()[0]
        print(message)
        send_message(message, channel = 'weixin')
    if g.buyDict != {}:
        message = '买 ' + g.buyDict.keys()[0]    
        print(message)
        send_message(message, channel = 'weixin')
                
####每天开盘后####===================================================
def handle_data(context, data):
    #先卖再买
    for security in g.sellDict:
        order_target_value(security, g.sellDict[security])
    for security in g.buyDict:
        order_target_value(security, g.buyDict[security])

 
                
                
                
                
        
        
        
        
        
        



