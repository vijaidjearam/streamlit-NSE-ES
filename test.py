#! C:\Users\Administrateur\Desktop\streamlit-NSE-ES\Scripts\python.exe
import pandas as pd
from nsepython import *
from datetime import datetime, timedelta, date
import math
def gethighofadate(symbol, dt):
    start_date = (datetime.today() - timedelta(days=7)).strftime("%m/%d/%Y")
    end_date = datetime.now().strftime("%m/%d/%Y")
    df = pd.DataFrame(index_history(symbol,start_date,end_date))
    print(df)
    dt = dt.strftime("%d %b %Y")
    filt = (df['HistoricalDate'] == dt)
    try:
        result = df.loc[filt,'HIGH'].values[0]
        return float(result)
    except IndexError:
        return "NA"
    except ValueError as ve:
        return ve
def getlowofadate(symbol, dt):
    start_date = (datetime.today() - timedelta(days=7)).strftime("%m/%d/%Y")
    end_date = datetime.now().strftime("%m/%d/%Y")
    df = pd.DataFrame(index_history(symbol,start_date,end_date))
    dt = dt.strftime("%d %b %Y")
    filt = (df['HistoricalDate'] == dt)
    try:
        result = df.loc[filt,'LOW'].values[0]
        return float(result)
    except IndexError:
        return "NA"
def derivativehistorycallgetlowvalue(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice):
    optionType = "CE"
    start_date = start_date.strftime("%d-%m-%Y")
    end_date = end_date.strftime("%d-%m-%Y")
    expiry_date = expiry_date.strftime("%d-%b-%Y")
    try:
        df = pd.DataFrame(derivative_history(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice,optionType))
        result = (df['FH_TRADE_LOW_PRICE'].min())
        return float(result)
    except:
        return "NA"
def derivativehistoryputgetlowvalue(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice,):
    optionType = "PE"
    start_date = start_date.strftime("%d-%m-%Y")
    end_date = end_date.strftime("%d-%m-%Y")
    expiry_date = expiry_date.strftime("%d-%b-%Y")
    try:
        df = pd.DataFrame(derivative_history(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice,optionType))
        result = (df['FH_TRADE_LOW_PRICE'].max())
        return float(result)
    except:
        return "NA"
def round_up_to_base(x, base=50):
    return x + (base - x) % base
def round_down_to_base(x, base=50):
    return x - (x % base)

def get_end_strike_value(index_symbol,derivative_symbol,start_date,end_date,expiry_date,instrumentType):
    symbol = index_symbol
    highofstartdate = gethighofadate(symbol,start_date)
    lowofstartdate = getlowofadate(symbol,start_date)
    highofenddate = gethighofadate(symbol,end_date)
    lowofenddate = getlowofadate(symbol,end_date)
    maxof2days = max(highofstartdate,highofenddate)
    minof2days = min(lowofstartdate,lowofenddate)
    bufferhigh = round(maxof2days * 1.0015)
    bufferlow = round(minof2days * 0.9985)
    callendstrike = round_down_to_base(bufferlow)
    print(callendstrike)
    putendstrike = round_up_to_base(bufferhigh)
    print(putendstrike)
    # calculate CallEntryStrike 1st row
    symbol = derivative_symbol
    strike = []
    premium = []
    twodll = []
    strike.append(callendstrike)
    temppremium = callendstrike * (0.85/100)
    premium.append(temppremium)
    temptwodll = derivativehistorycallgetlowvalue(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice=strike[0])
    twodll.append(temptwodll)
    # Call Entry strke 2....n rows
    for i in range(1,9):
        if twodll[-1] >= premium[-1]:
            strike.append(strike[-1]+50)
            premium.append(strike[-1]* (0.85/100))
            twodll.append(derivativehistorycallgetlowvalue(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice=strike[-1]))
        else:
            break
    calldf = pd.DataFrame({"strike":strike,"premium":premium,"twodll":twodll})
    calldf['diff']=round(calldf['twodll']-calldf['premium'],2)
    print (calldf)
    leastdiff = calldf.loc[calldf['diff']>0,'diff'].min()
    leastdiff = round(leastdiff,2)
    print (leastdiff)
    if math.isnan(leastdiff):
        callentrystrike = 'NA'
        calltwodll = 'NA'
    else:
        filt = (calldf['diff'] == leastdiff)
        callentrystrike = calldf.loc[filt,'strike'].values[0]
        calltwodll = calldf.loc[filt,'twodll'].values[0]
    print("Call entry strike : ",callentrystrike)
    print("Call entry twoDLL : ",calltwodll)
    # finding PutEntryStrike 1st row
    symbol = derivative_symbol
    strike = []
    premium = []
    twodll = []
    strike.append(putendstrike)
    temppremium = putendstrike * (0.85/100)
    premium.append(temppremium)
    temptwodll = derivativehistoryputgetlowvalue(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice=strike[0])
    twodll.append(temptwodll)
    # Put Entry strke 2....n rows
    for i in range(1,9):
        if twodll[-1] >= premium[-1]:
            strike.append(strike[-1]-50)
            premium.append(strike[-1]* (0.85/100))
            twodll.append(derivativehistoryputgetlowvalue(symbol,start_date,end_date,instrumentType,expiry_date,strikePrice=strike[-1]))
        else:
            break
    putdf = pd.DataFrame({"strike":strike,"premium":premium,"twodll":twodll})
    putdf['diff']=round(putdf['twodll']-putdf['premium'],2)
    print (putdf)
    leastdiff = putdf.loc[putdf['diff']>0,'diff'].min()
    leastdiff = round(leastdiff,2)
    print (leastdiff)
    if math.isnan(leastdiff):
        putentrystrike = 'NA'
        puttwodll = 'NA'
    else:
        filt = (putdf['diff'] == leastdiff)
        putentrystrike = putdf.loc[filt,'strike'].values[0]
        puttwodll = putdf.loc[filt,'twodll'].values[0]
    print("Put entry strike : ",putentrystrike)
    print("Put entry twoDLL : ",puttwodll)
    result = []
    result.append(index_symbol)
    result.append(derivative_symbol)
    result.append(start_date.strftime("%d-%m-%Y"))
    result.append(end_date.strftime("%d-%m-%Y"))
    result.append(expiry_date.strftime("%d-%m-%Y"))
    result.append(instrumentType)
    result.append(callentrystrike)
    result.append(calltwodll)
    result.append(putentrystrike)
    result.append(puttwodll)
    return result


index_symbol = "NIFTY 50"
derivative_symbol = "NIFTY"
start_date = date(2024,2,12)
end_date = date(2024,2,13)
expiry_date = date(2024,2,15)
instrumentType = "options"

result = get_end_strike_value(index_symbol,derivative_symbol,start_date,end_date,expiry_date,instrumentType)
print(result)

