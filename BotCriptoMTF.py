!pip install ta

import yfinance as yf
import pandas as pd
import requests
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

# ==============================
# 🔐 TELEGRAM
# ==============================

TOKEN = "8186639105:AAE-V8elgfa2UePaVvOKnkQS71nvOQBfVJs"
CHAT_ID = "7300077075"



def kirim_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    msg = msg[:4000]  # anti limit

    res = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })

    ###print("STATUS:", res.status_code)
    ###print("RESPONSE:", res.text)

# ==============================
# 🔧 CLEAN DATA
# ==============================
def clean_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    for col in df.columns:
        if isinstance(df[col], pd.DataFrame):
            df[col] = df[col].iloc[:, 0]

    df = df.dropna()

    if df.empty or 'Close' not in df.columns:
        return None

    return df

# ==============================
# 📊 SUPERTREND
# ==============================
def supertrend(df, period=10, multiplier=3):
    atr = AverageTrueRange(df['High'], df['Low'], df['Close'], window=period).average_true_range()
    hl2 = (df['High'] + df['Low']) / 2

    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    direction = [1]

    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i-1]:
            direction.append(1)
        elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
            direction.append(-1)
        else:
            direction.append(direction[-1])

    df['ST'] = direction
    return df

# ==============================
# 🎯 SIGNAL FUNCTION
# ==============================
def get_signal(df):
    df = clean_df(df)
    if df is None or len(df) < 50:
        return "WAIT", None

    df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
    df['EMA50'] = EMAIndicator(df['Close'], 50).ema_indicator()
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()

    df = supertrend(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = "WAIT"

    if prev['ST'] == -1 and last['ST'] == 1 and last['Close'] > last['EMA20']:
        signal = "BUY"

    elif prev['ST'] == 1 and last['ST'] == -1:
        signal = "SELL"

    return signal, last

# ==============================
# 📥 LIST SAHAM
# ==============================
tickers_input = [

"ACES","BBTN","ISAT","DOID","KEEN","MTDL","JIHD","CRSN","PPRE","ADRO",
"BRIS","JPFA","DSNG","MARK","ASJT","PYFA","DOSS","JAST","AKRA","EMTK",
"JSMR","HMSP","CAMP","DYAN","DATA","ERAL","PGUN","AMRT","ESSA","MAPA",
"ASGR","ULTJ","BIKE","INET","FAST","KLAS","ANTM","EXCL","MIKA","LPPF",
"PSSI","BREN","DSSA","GOLD","KMTR","ARTO","GGRM","MNCN","LSIP","DMAS",
"BKSL","TCPI","GTRA","SOLA","ASII","HRUM","MPMX","MMIX","TOBA","MBAP",
"NSSS","GUNA","SMGA","BBCA","INTP","MYOR","MSIN","TPMA","NELY","BULL",
"HATM","FUTR","BBNI","MAPI","PNLF","MTMH","BUMI","ANJT","CARE","IFII",
"SGRO","BBRI","MBMA","PTPP","OMED","CMNT","KAEF","DKFT","IOTF","KBLV",
"BMRI","MTEL","PWON","PNBN","SIMP","MLIA","WIRG","IPAC","TUGU","BRPT",
"ERTX","SCMA","PNIN","GOOD","NISP","BEEF","JATI","SFAN","BUKA","SIDO",
"SMIL","RAJA","FILM","MAIN","TRIM","JECC","NTBK","CPIN","SRTG","SMRA",
"RMKE","SSIA","PEVE","BJTM","LABS","BHAT","GOTO","TOWR","TBIG","SMDR",
"GEMS","DEWA","BNGA","MHKI","CNMA","ICBP","ADMR","TINS","SSMS","IMAS",
"AMMN","STAA","MKAP","DGIK","INCO","ASSA","TKIM","TAPG","IMJS","BYAN",
"MPXL","MKTR","ADMG","INDF","AUTO","TPIA","MPOW","NCKL","SRAJ","KEJU",
"MOLI","BUVA","INKP","BFIN","TOTL","POWR","NIKL","IMPC","MLPT","MTWI",
"WOOD","ITMG","BMTR","WIFI","WINS","ARNA","JRPT","WEHA","MUTU","ADES",
"KLBF","BRMS","AALI","MDKI","PTRO","ROTI","TLDN","PGLI","CSRA","MDKA",
"BSDE","ABMM","PNGO","PRDA","BIRD","PALM","PSGO","WIIM","MEDC","BTPS",
"ADHI","SMSM","KRAS","TGKA","DWGL","PZZA","CTBN","PGAS","CTRA","AGII",
"BESS","KIJA","MSTI","BNII","RCCC","IPCC","PGEO","ELSA","AGRO","CMRY",
"NICL","BDKR","PANR","RGAS","CITA","PTBA","ENRG","AVIA","CLEO","LPKR",
"PBID","TBLA","SDPC","CARS","SMGR","ERAA","ARKO","MIDI","SBMA","RALS",
"MYOH","SICO","TLKM","GJTL","BDMN","SAMF","SOCI","RAAM","CBUT","AADI",
"UNTR","HEAL","BELI","TMAS","HRTA","SHIP","JARR","TRIS","UNVR","INDY",
"BSSR","SILO","UNIQ","SMBR","MGRO","TYRE","HEXA","DILD","ASDM","GPSO",
"IPCM","BMHS","SKRN","VTNY","TSPC","PANI","INDO","ELIT","INTD","BBYB",
"ELPI","ZYRX","LABA","KPIG","MLPL","CUAN","ARCI","SPTO","UFOE","NICE",
"GPRA","PEGE","SGER","DMMX","MCOL","CENT","BUKK","SUNI","BAYU","KKGI",
"PSAB","AXIO","SAME","BOAT","KINO","DRMA"]
tickers = [t + ".JK" for t in tickers_input]

hasil = []

# ==============================
# 🔄 LOOP
# ==============================
for ticker in tickers:
    try:
        df1d = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=False)
        df4h = yf.download(ticker, period="1mo", interval="4h", progress=False, auto_adjust=False)
        df1h = yf.download(ticker, period="1mo", interval="1h", progress=False, auto_adjust=False)
        df30 = yf.download(ticker, period="7d", interval="30m", progress=False, auto_adjust=False)

        signal_1d, last1d = get_signal(df1d)
        signal_4h, _ = get_signal(df4h)
        signal_1h, _ = get_signal(df1h)
        signal_30, _ = get_signal(df30)

        signals = [signal_1d, signal_4h, signal_1h, signal_30]

        # =========================
        # 🔥 LOGIKA UTAMA
        # =========================
        final_signal = "WAIT"

        if "BUY" in signals:
            final_signal = "BUY 🚀"

        if "SELL" in signals:
            final_signal = "SELL 🐻"

        # =========================
        # 🔍 TF TRIGGER
        # =========================
        buy_tf = []
        sell_tf = []

        if signal_1d == "BUY": buy_tf.append("1D")
        if signal_4h == "BUY": buy_tf.append("4H")
        if signal_1h == "BUY": buy_tf.append("1H")
        if signal_30 == "BUY": buy_tf.append("30M")

        if signal_1d == "SELL": sell_tf.append("1D")
        if signal_4h == "SELL": sell_tf.append("4H")
        if signal_1h == "SELL": sell_tf.append("1H")
        if signal_30 == "SELL": sell_tf.append("30M")

        kode = ticker.replace(".JK", "")

        link_sb = f"https://stockbit.com/#/symbol/{kode}"
        link_tv = f"https://www.tradingview.com/chart/?symbol=IDX:{kode}"

        text = f"""📊 <b>{kode}</b>
💰 {last1d['Close']:.0f}
🎯 SIGNAL : {final_signal}
🔥 BUY TF : {', '.join(buy_tf) if buy_tf else '-'}
🐻 SELL TF : {', '.join(sell_tf) if sell_tf else '-'}
TF 1D : {signal_1d}
TF 4H : {signal_4h}
TF 1H : {signal_1h}
TF 30M : {signal_30}
📊 RSI : {last1d['RSI']:.1f}
🔗 <a href="{link_sb}">Stockbit</a>
📈 <a href="{link_tv}">TradingView</a>
"""

        # =========================
        # 🔥 KIRIM JIKA ADA SIGNAL
        # =========================
        if "BUY" in signals or "SELL" in signals:
            hasil.append(text)

        print("DEBUG:", ticker, signals, final_signal)

    except Exception as e:
        print("Error:", ticker, e)

# ==============================
# 📤 TELEGRAM
# ==============================
msg = "🔥 <b>CRIPTO MTF 4TF SIGNAL</b>\n\n"

if hasil:
    msg += "\n".join(hasil)
else:
    msg += "⚠️ Tidak ada cripto mtf signal"

kirim_telegram(msg)

print(msg)

