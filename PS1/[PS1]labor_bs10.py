# -*- coding: utf-8 -*-
"""


@author: Joan Alegre, Boyao Zang, Pau Belda
"""


import pandas as pd
import numpy as np
import os


os.chdir('/Users/Pau_Belda/Documents/Uni/Màster IDEA/2nd year/Development/PS1')
pd.options.display.float_format = '{:,.2f}'.format

dollars = 2586.89

#%%Income 

lab9 = pd.read_stata("GSEC8_1.dta")
lab9 = lab9[["HHID","h8q30a","h8q30b", "h8q31a","h8q31b","h8q31c","h8q44","h8q44b","h8q45a","h8q45b","h8q45c"]]     
lab9.columns = [["hh","months1","weeks1", "cash1","inkind1", "time1","months2","weeks2", "cash2","inkind2", "time2"]]



lab9["pay1"] = lab9.loc[:,["cash1","inkind1"]].sum(axis=1)
lab9["pay2"] = lab9.loc[:,["cash2","inkind2"]].sum(axis=1)
del lab9["cash1"], lab9["inkind1"], lab9["cash2"], lab9["inkind2"]


#Creating week wages

#We don't have info about months and weeks worked. We use the sample mean of 2013-2014. Note that this can hidden important inequality on work time.
lab9["wag"] =np.multiply(lab9[('months1')],lab9[('weeks1')])
lab9["wage1"] =np.multiply(lab9["wag"],lab9["pay1"])
lab9["wa"] =np.multiply(lab9[('months2')],lab9[('weeks2')])
lab9["wage2"] =np.multiply(lab9["wag"],lab9["pay2"])

#lab9.columns
lab9 = pd.DataFrame(columns=["hh","cash1","cash2","inkind1","inkind2","months1","months2","time1","time2","weeks1","weeks2","pay1","pay2","wag","wage1","wa","wage2","A"])
lab99 = lab9.groupby(by="hh")[["wage1","wage2"]].sum()
lab99["wage_total"] = lab99.loc[:,["wage1","wage2"]].sum(axis=1)
lab99= lab99.replace(0, np.nan)


lab99["hh"] = np.array(lab99.index.values)
summaryw = lab99.describe()/dollars
#print(summaryw.to_latex())

del lab9

#%% business

bus12 = pd.read_stata('gsec12.dta')
bus12 = bus12[["hhid","h12q12", "h12q13","h12q15","h12q16","h12q17"]]
bus12.rename(columns={'hhid':'hh'}, inplace=True)
bus12.rename(columns={'h12q13':'revenue'}, inplace=True)
bus12["cost"] = -bus12.loc[:,["h12q15","h12q16","h12q17"]].sum(axis=1)
bus12["bs_profit"] = bus12.loc[:,["revenue","cost"]].sum(axis=1)
bus12["bs_profit"] = bus12["bs_profit"].replace(0,np.nan)
bus12 = bus12[["hh","bs_profit"]]
bus12 = bus12.groupby(by="hh").sum()

bus12["hh"] = np.array(bus12.index.values)

summarybus = bus12.describe()/dollars

#print(summarybus.to_latex())

#%% Other income

other = pd.read_stata('GSEC11A.dta')
other = other[["HHID","h11q5","h11q6"]]
other.rename(columns={'HHID':'hh'}, inplace=True)
other["other_inc"] = other.loc[:,["h11q5","h11q6"]].sum(axis=1)
other = other[["hh","other_inc"]]
other = other.groupby(by="hh").sum()
other = other
other["hh"] = np.array(other.index.values)
summaryo = other.describe()/dollars



# extra-expenditures ---------------------------------------
# NO QUESTIONARY IN EXTRA EXPENDITURES





#%% Merge datasets
income_gsec = pd.merge(lab99, bus12, on="hh", how="outer")
income_gsec = pd.merge(income_gsec, other, on="hh", how="outer")
del income_gsec["wage1"], income_gsec["wage2"], bus12,  dollars, other, lab99, summarybus, summaryo, summaryw

sumlab = income_gsec[["wage_total","bs_profit", "other_inc"]].describe()
#print(sumlab.to_latex())

income_gsec.to_csv('income_hhsec_2010.csv')
