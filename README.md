# Assignment2

{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "f462bb8d-9e2f-4806-966d-21c590882f50",
   "metadata": {},
   "source": [
    "# Training Dataset Generation\n",
    "\n",
    "This notebook demonstrates how to read raw market data from [QUANTAXIS](https://github.com/QUANTAXIS/QUANTAXIS) package and generate training datasets accordingly based on deep learning model needs, assuming market data is already downloaded and stored locally through QUANTAXIS CLI or otherwise possessed in some way.\n",
    "\n",
    "## Data Format\n",
    "\n",
    "Before anything, agreeing on the trading data format is necessary. I have spent way more time than I'm willing to on trying to figure out the raw data format and pre-processing routines when researching others' repositories. \n",
    "\n",
    "If not familiar with QUANTAXIS, the raw market data are essentially `pd.DataFrame` instances whose format is more or less similar to the following:\n",
    "\n",
    "|                                                     |    open |    high |     low |   close |           volume |   trade |   amount |   time_stamp | date       | type   |\n",
    "|:----------------------------------------------------|--------:|--------:|--------:|--------:|-----------------:|--------:|---------:|-------------:|:-----------|:-------|\n",
    "| (Timestamp('2020-01-01 00:00:00'), 'HUOBI.btcusdt') | 7194.7  | 7221.91 | 7186.19 | 7213.05 |      1.56942e+06 |    1772 | 217.941  |   1577808000 | 2020-01-01 | 5min   |\n",
    "| (Timestamp('2020-01-01 00:05:00'), 'HUOBI.btcusdt') | 7213.48 | 7221.76 | 7206.9  | 7216.42 | 545030           |     665 |  75.5441 |   1577808300 | 2020-01-01 | 5min   |\n",
    "| (Timestamp('2020-01-01 00:10:00'), 'HUOBI.btcusdt') | 7216.85 | 7217.05 | 7204.95 | 7206.03 | 542448           |     586 |  75.2413 |   1577808600 | 2020-01-01 | 5min   |\n",
    "| (Timestamp('2020-01-01 00:15:00'), 'HUOBI.btcusdt') | 7206.02 | 7224.12 | 7202.49 | 7223.27 | 927444           |     979 | 128.582  |   1577808900 | 2020-01-01 | 5min   |\n",
    "| (Timestamp('2020-01-01 00:20:00'), 'HUOBI.btcusdt') | 7223.26 | 7223.26 | 7216.49 | 7217.81 | 159531           |     763 |  22.0955 |   1577809200 | 2020-01-01 | 5min   |\n",
    "\n",
    "The above table is an example of the cryptocurrency trading data of BTC/USDT pair with 5-minute intervals, starting from Jan. 1, 2020. Here is a sample daily data from China stock market:\n",
    "\n",
    "|                                              |   open |   high |   low |   close |   volume |      amount |\n",
    "|:---------------------------------------------|-------:|-------:|------:|--------:|---------:|------------:|\n",
    "| (Timestamp('2000-01-27 00:00:00'), '000963') |  16.3  |  22.5  | 16.01 |   20.62 |   297107 | 5.24846e+08 |\n",
    "| (Timestamp('2000-01-28 00:00:00'), '000963') |  19.3  |  19.78 | 18.56 |   18.56 |   117871 | 2.22077e+08 |\n",
    "| (Timestamp('2000-02-14 00:00:00'), '000963') |  18.21 |  20.3  | 17.71 |   20.07 |    92146 | 1.74449e+08 |\n",
    "| (Timestamp('2000-02-15 00:00:00'), '000963') |  19.38 |  19.97 | 18.18 |   18.24 |    61216 | 1.18008e+08 |\n",
    "| (Timestamp('2000-02-16 00:00:00'), '000963') |  18.25 |  18.77 | 17.3  |   17.57 |    46718 | 8.30775e+07 |\n",
    "\n",
    "The index column of the dataframe is a tuple consisting of the close time and the symbol/stock code, depending on which market the data is from. *Plase notice that the indices are actually named, the first index column is named \"datetime\" and the second is \"code\", which can be seen from the later example outputs.*\n",
    "\n",
    "The two dataframes are slightly different in the columns depending on the market and frequency of the data, but in general the columns should at least contain \n",
    "\n",
    "- **trade time**, which is the first element of the index for each row\n",
    "- **open**\n",
    "- **close**\n",
    "- **high**\n",
    "- **low**\n",
    "- **volume**\n",
    "- **amount**\n",
    "\n",
    "Having established the format of the raw data, one can either retrieve data for processing from QUANTAXIS or forge whatever market data of their own into the same format. "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8bb1db3b-d8a4-4388-9e6c-cee73e188463",
   "metadata": {},
   "source": [
    "## 0. Load dependencies\n",
    "\n",
    "Set up jupyter magic functions and load all necessary packages/modules for processing. For debugging purposes, the visualization functionalities are imported here, read the source code and possibly another notebook documentation for more information about its usages."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "68f31c80-a9d8-4cd2-9166-e2ca612ebaa9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "提示：当前环境 pandas 版本高于 0.25，get_price 与 get_fundamentals_continuously 接口 panel 参数将固定为 False\n",
      "注意：0.25 以上版本 pandas 不支持 panel，如使用该数据结构和相关函数请注意修改\n"
     ]
    }
   ],
   "source": [
    "%matplotlib inline\n",
    "%load_ext autoreload\n",
    "%autoreload 2\n",
    "\n",
    "import sys\n",
    "from pathlib import Path\n",
    "\n",
    "# add the project root directory into path so that we can import other modules in the project\n",
    "_project_root = Path().cwd().absolute().parent\n",
    "sys.path.append(str(_project_root))\n",
    "\n",
    "import QUANTAXIS as qa\n",
    "from datetime import datetime\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "\n",
    "\n",
    "from utilities.visualizations import draw_trading_data   # this is a utility function create to display financial data\n",
    "from matplotlib import pyplot as plt"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "30307bb7-b658-494b-a429-7c317f19a026",
   "metadata": {},
   "source": [
    "An example of retrieving data through QUANTAXIS package, notice that the dataframes from it are actually indexed with names \"datetime\" and \"code\", so if the later code uses the index names, please refer back to this accordingly. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "dedf3a71-2947-4b52-844d-e27b9e472ce4",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th>open</th>\n",
       "      <th>high</th>\n",
       "      <th>low</th>\n",
       "      <th>close</th>\n",
       "      <th>volume</th>\n",
       "      <th>trade</th>\n",
       "      <th>amount</th>\n",
       "      <th>time_stamp</th>\n",
       "      <th>date</th>\n",
       "      <th>type</th>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>datetime</th>\n",
       "      <th>code</th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "      <th></th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>2020-12-31 16:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>28782.01</td>\n",
       "      <td>28822.59</td>\n",
       "      <td>28311.00</td>\n",
       "      <td>28380.60</td>\n",
       "      <td>2970.381406</td>\n",
       "      <td>78389.0</td>\n",
       "      <td>3.840004e+07</td>\n",
       "      <td>1609430400</td>\n",
       "      <td>2020-12-31</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2020-12-31 17:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>28382.47</td>\n",
       "      <td>28723.68</td>\n",
       "      <td>28362.00</td>\n",
       "      <td>28571.97</td>\n",
       "      <td>2435.556988</td>\n",
       "      <td>49032.0</td>\n",
       "      <td>3.363307e+07</td>\n",
       "      <td>1609434000</td>\n",
       "      <td>2020-12-31</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2020-12-31 18:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>28571.97</td>\n",
       "      <td>28898.00</td>\n",
       "      <td>28424.56</td>\n",
       "      <td>28872.25</td>\n",
       "      <td>2579.419408</td>\n",
       "      <td>48133.0</td>\n",
       "      <td>3.760116e+07</td>\n",
       "      <td>1609437600</td>\n",
       "      <td>2020-12-31</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2020-12-31 19:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>28872.24</td>\n",
       "      <td>29000.00</td>\n",
       "      <td>28742.41</td>\n",
       "      <td>28897.83</td>\n",
       "      <td>2293.821339</td>\n",
       "      <td>56789.0</td>\n",
       "      <td>4.087368e+07</td>\n",
       "      <td>1609441200</td>\n",
       "      <td>2020-12-31</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2020-12-31 20:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>28897.84</td>\n",
       "      <td>29139.65</td>\n",
       "      <td>28862.00</td>\n",
       "      <td>29126.70</td>\n",
       "      <td>1936.480299</td>\n",
       "      <td>42101.0</td>\n",
       "      <td>3.275941e+07</td>\n",
       "      <td>1609444800</td>\n",
       "      <td>2020-12-31</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>...</th>\n",
       "      <th>...</th>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "      <td>...</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2021-07-29 03:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>39701.53</td>\n",
       "      <td>39849.20</td>\n",
       "      <td>39506.57</td>\n",
       "      <td>39609.78</td>\n",
       "      <td>1165.520236</td>\n",
       "      <td>26948.0</td>\n",
       "      <td>2.238507e+07</td>\n",
       "      <td>1627527600</td>\n",
       "      <td>2021-07-29</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2021-07-29 04:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>39609.78</td>\n",
       "      <td>40115.53</td>\n",
       "      <td>39491.99</td>\n",
       "      <td>39963.96</td>\n",
       "      <td>2031.998164</td>\n",
       "      <td>41339.0</td>\n",
       "      <td>4.149152e+07</td>\n",
       "      <td>1627531200</td>\n",
       "      <td>2021-07-29</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2021-07-29 05:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>39963.96</td>\n",
       "      <td>40270.53</td>\n",
       "      <td>39717.00</td>\n",
       "      <td>40108.92</td>\n",
       "      <td>2522.186110</td>\n",
       "      <td>47637.0</td>\n",
       "      <td>5.237000e+07</td>\n",
       "      <td>1627534800</td>\n",
       "      <td>2021-07-29</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2021-07-29 06:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>40108.92</td>\n",
       "      <td>40197.67</td>\n",
       "      <td>39893.08</td>\n",
       "      <td>39996.58</td>\n",
       "      <td>1641.204453</td>\n",
       "      <td>49210.0</td>\n",
       "      <td>3.324053e+07</td>\n",
       "      <td>1627538400</td>\n",
       "      <td>2021-07-29</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2021-07-29 07:00:00</th>\n",
       "      <th>BINANCE.BTCUSDT</th>\n",
       "      <td>39996.58</td>\n",
       "      <td>40078.91</td>\n",
       "      <td>39923.54</td>\n",
       "      <td>40024.60</td>\n",
       "      <td>416.284801</td>\n",
       "      <td>9751.0</td>\n",
       "      <td>8.234253e+06</td>\n",
       "      <td>1627542000</td>\n",
       "      <td>2021-07-29</td>\n",
       "      <td>60min</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "<p>5025 rows × 10 columns</p>\n",
       "</div>"
      ],
      "text/plain": [
       "                                         open      high       low     close  \\\n",
       "datetime            code                                                      \n",
       "2020-12-31 16:00:00 BINANCE.BTCUSDT  28782.01  28822.59  28311.00  28380.60   \n",
       "2020-12-31 17:00:00 BINANCE.BTCUSDT  28382.47  28723.68  28362.00  28571.97   \n",
       "2020-12-31 18:00:00 BINANCE.BTCUSDT  28571.97  28898.00  28424.56  28872.25   \n",
       "2020-12-31 19:00:00 BINANCE.BTCUSDT  28872.24  29000.00  28742.41  28897.83   \n",
       "2020-12-31 20:00:00 BINANCE.BTCUSDT  28897.84  29139.65  28862.00  29126.70   \n",
       "...                                       ...       ...       ...       ...   \n",
       "2021-07-29 03:00:00 BINANCE.BTCUSDT  39701.53  39849.20  39506.57  39609.78   \n",
       "2021-07-29 04:00:00 BINANCE.BTCUSDT  39609.78  40115.53  39491.99  39963.96   \n",
       "2021-07-29 05:00:00 BINANCE.BTCUSDT  39963.96  40270.53  39717.00  40108.92   \n",
       "2021-07-29 06:00:00 BINANCE.BTCUSDT  40108.92  40197.67  39893.08  39996.58   \n",
       "2021-07-29 07:00:00 BINANCE.BTCUSDT  39996.58  40078.91  39923.54  40024.60   \n",
       "\n",
       "                                          volume    trade        amount  \\\n",
       "datetime            code                                                  \n",
       "2020-12-31 16:00:00 BINANCE.BTCUSDT  2970.381406  78389.0  3.840004e+07   \n",
       "2020-12-31 17:00:00 BINANCE.BTCUSDT  2435.556988  49032.0  3.363307e+07   \n",
       "2020-12-31 18:00:00 BINANCE.BTCUSDT  2579.419408  48133.0  3.760116e+07   \n",
       "2020-12-31 19:00:00 BINANCE.BTCUSDT  2293.821339  56789.0  4.087368e+07   \n",
       "2020-12-31 20:00:00 BINANCE.BTCUSDT  1936.480299  42101.0  3.275941e+07   \n",
       "...                                          ...      ...           ...   \n",
       "2021-07-29 03:00:00 BINANCE.BTCUSDT  1165.520236  26948.0  2.238507e+07   \n",
       "2021-07-29 04:00:00 BINANCE.BTCUSDT  2031.998164  41339.0  4.149152e+07   \n",
       "2021-07-29 05:00:00 BINANCE.BTCUSDT  2522.186110  47637.0  5.237000e+07   \n",
       "2021-07-29 06:00:00 BINANCE.BTCUSDT  1641.204453  49210.0  3.324053e+07   \n",
       "2021-07-29 07:00:00 BINANCE.BTCUSDT   416.284801   9751.0  8.234253e+06   \n",
       "\n",
       "                                     time_stamp        date   type  \n",
       "datetime            code                                            \n",
       "2020-12-31 16:00:00 BINANCE.BTCUSDT  1609430400  2020-12-31  60min  \n",
       "2020-12-31 17:00:00 BINANCE.BTCUSDT  1609434000  2020-12-31  60min  \n",
       "2020-12-31 18:00:00 BINANCE.BTCUSDT  1609437600  2020-12-31  60min  \n",
       "2020-12-31 19:00:00 BINANCE.BTCUSDT  1609441200  2020-12-31  60min  \n",
       "2020-12-31 20:00:00 BINANCE.BTCUSDT  1609444800  2020-12-31  60min  \n",
       "...                                         ...         ...    ...  \n",
       "2021-07-29 03:00:00 BINANCE.BTCUSDT  1627527600  2021-07-29  60min  \n",
       "2021-07-29 04:00:00 BINANCE.BTCUSDT  1627531200  2021-07-29  60min  \n",
       "2021-07-29 05:00:00 BINANCE.BTCUSDT  1627534800  2021-07-29  60min  \n",
       "2021-07-29 06:00:00 BINANCE.BTCUSDT  1627538400  2021-07-29  60min  \n",
       "2021-07-29 07:00:00 BINANCE.BTCUSDT  1627542000  2021-07-29  60min  \n",
       "\n",
       "[5025 rows x 10 columns]"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "btc_symbol = 'BINANCE.BTCUSDT'\n",
    "freq = '60min'\n",
    "start_date = \"2021-01-01\"\n",
    "end_date = str(datetime.today())\n",
    "data = qa.QA_fetch_cryptocurrency_min_adv(btc_symbol, start=start_date, end=end_date, frequence=freq).data\n",
    "data"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "01348b7d-7e3d-4a75-b941-0c8ccee5524c",
   "metadata": {},
   "source": [
    "## 1. Construct Training Data\n",
    "\n",
    "Assuming the deep learning model takes $N$ consecutive candlesticks with attributes: **open, close, high, low, and volume** as input, and returns a 3-class classification output representing the 3 directions of the near future (e.g. prices in the next 6 time periods) given the input: **goes up, goes down, or oscillating sideways** respectively, and the output labels are determined by adopting a method called [**the Triple-Barrier Method**](https://towardsdatascience.com/financial-machine-learning-part-1-labels-7eeed050f32e). \n",
    "\n",
    "### 1. 1 - Data Segmentation\n",
    "\n",
    "The first step is to slide the trading data with a sliding window of $N + T$ where $N$ is the length of the model input and $T$ is the length used to determine the classification labels mentioned in the **TBM** (Triple-Barrier Method)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "f6309bd1-b9ea-4c26-b295-ae3a291cb36f",
   "metadata": {
    "tags": []
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "SHAPES:\n",
      "segment = (106, 10) | history = (100, 10) | future = (6, 10)\n"
     ]
    },
    {
     "data": {
      "image/png": "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pca//q7eefNFxcRE69vvfqk26dkbZ5x2opISm+nLaZOqtV98+U3asjW71tc5nU7ddtfDeuS/d+qOW67Xnj1Feu6liVq5em2D4pAq54jceMt/9N/7b1XrVi20bdt2jf73/SoqLlFsbIxrwrSkOj+7b7//RW3bpumzqW9IkqZ89Ln+9/0vkqSUlGTXHffS0jKN/vf9evjB25WW1kpLl63SHfceWKb2jnsf0TOP36+rr7xY2dk7dP1N96q0tKzB76/KuWedpm5dD9OsH6a52nbl5Or8kddpW/YO3T/2Gb347FjZkhI197eF+u/DlXstnHB8P9lsSZo88flqx7v1roddKzB5w5fvb9Lkj3TPHaP17Rfvqqxsr14dP9lV4Dz/0kTdd3flJPiKin2aPfd3PfCw+/0j6svJoRITE3RY546yWCxyOBy67sZ79PTj9+mB+27RuvUbde2Nd7ueW9fPTNs2rRQTHSVJdZ5f3sYHAA1hdO4+0POZhwAAAADCFsOWAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHiE4gEAAACARygeAAAAAHgkwuwA/GHjmgWKio41OwwXwzDkdDrNDgONRB5DA3kMDeQx+JHD4BQZYZUkVeyzSyKPkrR3b4k6HTHA7DCaTFgUD1HRserSPXCSGBcXq5KSUrPDQCORx9BAHkMDeQx+5DA4DTquhyRp9vwVksijJK1ZPs/sEJoUw5YAAAAAeCQseh4AAACAQHDd1aN0wbChstsdmjPvd30+4ztNfO1pbd68zfWcy665VQ6H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\n",
      "text/plain": [
       "<Figure size 864x576 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "n, t = 100, 6\n",
    "window_size = n + t\n",
    "\n",
    "for i in range(0, len(data) - window_size):\n",
    "    segment = data.iloc[i : i + window_size]\n",
    "    history = segment[:n]\n",
    "    future = segment[n:]\n",
    "    print(f\"SHAPES:\\nsegment = {segment.shape} | history = {history.shape} | future = {future.shape}\")\n",
    "    s = history.iloc[-1].name[0]\n",
    "    fig, (main_ax, vol_ax) = draw_trading_data(segment, pointers=[s])\n",
    "    main_ax.axvline(n-.5, ls='--', color='gray');\n",
    "    break\n",
    "    "
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5ed244fb-606b-4045-ae19-3a3e3989c7bb",
   "metadata": {},
   "source": [
    "The above code snippet shows how to slide the data with a given sliding window size and segment it into `history` and `future`, where `history` is the data intended to be fed into the neural network and `future` is used to determine the label. In the figure above, the yellow chevron denotes the start of the `future` segment. (The equivalent generator function `segment_trading_data()` is implemented in the `dataset_management/tools.py` module.)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "c233dfaa-c0b5-44c5-a340-2e8f971e2508",
   "metadata": {},
   "outputs": [],
   "source": [
    "from tools import segment_trading_data\n",
    "segments = segment_trading_data(data=data, n=100, t=12)\n",
    "\n",
    "for i, (history, future) in enumerate(segments):\n",
    "    \"\"\"DO SOMETHING WITH history AND future DATA HERE\"\"\"\n",
    "    break"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8babc802-3012-476d-a108-ff56888e7bc3",
   "metadata": {},
   "source": [
    "### 1. 2 - Label the segments\n",
    "\n",
    "The second step is to assign each segment a label, based on TBM. According to the article, the volatility of the previous prices is taken into account when determining the upper and lower bounds.\n",
    "\n",
    "Let's take a random segment and try to assign the correct label to it.\n",
    "\n",
    "It is easy to know that the definition of volatility in finance is simply equivalent to standard deviation in statistics with a minor difference:\n",
    "\n",
    "$\\text{volatility} = \\sqrt{\\dfrac{1}{N} \\sum_{i=1}^{N}(P_i - \\overline{P})^2}$ whereas $\\text{standard deviation} = \\sqrt{\\dfrac{1}{N - 1} \\sum_{i=1}^{N}(P_i - \\overline{P})^2}$\n",
    "\n",
    "Therefore setting the attribute `ddof=0`.\n",
    "\n",
    "After getting the volatility, the upper and lower bounds of the triple-barrier is defined accordingly, which is \n",
    "\n",
    "$\\text{upper} = k_{up}v + p_0$ and $\\text{lower} = -k_{lo}v + p_0$,\n",
    "\n",
    "where $k_{up}$ and $k_{lo}$ are the upper and lower bounds magnitudes, $v$ is the volatility, and $p_0$ is the closing price of the last candlestick. It means that the upper and lower bounds of the TBM are some magnitudes of the volatility away from the closing price.\n",
    "\n",
    "#### Alternatives for volatility\n",
    "\n",
    "One of the alternatives for the above mentioned volatility can be **average true range**, a.k.a. **ATR**. And it is calculated as follows:\n",
    "\n",
    "$\\text{True Range}_i = \\text{TR}_i = max\\{H_i - L_i, |C_{i-1} - H_i|, |C_{i-1} - L_i|\\}$\n",
    "\n",
    "$\\text{ATR}(\\text{candles} | n) = MA(\\text{TR}, n)$"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 78,
   "id": "8783e8fb-24af-4271-8b1e-b79971b2d63b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "50\n",
      "0.048736243783015935 0.02480979590923454\n"
     ]
    }
   ],
   "source": [
    "segments = segment_trading_data(data=data, n=100, t=12, shuffle=False, norm=True)\n",
    "r = 56                       # this is a random number, meaning that I'm taking the r-th segment as a sample\n",
    "for _ in range(r):\n",
    "    history, future = next(segments)\n",
    "\n",
    "volatility = history['close'].std(ddof=0)\n",
    "\n",
    "k_up, k_lo = 1., 1.\n",
    "last_bar = history.iloc[-1]\n",
    "last_closing_price = last_bar['close']\n",
    "upper_bound = k_up * volatility + last_closing_price\n",
    "lower_bound = -k_lo * volatility + last_closing_price\n",
    "\n",
    "\n",
    "# ATR version\n",
    "from utilities.funcs import indicator_ATR\n",
    "\n",
    "print(len(history) // 2)\n",
    "atr_df = indicator_ATR(history, n=len(history) // 2)\n",
    "atr = atr_df.iloc[-1].ATR\n",
    "\n",
    "up_atr = k_up * atr + last_closing_price\n",
    "lo_atr = -k_lo * atr + last_closing_price\n",
    "print(volatility, atr)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "335f78f9-5ca9-4f90-bad9-1b8aa4f95aa1",
   "metadata": {},
   "source": [
    "Now that the upper, lower bounds are calculated, let's visualize it to check if it all makes sense."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 79,
   "id": "9cdd48b6-184e-4c8a-b45a-13ea8ec48b5d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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SxbMwOhRkYiPv4tx46chJycXcrkcTz/5CLKysvHc/VGDAOCPvQfw/sKPKh1HTb6/O/F3MWPOEny4dA483Fzx738nMHvuMv36oHp1EVo/CAf+PVql45vi4+OtH3K1rBh0Oh3GvjYVixdMx7vT38LVa7EY89oU/XEahAbD7X5/g/UbtmDqxFfx648bkZubh5WrN+hvwmryO0VE1kcW1qRL6WfRREREREQkOmyWQ0REREQkEUzuiYiIiIgkgsk9EREREZFEMLknIiIiIpIIJvdERERERBLB5J6IiIiISCKY3BMRERERSQSTeyIiIiIiiWByT0REREQkEUzuiYiIiIgkgsk9EREREZFEMLknIiIiIpIIJvdERERERBLB5J6IiIiISCKY3BMRERERSQSTeyIiIiIiiWByT0REREQkEUzuiYiIiIgkgsk9EREREZFEMLknIiIiIpIIJvdERERERBLB5J6IiIiISCKY3BMRERERSQSTeyIiIiIiiWByT0REREQkEUzuiYiIiIgkgsk9EREREZFEMLknIiIiIpIIJvdERERERBLB5J6IiIiISCKY3BMRERERSQSTeyIiIiIiiWByT0REREQkEUzuiYiIiIgkgsk9EREREZFEMLknIiIiIpIIJvdERERERBLB5J6IiIiISCKY3BMRERERSQSTeyIiIiIiiWByT0REREQkEUzuiYiIiIgkgsk9EREREZFEMLknIiIiIpIIJvdERERERBLB5J6IiIiISCKY3BMRERERSYRS6AAqKvbyEdjaOQgdhp5MJoNOpxM6DKoAlpW4sLzEheUlLiwvy2ajVAAACtQalpWA8vKyUb9RR6HDqDLRJPe2dg4Ib2I5H7SjowOys3OEDoMqgGUlLiwvcWF5iQvLy7J17dQUAHDg8AWWlYAunz8kdAjVwmY5REREREQSweSeiIiIiEgimNwTEREREUkEk3siIiIiIokQTYdaIiIiIik7fipa6BBIApjcExEREVmAnNx8oUMgCWCzHCIiIiILEODvhQB/L6HDIJFjzT0RERGRBQgN8QMA3I5PFjgSEjPW3BMRERERSQSTeyIiIiIiiWByT0REREQkEUzuiYiIiIgkgh1qiYiIiCzAkeOXhQ6BKkAul2NAvycxacLL6NxjgH65s5Mj5r83BT4+XnB0cMD8RZ/g+MmzsLWxwbz3JiOoXl3k5eZh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\n",
      "text/plain": [
       "<Figure size 864x576 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "separator = last_bar.name[0]\n",
    "fig, (main_ax, vol_ax) = draw_trading_data(pd.concat([history, future]),)\n",
    "main_ax.axvline(99.5, color='gray', ls='--', linewidth=1.5)\n",
    "main_ax.axhline(upper_bound, color='g', linewidth=1.5, ls='--', label='vol up')\n",
    "main_ax.axhline(lower_bound, color='r', linewidth=1.5, ls='--', label='vol low')\n",
    "\n",
    "main_ax.axhline(up_atr, color='#64f960', linewidth=1.5, ls='-.', label='ATR up')\n",
    "main_ax.axhline(lo_atr, color='#ff0192', linewidth=1.5, ls='-.', label='ATR low')\n",
    "main_ax.legend();"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "093ecb75-6e44-46e2-abf2-eba44880fd8f",
   "metadata": {},
   "source": [
    "From the above plot, it's easy to see that the future price goes up and penetrates the upper bound, hence the label $y=1$. \n",
    "\n",
    "*Please note that the data here is randomly taken, and the example data is not necessarily the same for everyone who run this notebook, so this illustration might not be accurate for you*\n",
    "\n",
    "Now let's write the code to determine the label based on the code we already have."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "id": "1c5f1492-b20c-4fc4-89f4-8123a5d247fc",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1"
      ]
     },
     "execution_count": 75,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# determine the label\n",
    "above_upper, = np.nonzero((future['close'] > up_atr).values)\n",
    "below_lower, = np.nonzero((future['close'] < lo_atr).values)\n",
    "first_above = above_upper[0] if len(above_upper) else len(future) + 1\n",
    "first_below = below_lower[0] if len(below_lower) else len(future) + 1\n",
    "\n",
    "if first_above < first_below:\n",
    "    label = 1\n",
    "elif first_below < first_above:\n",
    "    label = -1\n",
    "else:\n",
    "    label = 0\n",
    "\n",
    "label"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "d2c8a0d7-898a-43c2-b0d0-9e7c9a62e20f",
   "metadata": {},
   "source": [
    "The above procedure is implemented in `dataset_management/tools.py` as function `compute_label()`.\n",
    "\n",
    "### 1. 3 - Data Normalization\n",
    "\n",
    "In deep learning, there is a well-known data pre-processing step called \"normalization\" and the purpose of it is to rescale data inputs to a universal range to help neural networks converge during training. And the input features we have here are OHLCV, notice that the first 4 features are prices and share more or less the same degree of magnitude; whereas the volume is there by its own. Therefore the normalization of the input data is as follows:\n",
    "\n",
    "$\\text{open}' = \\dfrac{\\text{open}}{a}$\n",
    "\n",
    "$\\text{close}' = \\dfrac{\\text{close}}{a}$\n",
    "\n",
    "$\\text{high}' = \\dfrac{\\text{high}}{a}$\n",
    "\n",
    "$\\text{low}' = \\dfrac{\\text{low}}{a}$\n",
    "\n",
    "$\\text{volume}' = \\dfrac{\\text{volume} - \\text{volume}_{min}}{\\text{volume}_{max} - \\text{volume}_{min}}$\n",
    "\n",
    "where $a$ is the anchor price, here we take the first closing price as its value.\n",
    "\n",
    "The implementation can be integrated into the previous code snippet when we segment the data:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 82,
   "id": "132e61db-822b-4726-9a0f-916a2e33a2ba",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 576x432 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "image/png": "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CRx26IG8+u+32ZgTvst0e+sicjqdZHXJrO0i6p4Vll1Eyo93yo93yk94CpmukKioSKqqqklLTeagwQNchcUxQw9n5ap1BkdnLIvFwoUXnIPFYsZWXEJVVTVffvMDCQlxHH7o4LAuLNRF5J3y453y453yE55CosXigjFn0717FmvX1g7IvPnG8bz+9n85ePAgCgqLwrp57cgjDqGispI1azYwdfJdrF67gVmz5wAQHR2lLiLURdQU5cc75cc75Sf8BH1hce45p3Ph+aO47e5H+Odzj/LmnPf5a9VaumZ1Jioqkv9+8D8gPEfvXzxuNKPOHkFpaRmbNm/luRf+zaT7bmVL7jaefOZlo8MLCOoi8k758U758U75CU9B1xVitVpwOnFtc96rRzeeef5fHDR4IKtWr8NiMVNdXc0n/9u3sEq4FBVdszLplN6RX39fxuADB3D00MMZe8kNXDxuNHfe+necTidTZjzLGSNONDrUgKAuIu+UH++UH++Un/AVVC0Wxx0zhFNOOo6U5CSW/PYnf61aR3JSB2647jJ27crn+pvu5aH7b2XZitWulopwERFhZfTI0+jcOYNvvvuRzVu2csaIE0lOSqRjx1SeeX4Wb/z7WR6e+jRLfvvT6HANpy4i75Qf75Qf75Sf8BY0hcVRQw7h5glX8diTLxITE0NsbDSnnzqcjZu20CEhnpSUJBwOJ1FRkdx652SjwzVEp/Q0jj1mCJkZ6fz2x3L+WrmWi8aew5LflnHw4IE4nU5mvz7P6DANpy4i75Qf75Qf75QfCYqukKFHHcZD993KhFsfYP3epV7NZjMlJWUcNHggb7z9PikpSaR3TOOrbxYYG6yBdu7KY8HCXzhh2FEcdsiB1OypweFwctMNV5K9cXPYDmJVF5F3yo93yo93yo94CorColtWZzbmbKGqal/zmcPhwFZcwvHHHcU77813TVsKd7vz8ln40xLOOuNk+vfrxbz3PuaLr75n0+atRodmiIgIK0OPPIzOnTOoqq5m85atLPxxCddfcykdO6ZywojzeePfz/LZF9/x+lvvGR1uu1N+vFN+vFN+pCFB0RUSHR3FiccfzRGHH8z8T75k6bKVrscemXQHM554wbWZjdQ6YGA/br/lWm658yGKi0uNDsdQ6iLyTvnxTvnxTvkRT0GxbXplZRXf/rCIP/5cwaizR9C3T08AHn34bux2u4qKvSIjI7nkwnMZNKAv1197KRtztoR9UQH7uoh27tzNYYccSP++vVxdRF2zOof9h57y453y453yI56CosWiTnR0FCcNP5ZDDz6AAf17s2zFah5/6p9GhxVQDj34AEaccgLWCAtTpz9ndDgBJaNTR84642QqKyv55H/fkJiYELZdRA1RfrxTfrxTfqROULRY1KmsrOKb734kZ9MW1q3PUVHRgD/+/IsZT77gKirqls4V2LFzNz8v/p2TTzwOh9OhDz0Pyo93yo93yo/UCYrBm+4qK6uYM2++a4GscFn8qrWUm9ouogvGnMXvf6xQF1EDlB/vlB/vlB/xFFRdISKtpS4i75Qf75Qf75QfcafCQsKSWrq8U368U368U37CW1CNsRDxFX3oeaf8eKf8eKf8hDcVFiIiIuIzKixERETEZ1RYiIiIiM+osBARERGfUWEhIiIiPqPCQkRERHzm/wECD/2ENZjfrwAAAABJRU5ErkJggg==\n",
      "text/plain": [
       "<Figure size 576x432 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "def segment_trading_data(data: pd.DataFrame, n: int=144, t: int=6, norm=False):\n",
    "    \"\"\" Slide the given trading data and generate segments\n",
    "        data:   the trading data formatted as QUANTAXIS DataStruct\n",
    "        n:      history window size, default to 144 (12 hours of 5min data)\n",
    "        t:      future window size, default to 6 (half hour of 5min data)\n",
    "        norm:   specify whether to normalize the input data\n",
    "        :return : generator of (history, future) pair\n",
    "    \"\"\"\n",
    "    window_size = n + t\n",
    "    for i in range(0, len(data) - window_size + 1):\n",
    "        segment = data.iloc[i : i + window_size].copy()\n",
    "        if norm:\n",
    "            \n",
    "            anchor_price = segment['close'].iloc[0]\n",
    "            max_vol = segment['volume'].iloc[:n].max()\n",
    "            min_vol = segment['volume'].iloc[:n].min()\n",
    "            segment[['open', 'high', 'low', 'close']] /= anchor_price\n",
    "            segment['volume'] = (segment['volume'] - min_vol) / (max_vol - min_vol)\n",
    "        history = segment[:n]\n",
    "        future = segment[n:]\n",
    "        yield history, future\n",
    "\n",
    "orig_segments = segment_trading_data(data, 100, 12, False)\n",
    "norm_segments = segment_trading_data(data, 100, 12, True)\n",
    "\n",
    "orig_history, orig_future = next(orig_segments)\n",
    "norm_history, norm_future = next(norm_segments)\n",
    "\n",
    "draw_trading_data(pd.concat([orig_history, orig_future]), title='original', figsize=(8, 6));\n",
    "draw_trading_data(pd.concat([norm_history, norm_future]), title='normalized', figsize=(8, 6));"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5e7fe393-0909-4e62-a44d-963c74e97080",
   "metadata": {},
   "source": [
    "### 1. 4 - Put Together\n",
    "\n",
    "So far, the input data is segmented, normalized, and the labels are determined, the data pre-processing is done. The next step is to put the pieces together to have a comprehensive training data generation pipeline.\n",
    "\n",
    "Sometimes the neural network model contains the data pre-processing layers to achieve the end-to-end training and inference functionality. So it is a good practice to parameterize the pre-processing options when generating the training datasets. \n",
    "\n",
    "Also, when training the model with Tensorflow, PyTorch, or any other deep learning frameworks, usually the data is in `numpy.ndarray` or `tf.EagerTensor` format, so we transform the `pd.DataFrame` into numpy. Recall that the original data might contain columns other than OHLCV, so in this step we are removing unnecessary columns, and keep the columns in the OHLCV order so that we can reconstruct the data later with the same order."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 83,
   "id": "7a0c9ec0-1da1-4624-b6ca-b6e5a5401002",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "(144, 5) <class 'numpy.ndarray'> (6, 5) <class 'numpy.ndarray'>\n"
     ]
    }
   ],
   "source": [
    "from tools import compute_label\n",
    "\n",
    "def construct_training_data(data: pd.DataFrame, n: int=144, t: int=6, k_up=1., k_lo=None, norm=False, columns=None):\n",
    "    if columns is None:\n",
    "        columns = ['open', 'high', 'low', 'close', 'volume']\n",
    "    columns = list(columns)\n",
    "    segments = segment_trading_data(data=data, n=n, t=t, norm=norm)\n",
    "    for history, future in segments:\n",
    "        y = compute_label(history, future, k_up=k_up, k_lo=k_lo)\n",
    "        hist = history[columns].values\n",
    "        fut = future[columns].values\n",
    "        '''Converting history and future data from float64 into float32 format is to reduce the size of the data by half'''\n",
    "        yield hist.astype('float32'), y, fut.astype('float32')\n",
    "\n",
    "\n",
    "dataset = construct_training_data(data, n=144, t=6, norm=True)\n",
    "for history, y, future in dataset:\n",
    "    print(history.shape, type(history), future.shape, type(future))\n",
    "    break"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "3e185f7d-db0f-499c-bfa1-65def46037e7",
   "metadata": {},
   "source": [
    "## 2. Writing to File\n",
    "\n",
    "It is a good habbit to generate the training data and save them into files. \n",
    "\n",
    "Following the above instructions, one might notice that the training data samples are generated in a consecutive fashion, meaning that 2 adjacent segments share most of the same data except for 1 candle. This is harmful to model training if familiar with deep learning since it can cause the model to overfit the first few batches of data quickly and to stay in a local-minima position. To resolve this, randomizing the appearance of the segments is one of the most effective way, and saving data into files and randomly re-order them during loading does just that.\n",
    "\n",
    "Besides, neural network training often takes place on machines with GPU and running Linux operating systems, which might not have direct access to the original trading data. For instance, QUANTAXIS saves trading data into a specified MongoDB instance, usually in a Docker container, and accessing those data from the said GPU machines can be tiresome, but transmitting training dataset files and loading them is not.\n",
    "\n",
    "Moreover, if using Tensorflow, loading **.tfrecord** files is faster.\n",
    "\n",
    "Long story short, it's worth implementing the functionality to save the training data into files.\n",
    "\n",
    "When creating Tensorflow dataset buffer files, it's needed to convert the original training data into the right format, which can be done by serializing numpy arrays into `tfrecord` buffer strings, and it is implemented in the `tfannotation` module as function `create_tfrecord()`, the basic idea is to encode various types of data into their corresponding buffer strings."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 103,
   "id": "17c440bd-f397-435a-9892-1a5784b5cc8c",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 47007/47007 [03:38<00:00, 215.26it/s]\n"
     ]
    }
   ],
   "source": [
    "from utilities.funcs import create_file_name\n",
    "from dataset_management.tfannotation import create_tfrecord\n",
    "import tensorflow as tf\n",
    "from dataset_management.tools import construct_training_data\n",
    "from tqdm import tqdm\n",
    "\n",
    "\n",
    "dataset = construct_training_data(data, n=144, t=6, norm=True)\n",
    "\n",
    "# specify where you want to put the training dataset files and make sure the directories exist\n",
    "dataset_dir = _project_root / 'dataset'\n",
    "train_dir = dataset_dir / 'train'\n",
    "valid_dir = dataset_dir / 'valid'\n",
    "train_dir.mkdir(parents=True, exist_ok=True)\n",
    "valid_dir.mkdir(parents=True, exist_ok=True)\n",
    "split_ratio = .1\n",
    "\n",
    "for i, (history, y, future) in tqdm(enumerate(dataset), total=len(data) - (144 + 6) + 1):\n",
    "    file_name = f\"{create_file_name()}.tfrecords\"\n",
    "    \n",
    "    if i % (1 / split_ratio) < 1:\n",
    "        file_path = valid_dir / file_name\n",
    "    else:\n",
    "        file_path = train_dir / file_name\n",
    "    \n",
    "    with tf.io.TFRecordWriter(str(file_path)) as writer:\n",
    "        serialized = create_tfrecord(history=history, label=y, future=future)\n",
    "        writer.write(serialized)\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "c41f3a11-27a3-44c9-bfb4-356fb4894c17",
   "metadata": {},
   "source": [
    "The above code snippet creates several tfrec files under the `dataset/` directory, now let's check if we can read the data back from those files, and use the same code to load the dataset when training.\n",
    "\n",
    "To do so, the first step is to find all the files need to be loaded, then create a raw dataset of type `TFRecordDataset`. However, the current dataset cannot be fed into the model nor human-readable yet, because each sample in the dataset is the serialized version of the data, recall the serialization step when creating the files. This brings us to the second step - deserialization. The deserialization function is already implemented in the `tfannotation` module with name `read_tfrecord()`, which decodes a single serialized string, mapping the function with each of the samples in the raw dataset will eventually restore the dataset."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 127,
   "id": "e75dfc68-1530-4fa1-b4e3-71adf30c7526",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[INFO] 47007 files founded.\n",
      "sample #1:\n",
      "history var type: <class 'tensorflow.python.framework.ops.EagerTensor'> dtype: <dtype: 'float32'> shape: (144, 5)\n",
      "label   var type: <class 'tensorflow.python.framework.ops.EagerTensor'> dtype: <dtype: 'int64'> shape: ()\n",
      "future  var type: <class 'tensorflow.python.framework.ops.EagerTensor'> dtype: <dtype: 'float32'> shape: (6, 5)\n",
      "\n"
     ]
    }
   ],
   "source": [
    "from dataset_management.tfannotation import read_tfrecord\n",
    "\n",
    "def load_dataset(directory):\n",
    "    directory = Path(str(directory))\n",
    "    data_files = [str(p) for p in directory.rglob('*.tfrecords')]\n",
    "    print(f\"[INFO] {len(data_files)} files founded.\", flush=True)\n",
    "    \n",
    "    raw = tf.data.TFRecordDataset(data_files)\n",
    "    dataset = raw.map(read_tfrecord)\n",
    "    return dataset\n",
    "\n",
    "\n",
    "testsflush== load_dataset(dataset_dir)\n",
    "for i, sample in enumerate(testset):\n",
    "    print(f\"sample #{i + 1}:\")\n",
    "    history, label, future = sample\n",
    "    print(f\"history var type: {type(history)} dtype: {history.dtype} shape: {history.shape}\")\n",
    "    print(f\"label   var type: {type(label)} dtype: {label.dtype} shape: {label.shape}\")\n",
    "    print(f\"future  var type: {type(future)} dtype: {future.dtype} shape: {future.shape}\")\n",
    "    print()\n",
    "    break"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "59022606-2700-49d7-b5af-36c10a3a1215",
   "metadata": {},
   "source": [
    "## 3. Dataset Distribution Review\n",
    "\n",
    "Usually the dataset needs to be reviewed and adjusted before training the model since the dataset distribution might be skewed. In this particular case, this could mean that the 3 classes might be unbalanced due to the settings of the **TBM** parameters when creating the data samples. And a visualization of the classes distribution is one of the most straightforward ways to identify such issue."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 130,
   "id": "ead67dac-7c77-4433-81d9-4b6f2feb670d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[INFO] 42306 files founded.\n",
      "[INFO] 4701 files founded.\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "42306it [00:08, 4733.25it/s]\n",
      "336it [00:00, 3355.28it/s]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "label -1: 3,804\n",
      "label 0: 35,057\n",
      "label 1: 3,445\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "4701it [00:01, 4477.74it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "label -1: 411\n",
      "label 0: 3,910\n",
      "label 1: 380\n"
     ]
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    },
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAXwAAAD0CAYAAACYc53LAAAAOXRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjMuMywgaHR0cHM6Ly9tYXRwbG90bGliLm9yZy/Il7ecAAAACXBIWXMAAAsTAAALEwEAmpwYAAAQG0lEQVR4nO3db4xcV33G8e8D3uIEBZTaGzXE/7Z9g4RCUVjUgokMKkpiAwIExVKdBks0i136gr4IIuJFEG9amqpQgRrwCsmYIAqRAIGSdaxWjXGMBNogk7RFFVL9J4siYlspECQrtvn1xQwwNrvemfV6xsv5fqQr7/zumXvOlaVnz565d26qCknS774XjXoAkqThMPAlqREGviQ1wsCXpEYY+JLUiFWjHsBC1q5dW5s2bRr1MCRpRXniiSdOVdX4fPuu2sDftGkTs7Ozox6GJK0oSY4vtM8lHUlqRN+Bn+SzST7V/fnOJIe7246eNgPVJUnD09eSTpJ3AH8I/HeS9cAUsAUIcDDJIaAGqVfVieU+GUnSwhYN/CSvAO4CPgG8HdgKzFTVue7+GeB2OmE+SH162c9Gkpbg7NmzzM3NcebMmVEPpW+rV69m3bp1jI2N9f2eSwZ+khcBnwQ+BPxRt7wWONbT7Ciwnk6wD1Kfr78pOn8NsGHDhn7GL0mXbW5ujuuuu45NmzaRZNTDWVRVcfr0aebm5piYmOj7fYut4f8t8FBVPd1TOwVs7Hk9AZxeQv23VNWeqpqsqsnx8XmvKpKkZXfmzBnWrFmzIsIeIAlr1qwZ+C+SxQL/zcDfJHkM+BTwHuBPgW1JViUZA7YBB4D9A9Yl6aqxUsL+V5Yy3ksu6VTV23oO/ibgnVX1oSR3AYe6ux6oqmPdNtOD1CXparTpIw8v6/GO/f1bl/V4S9X3jVdV9RjwWPfnfcC+edoMVJckze/8+fN88Ytf5N577+WZZ55ZlmNetXfaSgP52MtHPYIr62M/HfUINGTT09Ncf/313HDDDct2TO+0laSr0K5du9i+ffuyfrZg4EtSI1zSkaQR27t3L3v37r2gtn37dnbv3r2s/Rj4kjRiO3fuZOfOnVe8HwNfki5ytVxGudxcw5ekq9iRI0eW7VgGviQ1wsCXpEYY+JLUCANfkhph4EtSI7wsU5IuttzfzXSVfBeSM3xJugo8+OCDbN68mc2bN/OlL33pivThDF+SRuzpp59mz549HDx4kKpiy5Yt3Hrrrcv+qFdn+JI0YjMzM2zdupVVq1YxNjbG1q1befTRR5e9HwNfkkbs1KlTbNz4m0d/T0xMcOrUqWXvx8CXpBFbu3Ytx48f//Xro0ePsmbNmmXvx8CXpBG74447eOSRRzh37hxnz57lkUce4bbbblv2fvr60DbJh4H3AeeBA8AXgW8B/9vT7M+q6nySe4B3AAHuq6p/6x5j3rokXXWGfBnlhg0buPvuu7n11lsB2L17N5s2bVr2fhYN/CS3AHcArwZ+CXwTeCvw6aq6/6K2rwdeB9wKXAd8O8nm7nt/q15Vv1jGc5GkFeuuu+7irrvuuqJ99LOk8yPg3VV1HriWTmCfBjYmmUlyKMk7u23fDny9On4GPAG84RL1CySZSjKbZPbkyZOXfXKSpN9YNPCr6udV9VyS9wNzwCzwf8Ax4G3AO4H7krwCWAsc73n70W5tofrFfe2pqsmqmhwfH1/K+UiSFrBo4Ce5Psm1VfV54EZgHfA88MmqOl9Vp4F/B14FnAI29rx9gs5fAwvVJUlD0s+SzluBjycJ8AJwBvgH4C8BklwDvB74IfAw8K50vAyYBL5zibokaUj6uUrny8Bm4Ek6V9g8SifgP5/kr4GzwD9V1Rwwl+SNwOFu23uq6nng8AJ1SdKQLBr43Q9rd8+z688XaP8J4BP91iXpanPzF25e1uM99b6nlvV4S+WNV5I0YufPn2fv3r3ceOONV7QfA1+SRmx6epprrrmGG2644Yr2Y+BL0ojt2rWL7du307k25sox8CWpEQa+JDXCwJekRviIQ0m6yNVyGeVyc4YvSVeJI0eOXNHjG/iS1AgDX5IaYeBLElBVox7CQJYyXgNfUvNWr17N6dOnV0zoVxWnT59m9erVA73Pq3QkNW/dunXMzc2xkp60t3r1atatWzfQewx8Sc0bGxtjYmJi1MO44lzSkaRGGPiS1AgDX5IaYeBLUiP6CvwkH07yX0meTPKP3YeR35Pk8SSHk7ylp+1AdUnScCx6lU6SW4A7gFcDvwS+CbwBeB1wK3Ad8O0km7tt+q5X1S+W/YwkSfPqZ4b/I+Dd3YeZX0snsD8IfL06fgY8QeeXwNsHrEuShmTRwK+qn1fVc0neD8wBs8AvgOM9zY4Ca7vbIPULJJlKMptkdiXdACFJK8GigZ/k+iTXVtXngRuBdcCrgI09zSaA08CpAesXqKo9VTVZVZPj4+ODnosk6RL6WdJ5K/DxdJ6u+wJwBngYeFf3w9uXAZPAd5ZQlyQNST9frfBlYDPwJBDgUeDvgHuAw93aPVX1PHA4yRsHqEuShiRX67fDTU5O1uzs7KiHoZXiYy8f9QiurI/9dNQj0AqR5ImqmpxvnzdeSVIjDHxJaoSBL0mNMPAlqREGviQ1wsCXpEYY+JLUCANfkhph4EtSIwx8SWqEgS9JjTDwJakRBr4kNcLAl6RGGPiS1AgDX5IaYeBLUiMMfElqhIEvSY3oK/CT7EryeJInk3w8ycuTPJvksZ7tpm7bO5Mc7m47eo4xb12SNByrFmuQ5JXAe4A3AeeBR4E/Bh6qqg9e1HY9MAVsAQIcTHIIqPnqVXVi+U5FknQp/czwVwP3V9W5qirgGeBPgOuSfKM7Y/9At+1WYKbb9iwwA9x+ifoFkkwlmU0ye/LkyWU4PUnSryw6w6+qIwBJAtwNnAVmgd8H/goYA76VZBZYCxzreftRYD2dWf189Yv72gPsAZicnKwBz0WSdAmLBj5AkpcC/wwcoRP6q4HHu7P1F5J8DbgFOAVs7HnrBPCT7s8L1SVJQ7Dokk6SlwDfAj5XVZ/pLuvsAD7a3b8KeAvwA2A/sC3JqiRjwDbgwCXqkqQh6WeG/w7gZuD+zqoOAPcBr03yfeAM8GBVfQ8gyTRwqNvugao6dqm6JGk4+lnD/yrw1Xl2HVyg/T5gX791SdJweOOVJDXCwJekRhj4ktQIA1+SGmHgS1IjDHxJaoSBL0mNMPAlqREGviQ1wsCXpEYY+JLUCANfkhph4EtSIwx8SWqEgS9JjTDwJakRBr4kNcLAl6RG9BX4SXYleTzJk0k+no47kxzubjt62g5UlyQNx6LPtE3ySuA9wJuA88CjwBuBKWALEOBgkkNADVKvqhPLfUKSpPktGvjAauD+qjoHkOQZ4PXATE9tBridTpgPUp9e3tORJC1k0cCvqiMASQLcDZwFxoCjPc2OAuvpBPuxAeoXSDJF5y8BNmzY0O85SJL60O8a/kvpzMZ/j07onwQ29jSZAE4DpwasX6Cq9lTVZFVNjo+PD3AakqTFLBr4SV4CfAv4XFV9pqoK2A9sS7IqyRiwDTiwhLokaUj6WcN/B3AzcH9nVQeA++jM+A91Xz9QVccAkgxUlyQNRz9r+F8FvrrA7n3ztN83SF2SNBzeeCVJjTDwJakRBr4kNcLAl6RGGPiS1AgDX5IaYeBLUiMMfElqhIEvSY0w8CWpEQa+JDXCwJekRhj4ktQIA1+SGmHgS1IjDHxJaoSBL0mNMPAlqREGviQ1ou/AT/LiJDuTPJPkZUmeTfJYz3ZTt92dSQ53tx0975+3LkkajkUfYt7jbuA54FlgHfBQVX2wt0GS9cAUsAUIcDDJIaDmq1fVics/BUlSP/qe4VfVZ6vqK3TC+ybguiTf6M7YP9BtthWYqapzVXUWmAFuv0T9AkmmkswmmT158uRlnpokqddS1/DPAj8G3gvcBmxP8lpgLXC8p93Rbm2h+gWqak9VTVbV5Pj4+BKHJkmazyBLOr2+CxzuztZfSPI14BbgFLCxp90E8JPuzwvVJUlDsNQZ/g7gowBJVgFvAX4A7Ae2JVmVZAzYBhy4RF2SNCRLneHvBT6d5PvAGeDBqvoeQJJp4FC33QNVdexSdUnScAwc+FX1mu6PuxfYvw/Y129dkjQc3nglSY0w8CWpEQa+JDXCwJekRhj4ktQIA1+SGmHgS1IjDHxJaoSBL0mNMPAlqREGviQ1wsCXpEYY+JLUCANfkhph4EtSIwx8SWqEgS9JjTDwJakRfQd+khcn2Znkme7rO5Mc7m47etoNVJckDccgz7S9G3gOeDbJemAK2AIEOJjkEFCD1KvqxLKdiSTpkvoO/Kr6LECSe4GtwExVnevWZoDb6YT5IPXp5TsVSdKlLHUNfy1wvOf10W5t0PoFkkwlmU0ye/LkySUOTZI0n6UG/ilgY8/rCeD0EuoXqKo9VTVZVZPj4+NLHJokaT5LDfz9wLYkq5KMAduAA0uoS5KGZJAPbX+tqk4kmQYOdUsPVNUxgEHrkqThGDjwq+o13X/3Afvm2T9QXZI0HN54JUmNMPAlqREGviQ1wsCXpEYY+JLUCANfkhph4EtSIwx8SWqEgS9JjTDwJakRBr4kNcLAl6RGGPiS1AgDX5IaYeBLUiMMfElqhIEvSY0w8CWpEQa+JDViyYGf5GVJnk3yWM92U5I7kxzubjt62s9blyQNx8APMe+xDnioqj74q0KS9cAUsAUIcDDJIaDmq1fVicvoX5I0gMsJ/JuA65J8AxgH9tEJ9pmqOgeQZAa4nU7Iz1ef7j1gkik6vxjYsGHDZQxNknSxy1nDPwv8GHgvcBuwnU7wH+9pcxRY293mq1+gqvZU1WRVTY6Pj1/G0CRJF7ucGf53gcNVdRZ4IcnX6PwS2NjTZgL4SffnheqSpCG4nBn+DuCjAElWAW8BfghsS7IqyRiwDTgA7F+gLkkaksuZ4e8FPp3k+8AZ4MGq+naSaeBQt80DVXUMYKG6JGk4lhz43Q9gd89T30fnA9y+6hqOTR95eNRDuKKOrR71CKSrnzdeSVIjLmdJR9KQ3PyFm0c9hCvmqfc9NeohNMMZviQ1wsCXpEYY+JLUCANfkhph4EtSIwx8SWqEgS9JjTDwJakRBr4kNcLAl6RGGPiS1AgDX5IaYeBLUiMMfElqhIEvSY0w8CWpEUMN/CR3Jjnc3XYMs29Jat3QnniVZD0wBWwBAhxMcqiqTgxrDJLUsmHO8LcCM1V1rqrOAjPA7UPsX5KaNsxn2q4FjvW8Pgqs722QZIrOXwEAzyf5n+EMTStdht/lWuDU8Lr7z+F1NWTZOYL/vd9tGxfaMczAP3XRQCaAn/Q2qKo9wJ4hjklakiSzVTU56nFIgxjmks5+YFuSVUnGgG3AgSH2L0lNG9oMv6pOJJkGDnVLD1TVsWH1L0mtS1WNegzSipNkqrsEKa0YBr4kNcI7bSWpEQa+JDXCwJekRgzzOnxpxUqyjs6d4WuB08ABvxZEK40zfGkRSf4C+ArwB8Bc999/9QsAtdJ4lY60iCSHgDdX1bme2hjwWFVtHt3IpME4w5cWF+D8RbXzjOQrfKSlcw1fWtwDwH8kmQGOA5vofPvrv4xyUNKgXNKR+tD90HYrv/mWzP1V9fRoRyUNxsCXpEa4hi9JjTDwJakRBr4kNcLAl6RG/D8S2BHG8o0acgAAAABJRU5ErkJggg==\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "trainset = load_dataset(train_dir)\n",
    "validset = load_dataset(valid_dir)\n",
    "\n",
    "\n",
    "def visualize_label_distribution(dataset):\n",
    "    labels = [-1, 0, 1]\n",
    "    label_counts = {k: 0 for k in labels}    \n",
    "    \n",
    "    for history, label, future in tqdm(dataset):\n",
    "        label = label.numpy()\n",
    "        label_counts[label] += 1\n",
    "\n",
    "    for lb in labels:\n",
    "        print(f\"label {lb}: {label_counts[lb]:,d}\", flush=True)\n",
    "    pd.DataFrame(label_counts, columns=label_counts.keys(), index=[0]).plot.bar();\n",
    "    \n",
    "\n",
    "visualize_label_distribution(trainset)\n",
    "visualize_label_distribution(validset)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "385c6719-474d-4d8d-81bd-678dc9fc28d6",
   "metadata": {},
   "source": [
    "The above results depicts that the dataset is extremely unbalanced since the majority of the data samples are labeled 0, this implies that training the deep learning models directly with this dataset might not lead to a robust result and that:\n",
    "\n",
    "1. either a weighted loss function needs to be implemented during training;\n",
    "2. or some kind of data augmentation method needs to be adopted;\n",
    "\n",
    "One easy way of eliminating the distribution skewness is randomly removing some of the data with label 0 to have a balanced dataset, however, doing so will decrease the size of the training set dramatically.\n",
    "\n",
    "Another possible way is to tune the **TBM** parameters, it could be to increase the window size of the future $T$ to give it more time for the asset to reach either horizontal barriers, or decrease the $k$ parameters so that reaching the take profit or stop loss thresholds become more tangible. \n",
    "\n",
    "Have fun generating your own financial datasets!"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "9930d921-e2d7-408f-8bb5-9c465e5054d7",
   "metadata": {},
   "source": [
    "# JUST SOME EXPERIMENTS\n",
    "\n",
    "The following is just some experimental code to try to resolve the unbalancing issue."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 133,
   "id": "caab6667-64ce-468c-ab8a-34e9a04eb7fb",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "  0%|          | 28/47001 [00:00<05:31, 141.85it/s]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[INFO] creating tfrec files\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 47001/47001 [03:58<00:00, 196.87it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[INFO] 42300 files founded.\n",
      "[INFO] 4701 files founded.\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "42300it [00:16, 2497.96it/s]\n",
      "427it [00:00, 1925.35it/s]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "label -1: 7,839\n",
      "label 0: 27,373\n",
      "label 1: 7,088\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "4701it [00:02, 1958.21it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "label -1: 871\n",
      "label 0: 3,043\n",
      "label 1: 787\n"
     ]
    },
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAYIAAAD0CAYAAACW9iHhAAAAOXRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjMuMywgaHR0cHM6Ly9tYXRwbG90bGliLm9yZy/Il7ecAAAACXBIWXMAAAsTAAALEwEAmpwYAAANIElEQVR4nO3dwWuc+X3H8fe3kRotwTGLZVNjWZZuuZhCdqAU1ziFxV6ph1xCRGvj+FArNvsHNCWHmBxKwaeSUqfSRVm80GRhWVhi2YbSVbU+JJUXN1soPUm2tWzXkggLPZiV1G8PM9mOjb2eGY3m0ezv/YIHa77zm+f5PhjmM7/neeaZyEwkSeX6vaobkCRVyyCQpMIZBJJUOINAkgpnEEhS4QaqbqBdw8PDOTY2VnUbktRX7t69u56ZB5/1XN8FwdjYGEtLS1W3IUl9JSLuP+85Dw1JUuEMAkkqnEEgSYXru3MEktQrm5ubrK6u8vjx46pbadnQ0BAjIyMMDg62/BqDQJKeY3V1lX379jE2NkZEVN3OC2UmGxsbrK6uMj4+3vLrPDQkSc/x+PFjDhw40BchABARHDhwoO0ZjEEgSV+gX0Lgdzrp10NDktSisR/8sqvrW/nbP+vq+jrljECS+sj29jZzc3McPny4a+t0RqAvtyv7q+5gd135tOoO1GOzs7O8/PLLHDp0qGvrdEYgSX3k0qVLTE1NdfXchUEgSYXz0JAk7VFzc3PMzc09UZuamuLy5ctd3Y5BIEl71IULF7hw4cKub8cgkKQW7ZXLPbvNcwSS1Ifu3bvXtXUZBJJUOINAkgpnEEhS4QwCSSqcQSBJhfPyUUlqVbfvXbVH7hXljECS9rDr169z4sQJTpw4wZtvvrkr23BGIEl71MOHD5mZmWFhYYHM5NSpU5w8eZLR0dGubqelGUFEXIqI9yPiNxHx44jYHxGPIuK9puVIY+y5iLjTWM42raOtuiSVbn5+nomJCQYGBhgcHGRiYoJbt251fTsvnBFExDeA7wDfAraBW8AfAm9l5utPjT0KTAOngAAWImIRyHbqmfmgK3snSX1sfX2dsbGxzx+Pj4/z8OHDrm+nlRnBEHA1M7cyM4GPgT8C9kXEO41P8t9vjJ0A5htjN4F54EwHdUkq3vDwMPfv3//88fLyMgcOHOj6dl4YBJl5LzNvRd00sAksAR8B3wVOA1MR8QowDNxvevlyo9Zu/QkRMR0RSxGxtLa21s7+SVLfeu2117hx4wZbW1tsbm5y48YNTp8+3fXttHSyOCK+BvwdcA+4SH2W8H7jU/xnEfE28E1gHTjW9NJx4JPG3+3WP5eZM8AMQK1Wy1Z6lqSu6/HlnqOjo1y8eJGTJ08CcPny5ScOFXVLK+cIvgq8C/xVZv5bo3YWGAGuRMQA8CrwN8B/A29GxFXqx/wngT8H/rfNuiQJOH/+POfPn9/VbbQyI/g2cBy42vQbmT8CXomID4DHwPXM/DVARMwCi41x1zJzpZO6JKk3XhgEmfkL4BfPeGrhOePfAN7YaV2S1Bt+s1iSCmcQSFLhDAJJKpz3GpKkFh3/2fGuru/D733Y1fV1yhmBJO1R29vbzM3Ncfjw4V3djkEgSXvU7OwsL730EocOHdrV7RgEkrRHXbp0iampKZq+w7UrDAJJKpxBIEmFMwgkqXBePipJLdorl3t2mzMCSdrj7t27t6vrNwgkqXAGgSQVziCQpC9Q/6n2/tFJvwaBJD3H0NAQGxsbfRMGmcnGxgZDQ0Ntvc6rhiTpOUZGRlhdXWVtba3qVlo2NDTEyMhIW68xCCTpOQYHBxkfH6+6jV3noSFJKpxBIEmFMwgkqXAGgSQVziCQpMIZBJJUOINAkgpnEEhS4QwCSSqcQSBJhTMIJKlwBoEkFa6lIIiISxHxfkT8JiJ+HHXnIuJOYznbNLYrdUlSb7zw7qMR8Q3gO8C3gG3gFvAnwDRwCghgISIWgexGPTMfdHEfJUlfoJXbUA8BVzNzCyAiPgb+GJhvqs0DZ6i/mXejPtvcQERMUw8MRkdHd7K/kqSnvDAIMvMeQEQEcBHYBAaB5aZhy8BR6m/sK12oP93DDDADUKvV+uOngiSpT7R6juBr1D+l/z71MFgDjjUNGQc2gPUu1SVJPfLCIIiIrwLvAv+YmX+f9R/vvAlMRsRARAwCk8DtLtYlST3SyjmCbwPHgav1o0MA/Ij6DGGx8fhaZq4ARERX6pKk3oj6B/z+UavVcmlpqeo21C+u7K+6g9115dOqO1CfiIi7mVl71nN+oUySCmcQSFLhDAJJKpxBIEmFMwgkqXAGgSQVziCQpMIZBJJUOINAkgpnEEhS4QwCSSqcQSBJhTMIJKlwBoEkFc4gkKTCGQSSVDiDQJIKZxBIUuEMAkkqnEEgSYUzCCSpcAaBJBXOIJCkwhkEklQ4g0CSCmcQSFLhDAJJKpxBIEmFMwgkqXAGgSQVruUgiIivRMSFiPg4Ir4eEY8i4r2m5Uhj3LmIuNNYzja9vq26JKk3BtoYexH4LfAIGAHeyszXmwdExFFgGjgFBLAQEYtAtlPPzAc72itJUstanhFk5k8z8+fU37yPAPsi4p3GJ/nvN4ZNAPOZuZWZm8A8cKaD+hMiYjoiliJiaW1tbQe7K0l6WqfnCDaBj4DvAqeBqYh4BRgG7jeNW27U2q0/ITNnMrOWmbWDBw922LIk6VnaOTTU7FfAncan+M8i4m3gm8A6cKxp3DjwSePvduuSpB7odEZwFvghQEQMAK8C/w7cBCYjYiAiBoFJ4HYHdUlSj3Q6I5gDfhIRHwCPgeuZ+WuAiJgFFhvjrmXmSid1SVJvRGZW3UNbarVaLi0tVd2G+sWV/VV3sLuufFp1B+oTEXE3M2vPes4vlElS4QwCSSqcQSBJhTMIJKlwBoEkFc4gkKTCGQSSVDiDQJIKZxBIUuEMAkkqnEEgSYUzCCSpcAaBJBXOIJCkwhkEklQ4g0CSCmcQSFLhDAJJKpxBIEmFMwgkqXAGgSQVziCQpMIZBJJUOINAkgpnEEhS4QwCSSqcQSBJhTMIJKlwBoEkFa7lIIiIr0TEhYj4uPH4XETcaSxnm8Z1pS5J6o2BNsZeBH4LPIqIo8A0cAoIYCEiFoHsRj0zH3Rj5yRJL9ZyEGTmTwEi4q+BCWA+M7catXngDPU3827UZ7uyd5KkF+r0HMEwcL/p8XKj1q36EyJiOiKWImJpbW2tw5YlSc/SaRCsA8eaHo8DG12sPyEzZzKzlpm1gwcPdtiyJOlZOg2Cm8BkRAxExCAwCdzuYl2S1CPtnCz+XGY+iIhZYLFRupaZKwDdqkuSeiMys+oe2lKr1XJpaanqNtQvruyvuoPddeXTqjtQn4iIu5lZe9ZzfqFMkgpnEEhS4QwCSSqcQSBJhTMIJKlwBoEkFc4gkKTCGQSSVDiDQJIKZxBIUuEMAkkqXEc3ndOXx9gPfll1C7tqZajqDqS9zxmBJBXOIJCkwhkEklQ4g0CSCmcQSFLhvGpI6mPHf3a86hZ2zYff+7DqForhjECSCmcQSFLhDAJJKpxBIEmFMwgkqXAGgSQVziCQpMIZBJJUOINAkgpnEEhS4QwCSSqcQSBJhes4CCLi6xHxKCLea1qORMS5iLjTWM42jW+rLknqjZ3cfXQEeCszX/9dISKOAtPAKSCAhYhYBLKdemY+2EFfkqQ27CQIjgD7IuId4CDwBvU39vnM3AKIiHngDPU3+XbqszvoS5LUhp0EwSbwEfCXwCDwLvDPwHLTmGXgKPU3/JU26k+IiGnqMwdGR0d30LIk6Wk7CYJfAXcycxP4LCLeph4Ox5rGjAOfNP5ut/65zJwBZgBqtVruoGdJ0lN2ctXQWeCHABExALwK/CcwGREDETEITAK3gZtt1iVJPbKTGcEc8JOI+AB4DFzPzH+NiFlgsTHmWmauALRblyT1RsdB0DjBe/kZ9TeonzjeUV2S1Bt+oUySCmcQSFLhDAJJKpxBIEmFMwgkqXAGgSQVziCQpMIZBJJUOINAkgpnEEhS4QwCSSqcQSBJhTMIJKlwBoEkFc4gkKTCGQSSVDiDQJIKZxBIUuEMAkkqnEEgSYUzCCSpcAaBJBXOIJCkwhkEklQ4g0CSCmcQSFLhDAJJKpxBIEmFMwgkqXAGgSQVbk8EQUSci4g7jeVs1f1IUkkGqm4gIo4C08ApIICFiFjMzAfVdiZJZdgLM4IJYD4ztzJzE5gHzlTckyQVo/IZATAMrDQ9XgaONg+IiGnqswaA/4mI/+pNa+p30ftNDgPrvdvcf/RuUz0WFyr43/tyO/a8J/ZCEKzzZIPjwCfNAzJzBpjpZVNSJyJiKTNrVfchtWMvHBq6CUxGxEBEDAKTwO2Ke5KkYlQ+I8jMBxExCyw2Stcyc6XCliSpKJGZVfcgfWlExHTjUKbUNwwCSSrcXjhHIEmqkEEgSYUzCCSpcJVfNST1s4gYof5N+GFgA7jt7VHUb5wRSB2KiL8Afg78AbDa+PefvHGi+o1XDUkdiohF4E8zc6upNgi8l5knqutMao8zAqlzAWw/VdumklscSZ3zHIHUuWvAv0TEPHAfGKN+N91/qLIpqV0eGpJ2oHGyeIL/v+vozcx8WG1XUnsMAkkqnOcIJKlwBoEkFc4gkKTCGQSSVLj/AzYN5yV2xHeGAAAAAElFTkSuQmCC\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "params = dict(\n",
    "    n=144, \n",
    "    t=12,\n",
    "    k_up=1.,\n",
    "    norm=True\n",
    ")\n",
    "dataset = construct_training_data(data, **params)\n",
    "\n",
    "dataset_dir = _project_root / 'dataset'\n",
    "train_dir = dataset_dir / 'train'\n",
    "valid_dir = dataset_dir / 'valid'\n",
    "train_dir.mkdir(parents=True, exist_ok=True)\n",
    "valid_dir.mkdir(parents=True, exist_ok=True)\n",
    "split_ratio = .1\n",
    "\n",
    "print(f\"[INFO] creating tfrec files\", flush=True)\n",
    "for i, (history, y, future) in tqdm(enumerate(dataset), total=len(data) - (params[\"n\"] + params[\"t\"]) + 1):\n",
    "    file_name = f\"{create_file_name()}.tfrecords\"\n",
    "    \n",
    "    if i % (1 / split_ratio) < 1:\n",
    "        file_path = valid_dir / file_name\n",
    "    else:\n",
    "        file_path = train_dir / file_name\n",
    "    \n",
    "    with tf.io.TFRecordWriter(str(file_path)) as writer:\n",
    "        serialized = create_tfrecord(history=history, label=y, future=future)\n",
    "        writer.write(serialized)\n",
    "\n",
    "\n",
    "trainset = load_dataset(train_dir)\n",
    "validset = load_dataset(valid_dir)\n",
    "\n",
    "\n",
    "def visualize_label_distribution(dataset):\n",
    "    labels = [-1, 0, 1]\n",
    "    label_counts = {k: 0 for k in labels}    \n",
    "    \n",
    "    for history, label, future in tqdm(dataset):\n",
    "        label = label.numpy()\n",
    "        label_counts[label] += 1\n",
    "\n",
    "    for lb in labels:\n",
    "        print(f\"label {lb}: {label_counts[lb]:,d}\")\n",
    "    pd.DataFrame(label_counts, columns=label_counts.keys(), index=[0]).plot.bar();\n",
    "    \n",
    "\n",
    "visualize_label_distribution(trainset)\n",
    "visualize_label_distribution(validset)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
