import streamlit as st
import pandas as pd
from nsepython import *
from datetime import datetime, timedelta, date
import math
st.title('NSE Derivative options calculate Strike Price')
# index_symbol = "NIFTY 50"
# derivative_symbol = "NIFTY"
# start_date = date(2024,2,8)
# end_date = date(2024,2,9)
# expiry_date = date(2024,2,15)
# instrumentType = "options"
index_symbol = st.selectbox('Select Index Symbol', ["NIFTY 50"])
derivative_symbol = st.selectbox('Select Derivative Symbol', ["NIFTY"])
start_date = st.date_input('Start Date')
end_date = st.date_input('End Date')
expiry_date = st.date_input('Expiry Date')
instrumentType = st.selectbox('Select Instrument Type', ["options"])
def get_index_history_lastweek(symbol):
    start_date = (datetime.today() - timedelta(days=7)).strftime("%m/%d/%Y")
    end_date = datetime.now().strftime("%m/%d/%Y")
    df = pd.DataFrame(index_history(symbol,start_date,end_date))
    st.write("Index history of Last Week")
    st.write(df)

def gethighofadate(symbol, dt):
    start_date = (datetime.today() - timedelta(days=7)).strftime("%m/%d/%Y")
    end_date = datetime.now().strftime("%m/%d/%Y")
    df = pd.DataFrame(index_history(symbol,start_date,end_date))
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
    get_index_history_lastweek(symbol)
    highofstartdate = gethighofadate(symbol,start_date)
    col1,col2,col3,col4, col5,col6,col7 = st.columns(7)
    col1.write(" ")
    col1.write("HIGH")
    col1.write("LOW")
    col2.write(start_date)
    col3.write(end_date)
    col4.write("2 Days")
    col5.write("Buffer")
    col6.write("End strike")
    col6.write("Call")
    col6.write("Put")
    col7.write("Value")
    col2.write(highofstartdate)
    lowofstartdate = getlowofadate(symbol,start_date)
    col2.write(lowofstartdate)
    highofenddate = gethighofadate(symbol,end_date)
    col3.write(highofenddate)
    lowofenddate = getlowofadate(symbol,end_date)
    col3.write(lowofenddate)
    maxof2days = max(highofstartdate,highofenddate)
    col4.write(maxof2days)
    minof2days = min(lowofstartdate,lowofenddate)
    col4.write(minof2days)
    bufferhigh = round(maxof2days * 1.0015)
    col5.write(bufferhigh)
    bufferlow = round(minof2days * 0.9985)
    col5.write(bufferlow)
    callendstrike = round_down_to_base(bufferlow)
    col7.write(callendstrike)
    putendstrike = round_up_to_base(bufferhigh)
    col7.write(putendstrike)
    call,put = st.columns(2)
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
    call.write("CALL")
    call.write(calldf)
    #print (calldf)
    leastdiff = calldf.loc[calldf['diff']>0,'diff'].min()
    leastdiff = round(leastdiff,2)
    #print (leastdiff)
    call.write("least Diff: "+str(leastdiff))
    if math.isnan(leastdiff):
        callentrystrike = 'NA'
        calltwodll = 'NA'
    else:
        filt = (calldf['diff'] == leastdiff)
        callentrystrike = calldf.loc[filt,'strike'].values[0]
        calltwodll = calldf.loc[filt,'twodll'].values[0]
    #print("Call entry strike : ",callentrystrike)
    #print("Call entry twoDLL : ",calltwodll)
    call.write("Call Entry Strike : "+ str(callentrystrike))
    call.write("Call entry twoDLL : "+str(calltwodll))
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
    put.write("PUT")
    put.write(putdf)
    #print (putdf)
    leastdiff = putdf.loc[putdf['diff']>0,'diff'].min()
    leastdiff = round(leastdiff,2)
    put.write("Least Diff: "+str(leastdiff))
    #print (leastdiff)
    if math.isnan(leastdiff):
        putentrystrike = 'NA'
        puttwodll = 'NA'
    else:
        filt = (putdf['diff'] == leastdiff)
        putentrystrike = putdf.loc[filt,'strike'].values[0]
        puttwodll = putdf.loc[filt,'twodll'].values[0]
    #print("Put entry strike : ",putentrystrike)
    #print("Put entry twoDLL : ",puttwodll)
    put.write("Put Entry Strike : "+str(putentrystrike))
    put.write("Put enty twoDll: "+str(puttwodll))
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


if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Go', on_click=click_button)

if st.session_state.clicked:
    try:
        df = pd.DataFrame(columns = ['index_symbol', 'derivative_symbol', 'start_date', 'end_date', 'expiry_date', 'instrumentType','callentrystrike','calltwodll','putentrystrike','puttwodll'])
        result = get_end_strike_value(index_symbol,derivative_symbol,start_date,end_date,expiry_date,instrumentType)
        t = {}
        t['index_symbol'] = result[0]
        t['derivative_symbol'] = result[1]
        t['start_date'] = result[2]
        t['end_date'] = result[3]
        t['expiry_date'] = result[4]
        t['instrumentType'] = result[5]
        t['callentrystrike'] = result[6]
        t['calltwodll'] = result[7]
        t['putentrystrike'] = result[8]
        t['puttwodll'] = result[9]
        print(t)
        df.loc[len(df)] = t
        st.write(df)
    except:
        st.write('Error occured')
    finally:
        st.session_state.clicked = False