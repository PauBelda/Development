# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 00:01:53 2019

@author: Joana
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
os.chdir('C:/Users/Joana/Desktop/Cole/18-19/2.Development/ps1/data')
dollars = 2586.89

import statsmodels.formula.api as sm
from statsmodels.iolib.summary2 import summary_col
pd.options.display.float_format = '{:,.2f}'.format
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt


##%%
#Data = pd.read_csv("gsec1.csv")
#Data = Data[["HHID","HHID_old"]]
#Data2 = pd.read_csv("agsec1.csv")
#Data2 = Data2[["hh","HHID_old"]]
#Data2.columns = ['HHID', 'HHID_old']
#A = Data.merge(Data2, on="HHID", how="right")
#%% Summary for making database:
'''WEALTH: I constructed wealth from H.H questionary taking the value of assets, and from agricultural questionary taking
the living stock quantities and multiplying it by their prices, the prices were estimated
by the median of all the people that bough. I convert this prices to dolars, no data about land has been used. '''

'''INCOME: I find income wages from H.H taking pay in cash and kind, and other income, standarizing it by period of time
earned, and in dollar prices.
I find agricultural inputs cost, taking value of fertilizer, value of seed, value of pestizide, with this we get cost of agricultural inputs
Now I compute the cost of the labour of the farm activity, to do so I compute
total hours of the household member and outsiders. Wages are computed from the part
is paid for outsiders.
To find income of the farm I used value of the crop sold and the quantity sold,
I use the median of the value per quantity to get the prices of evey cropt, 
converted all the quantities into Kg. I use this prices to compute the total
value of the production. 
To convert everything Bunch has not been used since I did not know equivalence with
Kg, Lts have been used but assuming density of 1 of the products inside the bins.
'''

'''CONSUMPTION: We compute total consumption from nondurable consumption goods and food consumption.
To do so we sum all the values from purchases, gifts, own_value and home value'''
#%% ############ Food Consumption
C = pd.read_csv("gsec15b.csv")
C = C[["HHID","itmcd","h15bq4","h15bq5","h15bq6","h15bq7","h15bq8","h15bq9","h15bq10","h15bq11","h15bq12","h15bq13"]]
C.columns = ["hh","code", "purch_home_quant","purch_home_value","purch_away_quant","purch_away_value","own_quant","own_value","gift_quant","gift_value", "m_p", "gate_p"]

pricescons = C.groupby(by="code")[["m_p", "gate_p"]].median() #This is gathering by type of food and finding the median. 

pricescons.to_csv("pricesfood.csv") #This saves the vector into a new document in my folder.


############### Own value lives stock.
livestock = C.loc[C["code"].isin([117,118,119,120,121,122,123,124,125]),["hh","own_value"]] #I think the logic of this is: 
#we use isin for making all the rows with items of 117-125 true and else false and loc take variables hh and own_ value for the true values.

livestock = livestock.groupby(by="hh").sum()*52 #We sum all values and multiply by number of weeks of a year.
suml = livestock.describe()/dollars #Describe gives main statistics ( mean, max, quartile...) of livestock.

############### Aggregate across items.
C = C.groupby(by="hh")[["purch_home_quant","purch_home_value","purch_away_quant","purch_away_value","own_quant","own_value","gift_quant","gift_value"]].sum()

C = C[["purch_home_value", "purch_away_value", "own_value","gift_value"]]

C["cfood"] = C[["purch_home_value", "purch_away_value", "own_value","gift_value"]].sum(axis=1)

C.rename(columns={'total_value':'cfood'}, inplace=True)
C.rename(columns={'gift_value':'cfood_gift'}, inplace=True)
C.rename(columns={'own_value':'cfood_own'}, inplace=True)

C["cfood_purch"] = C.loc[:,["purch_home_value","purch_away_value"]].sum(axis=1) 
C["cfood_nogift"] = C.loc[:,["cfood_purch","own_value"]].sum(axis=1)

############### Food consumption at year level
C = C[["cfood", "cfood_nogift", "cfood_own", "cfood_purch", "cfood_gift"]]*52

C.reset_index(inplace=True)

data = C

########## Non-durable Non-food goods:
C = pd.read_csv("gsec15c.csv")
C = C[["HHID","itmcd","h15cq5","h15cq7","h15cq9","h15cq10"]]#We take columns of interest
C.columns = ["hh","code","purch_value","own_value","gift_value", "m_p"] # we rename them
C = C.groupby(by="hh")[["hh","code","purch_value","own_value","gift_value", "m_p"]].sum() #aggregate

C['cnodur'] = C.fillna(0)["purch_value"] + C.fillna(0)["own_value"] + C.fillna(0)["gift_value"] #fill everything NaN with 0.
C["cnodur_nogift"] = C.loc[:,["purch_value","own_value"]].sum(axis=1)
C.rename(columns={'gift_value':'cnodur_gift'}, inplace=True)
C.rename(columns={'own_value':'cnodur_own'}, inplace=True)
C.rename(columns={'purch_value':'cnodur_purch'}, inplace=True)

# non food non durable consumption at year level
C = C[["cnodur", "cnodur_nogift", "cnodur_own", "cnodur_purch", "cnodur_gift"]]*12
C.reset_index(inplace=True)

data = data.merge(C, on="hh", how="outer")



###### DURABLE CONSUMPTION
C = pd.read_csv("gsec15d.csv")
C = C[["HHID","h15dq2","h15dq3","h15dq4","h15dq5"]]
C.columns = ["hh","code","purch_value","own_value","gift_value"]

C = C.groupby(by="hh")[["purch_value","own_value","gift_value"]].sum() #I use 
C['Cdurable'] = C.fillna(0)["purch_value"] + C.fillna(0)["own_value"] + C.fillna(0)["gift_value"]

C.rename(columns={'Cdurable':'cdur'}, inplace=True)
C.reset_index(inplace=True)

data = data.merge(C, on="hh", how="outer") #outer is taking all the elements, inner is only taking
# data for the matches, left is focus only on the left framedata, and right is only for right framdata.
######## Create join variables

data["ctotal"] = data.loc[:,["cfood","cnodur"]].sum(axis=1)
data["ctotal_dur"] = data.loc[:,["cfood","cnodur","cdur"]].sum(axis=1)

data["ctotal_gift"] = data.loc[:,["cfood_gift","cnodur_gift"]].sum(axis=1)
data["ctotal_dur_gift"] = data.loc[:,["ctotal_gift","cdur_gift"]].sum(axis=1)

data["ctotal_nogift"] = data.loc[:,["cfood_nogift","cnodur_nogift"]].sum(axis=1)
data["ctotal_dur_nogift"] = data.loc[:,["cfood_nogift","cnodur_nogift"]].sum(axis=1)

data["ctotal_own"] = data.loc[:,["cfood_own","cnodur_own"]].sum(axis=1)
data["ctotal_dur_own"] = data.loc[:,["ctotal_own","cdur_own"]].sum(axis=1)


cdata_short = data[["hh","ctotal","ctotal_dur","ctotal_gift","ctotal_dur_gift","ctotal_nogift","ctotal_dur_nogift","ctotal_own","ctotal_dur_own","cfood","cnodur","cdur"]]

sumc =cdata_short.describe()/dollars 

cdata_short.to_csv("ps1cons.csv", index=False)

########### Wealth
'''I constructed wealth from H.H questionary taking the value of assets, and from agricultural questionary taking
the living stock quantities and multiplying it by their prices, the prices were estimated
by the median of all the people that bough. I convert this prices to dolars. '''

#ASSET HOLDING OF H.H:
W = pd.read_csv("gsec14a.csv")
#W = W.merge(A, on="HHID", how="left") 
W = W[["HHID", "h14q5"]] #I take estimated value
W.columns = ["hh", "asset_value"] 
wealthasset = W.groupby(by = "hh")[["asset_value"]].sum()/dollars
wealthasset.reset_index(inplace=True)



#NOW WE COMPUTE LIFSTOCK WEALTH:
W = pd.read_csv("agsec6c.csv")


W = W[["hh","APCode", "a6cq3a", "a6cq13b", "a6cq14b"]]
W.columns = ["hh", "code","quantity", "pricebuy", "pricesell"]
prices =  W.groupby(by="code")[["pricebuy", "pricesell"]].median()/dollars
prices.reset_index(inplace=True)


#With prices of buying:
W = W.merge(prices, on="code", how="left")
W[['quantity','pricebuy_y']] = W[['quantity','pricebuy_y']].astype(float)
W['value'] = W['quantity']*W['pricebuy_y']
W['value'] = W['value'].fillna(0)
wealthlifestock =  W.groupby(by = "hh")[["value"]].sum()
wealthlifestock.reset_index(inplace=True)
#wealthlifestock.to_xlsx("wealthlifestock.csv", index=False)

Wealth = wealthasset.merge(wealthlifestock, on="hh", how="outer")
Wealth["value"] = Wealth["value"].fillna(0)
Wealth['Total'] = Wealth['value'] + Wealth['asset_value']
Wealth = Wealth[["hh","Total"]]
Wealth.reset_index(inplace=True)
Wealth = Wealth[['hh','Total']]
Wealth.columns = ['HHID', 'totalwealth']

Wealth.to_csv("ps1wealth.csv", index=False)


########## INCOME:
'''I find income wages from H.H taking pay in cash and kind, and other income, standarizing it by period of time
earned, and in dollar prices. '''

W = pd.read_stata("gsec8_1.dta")
W = W[["HHID","h8q31a","h8q31b", "h8q31c"]]
W.columns = ["HHID", "cash", "kind", "period"]
W['cash'] = W['cash'].fillna(0)
W['kind'] = W['kind'].fillna(0)
W['Total'] = W['cash'] + W['kind']
W['period'] = W['period'].replace(['Month', 'Week', 'Day', 'Other (specify)', 'Hour'], 
                     [12, 52, 365, 0, 2920])
W['final'] = W['Total']*W['period']
W['final'] = W['final'].fillna(0)
Incomewages = W.groupby(by="HHID")[["final"]].sum()
Incomewages.reset_index(inplace=True)
Incomewages.columns = ['HHID','Wages']

W  = pd.read_stata("gsec11b.dta")
W = W[["HHID","h11q5", "h11q5"]]
W.columns = ['HHID', 'cash', 'kind']
W['cash'] = W['cash'].fillna(0)
W['kind'] = W['kind'].fillna(0)
W['Total'] = W['cash'] + W['kind']
Incomebussiness = W.groupby(by="HHID")[["Total"]].sum()
Incomebussiness.reset_index(inplace=True)
Incomebussiness.columns = ['HHID','bussiness']


'''I find agricultural inputs cost, taking value of fertilizer, value of seed, value of pestizide
value of the work, to do so I compute household work on the farm, and the value of this wages 
with the median of the paid wages'''

W  = pd.read_stata("AGSEC3A.dta")
W = W[["hh","a3aq5","a3aq8","a3aq7", "a3aq15", "a3aq17", "a3aq18","a3aq24b",
       "a3aq26" , "a3aq27",]]
W.columns = ['HHID', 'orgfertquant', 'orgsellquant', 'orgfertval', 'inorgertquant',
             'inorgsellquant', 'inorgfertval', 'pestquant','pestsellquant', 'pestval',
             ]
W['orgfertval'] = W['orgfertval'].fillna(0)
W['orgsellquant'] = W['orgsellquant'].fillna(0)
W['inorgfertval'] = W['inorgfertval'].fillna(0)
W['inorgsellquant'] = W['inorgsellquant'].fillna(0)
W['pestval'] = W['pestval'].fillna(0)
W['pestquant'] = W['pestquant'].fillna(0)


W['priceorg'] = W['orgfertval']/W['orgsellquant']
#W['priceorg'] = W['priceorg'].fillna(0)
W['priceino'] = W['inorgfertval']/W['inorgsellquant']
#W['priceino'] = W['priceino'].fillna(0)
W['pricepest'] = W['pestval']/W['pestquant']
#W['pricepest'] = W['pricepest'].fillna(0)
priceorg = W['priceorg'].median()
pricepest = W['pricepest'].median()
priceino = W['priceino'].median()
W['org'] = W['orgfertquant']*priceorg
W['inorg'] = W['inorgertquant']*priceino
W['pest'] = W['pestquant']*pricepest

W['pest'] = W['pest'].fillna(0)
W['inorg'] = W['inorg'].fillna(0)
W['org'] = W['org'].fillna(0)
W['Totalcost'] = W['pest']+W['inorg']+W['org']

Costinputfarm = W.groupby(by="HHID")[["Totalcost"]].sum()
Costinputfarm.reset_index(inplace=True)

'''Now I compute the cost of the labour of the farm activity, to do so I compute
total hours of the household member and outsiders. Wages are computed from the part
is paid for outsiders.'''

W  = pd.read_stata("AGSEC3A.dta")
W = W[["hh", "a3aq33a_1", "a3aq33b_1", "a3aq33c_1", "a3aq33d_1", "a3aq33e_1",
       "a3aq35a", "a3aq35b", "a3aq35c","a3aq36"]]

W.columns = ['HHID','hours1','hours2','hours3','hours4','hours5', 'men', 
             'women', 'children', 'totalpaid']
W['hours1'] = W['hours1'].fillna(0)
W['hours2'] = W['hours2'].fillna(0)
W['hours3'] = W['hours3'].fillna(0)
W['hours4'] = W['hours4'].fillna(0)
W['hours5'] = W['hours5'].fillna(0)
W['men'] = W['men'].fillna(0)
W['women'] = W['women'].fillna(0)
W['children'] = W['children'].fillna(0)
W['Totalhousehold'] = W['hours1']+W['hours2']+W['hours3']+W['hours4']+W['hours5']
W['Totaloutsider'] = W['men']+W['women']+W['children']
W['totalpaid'] = W['totalpaid'].fillna(0)

W['paidperhour'] = W['totalpaid']/W['Totaloutsider'] 
W['Total'] = W['Totaloutsider']+W['Totalhousehold']
W['Total'] = W['Total'].fillna(0)
price = W['paidperhour'].median()
W['total'] = W['Total']*price
Costlabourfarm = W.groupby(by="HHID")[["total"]].sum()
Costlabourfarm.reset_index(inplace=True)
Total = Costlabourfarm.merge(Costinputfarm, on='HHID', how='outer') 
Total['Total'] = Total['total']+Total['Totalcost']
Total = Total[["HHID","Totalcost"]]
Total['Totalcost']=Total['Totalcost']


'''To find income of the farm I used value of the crop sold and the quantity sold,
 I use the median of the value per quantity to get the prices of evey cropt, 
 converted all the quantities into Kg. I use this prices to compute the total
 value of the production. 
 To convert everything Bunch has not been used since I did not know equivalence with
 Kg, Lts have been used but assuming density of 1 of the products inside the bins'''

W  = pd.read_stata("AGSEC5A.dta")
W = W[["hh","cropID","a5aq6a", "a5aq6b", "a5aq6c", "a5aq7a", "a5aq7c", "a5aq8"]]
W.columns = ['HHID',"cropID",'qty',"state","conversion", "Quantsold","Conversionsold", "Valuesold"]
#First I convert everything into Kg.
W['conversion'] = W['conversion'].replace(['Kilogram (KG)','Sack (120 kgs)','Sack (100 kgs)',
 'Sack (50 kgs)','Jerrican (20 lts)','Jerrican(10Lts)','Jerrican (5 lts)', 
 'Jerrican (3 lts)','Jerrican (2 lts)','Tin (20 lts)','Tin (5 lts)','Plastic Basin (15 lts)',
 'Kimbo/Cowboy/Blueband Tin (2 kg)','Kimbo/Cowboy/Blueband Tin (1 kg)','Kimbo/Cowboy/Blueband Tin (0.5 kg)',
 'Cup/Mug(0.5Lt)','	Basket (20 kg)','Basket (10 kg)','Basket (5 kg)','Basket (2 kg)',
 'Bunch (Big)','Bunch (Medium)','Bunch (Small)','Piece (Large)','Piece (Medium)', 
 'Heap (Large)','Heap (Medium)','Heap (Small)','Nomi Tin (1 kg)','Nomi Tin (0.5 kg)',
 'Nice cup (Medium)','Nice cup (Large)','Cluster (Small)','Cluster (Medium)','Cluster (Large)','Basket (20 kg)',
 'Piece (Small)'],
[1,120,100,50,20,10,5,3,2,20,5,15,2,1,0.5,0.5,20,10,5,2,0,0,0,0,0,0,0,0,1,0.5,0,0,0,0,0,20,0])

W['qty'] = W['qty']*W['conversion']
W['Quantsold'] = W['Quantsold']*W['conversion']

#First I will find prices:
prices = W[["HHID","cropID","Quantsold", "Valuesold"]]
prices['priceperquant'] = prices['Valuesold']/prices['Quantsold']
prices = prices.groupby(by="cropID")[["priceperquant"]].median()
prices.reset_index(inplace=True)


#I compute total value multiplying prices by quant
W = W.merge(prices, on="cropID", how = "left")

W['total value'] = W['qty']*W['priceperquant']
W['total value'] = W['total value'].fillna(0)
W['total value'] = W['total value'].replace([np.inf],[0])
W['Valuesold'] = W['Valuesold'].fillna(0)

A = W.loc[W["total value"].isin([0]),["HHID", "Valuesold"]]
A = A.groupby(by="HHID")[["Valuesold"]].sum()
A.reset_index(inplace=True)
W = W.groupby(by="HHID")[["total value"]].sum()
W.reset_index(inplace=True)
W = W.merge(A, on="HHID", how="outer")
W['Valuesold'] = W['Valuesold'].fillna(0)
W['total value'] = W['Valuesold']+W['total value']
Agriculturalincome = W[["HHID","total value"]]
Agriculturalincome = Agriculturalincome.merge(Total, on ="HHID", how="left")
Agriculturalincome['agincome'] = Agriculturalincome["total value"]-Agriculturalincome["Totalcost"]
Agriculturalincome = Agriculturalincome[['HHID', 'agincome']]
Incomeagri = Agriculturalincome
Totalincome = Agriculturalincome.merge(Incomebussiness, on="HHID", how="outer")
Totalincome = Totalincome.merge(Incomewages, on="HHID", how="outer")
Totalincome['totalincome'] = Totalincome['agincome']+Totalincome['bussiness']+Totalincome['Wages']
Totalincome['totalincome'] = Totalincome['totalincome']/dollars
Totalincome = Totalincome[["HHID", "totalincome"]]

###########FINAL DATA

Totalconsumption = cdata_short[['hh','ctotal']]
Totalconsumption['ctotal'] = Totalconsumption['ctotal']/dollars
Totalconsumption.columns = ['HHID', 'ctotal']
data = Totalincome.merge(Wealth, on="HHID", how="left")

data = data.merge(Totalconsumption, on="HHID", how="left")


age = pd.read_stata("GSEC2.dta")
age = age[['HHID','h2q8', 'h2q4']]
age = age.loc[age['h2q4'].isin(['Head']),['HHID','h2q8']]
age.columns = ['HHID', 'age']
data = data.merge(age, on="HHID", how="left")

rural = pd.read_stata("GSEC1.dta")
rural = rural[['HHID','urban']]
data = data.merge(rural, on="HHID", how="left")

#%% QUESTION 1:
data['inctotal'] = data['totalincome'].fillna(0)
urban = data.loc[data["urban"]=='Urban',["HHID","ctotal","totalwealth","totalincome"]]
urban.columns = ['hh','urban consumption','urban wealth', 'urban income']
urban['urban income'] = urban['urban income'].fillna(0)
rural = data.loc[data["urban"]=='Rural',["HHID","ctotal","totalwealth","totalincome"]]
rural.columns = ['hh','rural consumption','rural wealth', 'rural income']
rural['rural income'] = rural['rural income'].fillna(0)


curban = urban[["urban consumption"]]
curban = curban.dropna()
wurban = urban[["urban wealth"]]
iurban = urban[["urban income"]]
sum_urb=urban[["urban consumption","urban wealth", "urban income"]]
sum_urb=sum_urb.describe()
print(sum_urb.to_latex())


crural = rural[["rural consumption"]]
crural = crural.dropna()
wrural = rural[["rural wealth"]]
irural = rural[["rural income"]]
sum_rur=rural[["rural consumption","rural wealth", "rural income"]]
sum_rur=sum_rur.describe()
print(sum_rur.to_latex())



#%% QUESTION 1.2:INEQUALITY
#CIW combined in one histogram per area
#Convert to array
iu=np.asarray(iurban)
cu=np.asarray(curban)
wu=np.asarray(wurban)
cr=np.asarray(crural)
ir=np.asarray(irural)
wr=np.asarray(wrural)



#Hist
plt.figure
plt.subplots_adjust(top=0.9, bottom=0, left=0.3, right=1.5, wspace=0.5)
plt.suptitle('CIW Histograms')
bins=50 #Adjust the number of bins
bins2=75
plt.subplot(2,2,1)
plt.hist(cu, bins, alpha=0.5, label='Urban_C')
plt.hist(iu, bins, alpha=0.5, label='Urban_I')
#pyplot.hist(wu, bins, alpha=0.5, label='Wealth')
plt.xlim([-200,7000])
plt.legend(loc='upper right')

plt.subplot(2,2,2)
plt.hist(cu, bins, alpha=0.5, label='Urban_C')
plt.hist(wu, bins2, alpha=0.5, color='r', label='Urban_W')
plt.xlim([-200,10000])
#pyplot.hist(wu, bins, alpha=0.5, label='Wealth')
plt.legend(loc='upper right')

plt.subplot(2,2,3)
plt.hist(cr, bins, alpha=0.5,label='Rural_C')
plt.hist(ir, bins, alpha=0.5, label='Rural_I')
#pyplot.hist(wu, bins, alpha=0.5, label='Wealth')
plt.xlim([0,5000])
plt.legend(loc='upper right')

plt.subplot(2,2,4)
#plt.hist(cr, bins, alpha=0.5, label='Rural_C')
plt.hist(wr, bins2, alpha=0.5, color='r', label='Rural_W')
plt.hist(wu, bins2, alpha=0.5, color='b', label='urban_W')
#pyplot.hist(wu, bins, alpha=0.5, label='Wealth')
plt.xlim([-200,12000])
plt.legend(loc='upper right')
plt.show()


# VARIANCES:
###RURAL.
#Since logarithm of 0 is menus infinite, I convert these values to 0. Variance will be undervaluated.
lncrural = np.log(crural)
varcrural =  np.var(lncrural)
irural = irural.replace(0, 1)
lnirural = np.log(irural)
varirural =  np.var(lnirural)
wrural = wrural.replace(0, 1)
lnwrural = np.log(wrural)
varwrural =  np.var(lnwrural)

### Urban.
lncurban = np.log(curban)
varcurban = np.var(lncurban)
iurban = iurban.replace(0, 1)
lniurban = np.log(iurban)
iurban = lniurban.fillna(0)
variurban = np.var(lniurban)
wurban = wurban.replace(0, 1)
lnwurban = np.log(wurban)
wurban = lniurban.fillna(0)
varwurban = np.var(lnwurban)



#%% QUESTION 1.3: CROSS-SECTION
#I remove 0 consumption people:
urban = urban.dropna()
rural = rural.dropna()

#1- Correlations Matrix (CM)
CIW_R=rural[["rural consumption","rural wealth", "rural income"]]
CM_R= CIW_R.corr()
print(CM_R.to_latex())

CIW_U=urban[["urban consumption","urban wealth", "urban income"]]
CM_U= CIW_U.corr()
print(CM_U.to_latex())

#2.- Joint density graphs
with sns.axes_style('white'):
    sns.jointplot("rural income", "rural consumption", rural, kind='kde', xlim=(-500,4000),ylim=(0,4000));

with sns.axes_style('white'):
    sns.jointplot("rural income", "rural wealth", rural, kind='kde',xlim=(-1000,2000),ylim=(-1000,4000));

with sns.axes_style('white'):
    sns.jointplot("urban income", "urban consumption", urban, kind='kde',xlim=(-600,1500),ylim=(-1000,8000));

with sns.axes_style('white'):
    sns.jointplot("urban income", "urban wealth", urban, kind='kde',xlim=(-600,6000),ylim=(-1000,18000));
    

    
#%%QUESTION 1.4: LIFECYCLE CIW:
# Uganda
A = data.groupby(by = "age")[["ctotal","totalwealth","totalincome"]].mean()
A['age'] = A.index

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Age')
ax1.set_ylabel('CI', color=color)
ax1.plot(A['age'],A[['ctotal']] , color='g',label='consumption')
ax1.plot(A['age'],A[['totalincome']] , color=color,label='income')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Wealth', color=color)  # we already handled the x-label with ax1
ax2.plot(A['age'],A[['totalwealth']] , color=color, label='wealth')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
fig.legend(loc='best')
plt.title('Life cycle intensive and extensive')
plt.show()

#Urban
Urban_data=data.loc[data["urban"]=='Urban',["ctotal","totalwealth","totalincome","age"]]
A = Urban_data.groupby(by = "age")[["ctotal","totalwealth","totalincome"]].mean()
A['age'] = A.index

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Age')
ax1.set_ylabel('CI', color=color)
ax1.plot(A['age'],A[['ctotal']] , color='g',label='consumption')
ax1.plot(A['age'],A[['totalincome']] , color=color,label='income')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Wealth', color=color)  # we already handled the x-label with ax1
ax2.plot(A['age'],A[['totalwealth']] , color=color, label='wealth')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
fig.legend(loc='best')
plt.title('Urban CIW life-cycle profile')
plt.show()


#Rural
Rural_data=data.loc[data["urban"]=='Rural',["ctotal","totalwealth","totalincome","age"]]
A = Rural_data.groupby(by = "age")[["ctotal","totalwealth","totalincome","age"]].mean()
A['age'] = A.index

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Age')
ax1.set_ylabel('CI', color=color)
ax1.plot(A['age'],A[['ctotal']] , color='g',label='consumption')
ax1.plot(A['age'],A[['totalincome']] , color=color,label='income')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Wealth', color=color)  # we already handled the x-label with ax1
ax2.plot(A['age'],A[['totalwealth']] , color=color, label='wealth')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
fig.legend(loc='best')
plt.title('Rural CIW life-cycle profile')
plt.show()


#%%1.5 EXTREME BEHAVIOUR
#Rank by income percentile
data['inctotal'] = data["totalincome"].replace(0,float('NaN'))
data['I_Percentile_rank']=data.inctotal.rank(pct=True)

#Get the consumption/wealth share of the income top and bottom 10%. 
#Consumption
C_bottom=data.loc[data["I_Percentile_rank"]<0.1,["ctotal"]]
C_bottom_10share=C_bottom.sum()/data["ctotal"].sum()
C_top=data.loc[data["I_Percentile_rank"]>0.9,["ctotal"]]
C_top_10share=C_top.sum()/data["ctotal"].sum()
#The bottom 10% consumes only about 6% and the top 10% about 12%. 

#Wealth
W_bottom=data.loc[data["I_Percentile_rank"]<0.1,["totalwealth"]]
W_bottom_10share=W_bottom.sum()/data["totalwealth"].sum()
W_top=data.loc[data["I_Percentile_rank"]>0.9,["totalwealth"]]
W_top_10share=W_top.sum()/data["totalwealth"].sum()

#%%QUESTION 2 DATA
data2 = pd.read_stata("gsec1.dta")
dataurban = data2[["HHID","urban"]]
dataurban = dataurban.replace(['Urban', 'Rural'], 
                     [1, 0])

'''in Gender, 1 if women, 0 if men '''
data2 = pd.read_stata("gsec2.dta")
dataage = data2[["HHID","h2q8", "h2q3"]]
dataage.columns = [["HHID","Age1", "Gender"]]
dataage = dataage.replace(['Female', 'Male'], 
                     [1, 0])
dataage.columns = ['HHID','Age1', 'Gender']

age = pd.read_stata("GSEC2.dta")
age = age[['HHID','h2q8', 'h2q4']]
age = age.loc[age['h2q4'].isin(['Head']),['HHID','h2q8']]
age.columns = ['HHID', 'age']
dataage = dataage.merge(age, on='HHID', how='left')
dataage = dataage[['HHID', 'age', 'Gender']]
data2 = dataage.merge(dataurban, on="HHID", how="left")


'''Less than primary is 0, primary is 1, and more or equal than secundary is 2 .
Don't know is understood as less than primary.'''
school = pd.read_stata("gsec3.dta")
school = school[["HHID","h3q3"]].dropna()
school.columns = ["HHID","school"]
school = school.replace(['No formal education (*OLD*)', 'Less than primary (*OLD*)', 
                           'Some schooling but not Completed P.1','DK','Completed P.1','Completed P.2'
                           ,'Completed P.3', 'Completed P.4', 'Completed P.5', 'Completed P.6','Completed P.7'
                           ,'Completed J.1', 'Completed J.2', 'Completed J.3', '	Completed primary (*OLD*)'
                           ,'Completed S.1', 'Completed S.2', 'Completed S.3', 'Completed S.4'
                           ,'Completed S.5', 'Completed S.6', 'Completed Post primary Specialized training or Certificate'
                           ,'Completed Post secondary Specialized training or diploma', 'Completed Degree and above'
                           , 'Some secondary', 'Some primary', 'Never attended school', 'Completed O-level (*OLD*)'
                           ,'Completed A-level (*OLD*)', 'Completed University (*OLD*)', 'Don\'t know (*OLD*)', 'Completed primary (*OLD*)', '	Other (Specify) (*OLD*)'], 
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 2, 2, 2, 0, 1, 0])

data1 = data2.merge(school, on="HHID", how="left")

'''METHOD: I took for intensive labour hours worked the whole week and 
I add iit '''
age.columns = ['hh','age']

data2 = pd.read_stata("gsec8_1.dta")
data2 = data2.merge(data1, on="HHID", how="left") 
data2 = data2[["HHID","h8q5","h8q7","h8q9","h8q13", "urban","age"]]
data2.columns = ["hh", "paid", "busines", "non-paid", "farm", "urban", "age"]
data2 = data2.replace(['No', 'Yes', 'nan'], 
                     [0, 1, float('NaN')]).dropna()
#data2 = data2.merge(age, on="HHID", how="left")
dataurban = data2.loc[data2["urban"].isin([1]),["hh", "paid", "busines", "non-paid", "farm","age"]]
datarural = data2.loc[data2["urban"].isin([0]),["hh", "paid", "busines", "non-paid", "farm", "age"]]


dataurban = dataurban.groupby(by = "hh")[["paid", "busines", "non-paid", "farm"]].sum()
dataurban.reset_index(inplace=True)
dataurban = dataurban.merge(age, on='hh', how='left')
extensivelaboururban = dataurban[['hh',"paid", "busines", "non-paid", "farm", "age"]]
extensivelaboururban['totalextensiveurban']= extensivelaboururban["paid"]+extensivelaboururban["busines"]+extensivelaboururban["non-paid"]+extensivelaboururban["farm"]
extensivelaboururban.columns = ['HHID',"paid", "busines", "non-paid", "farm","age", "totalextensiveurban"]

extensivelaboururban = extensivelaboururban[['HHID','totalextensiveurban', 'age']]

datarural = datarural.groupby(by = "hh")[["paid", "busines", "non-paid", "farm"]].sum()
datarural.reset_index(inplace=True)
datarural = datarural.merge(age, on='hh', how='left')
extensivelabourrural = datarural[['hh',"paid", "busines", "non-paid", "farm", "age"]]
extensivelabourrural['totalextensiverural'] = extensivelabourrural["paid"]+extensivelabourrural["busines"]+extensivelabourrural["non-paid"]+extensivelabourrural['farm']
extensivelabourrural.columns = ["HHID","paid", "busines", "non-paid", "farm", "age","totalextensiverural"]
extensivelabourrural = extensivelabourrural[['HHID','totalextensiverural', 'age']]
#extensivelabourrural = extensivelabourrural['totalextensiverural']


#MAKING INTENSIVE
age.columns = ['HHID', 'age']
data = pd.read_stata("gsec8_1.dta")
data = data.merge(data1, on="HHID", how="left") 
data = data[["HHID","h8q36a","h8q36b","h8q36c","h8q36d","h8q36e","h8q36f","h8q36g", "urban"]].dropna()
dataurban = data.loc[data["urban"].isin([1]),["HHID","h8q36a","h8q36b","h8q36c","h8q36d","h8q36e","h8q36f","h8q36g"]]
datarural = data.loc[data["urban"].isin([0]),["HHID","h8q36a","h8q36b","h8q36c","h8q36d","h8q36e","h8q36f","h8q36g"]]

dataurban = dataurban.groupby(by = "HHID")[["h8q36a","h8q36b","h8q36c","h8q36d","h8q36e","h8q36f","h8q36g"]].sum()
datarural = datarural.groupby(by = "HHID")[["h8q36a","h8q36b","h8q36c","h8q36d","h8q36e","h8q36f","h8q36g"]].sum()
dataurban.reset_index(inplace=True)
datarural.reset_index(inplace=True)
datarural = datarural.merge(age, on='HHID', how='left')
dataurban = dataurban.merge(age, on='HHID', how='left')

intensivelaboururban = dataurban[['HHID']]
intensivelabourrural = datarural[['HHID']]
intensivelaboururban['totalinturban'] = dataurban['h8q36a']+dataurban['h8q36b']+dataurban['h8q36c']+dataurban['h8q36d']+dataurban['h8q36e']+dataurban['h8q36f']+dataurban['h8q36g']
intensivelabourrural['totalintrural'] = datarural['h8q36a']+datarural['h8q36b']+datarural['h8q36c']+datarural['h8q36d']+datarural['h8q36e']+datarural['h8q36f']+datarural['h8q36g']


#intensivelaboururban = dataurban.sum(axis=1)
#intensivelabourrural = datarural.sum(axis=1)
rural = intensivelabourrural.merge(extensivelabourrural,on="HHID", how="outer")

urban = intensivelaboururban.merge(extensivelaboururban,on="HHID", how="outer")


#%% QUESTION 2.1.1:

Iurban = intensivelaboururban[["totalinturban"]]
Irural = intensivelabourrural[["totalintrural"]]
Erural = extensivelabourrural[["totalextensiverural"]]
Eurban = extensivelaboururban[["totalextensiveurban"]]

sum_extensivelaboururban = Eurban.describe()
sum_extensivelabourrural = Erural.describe()
sum_intensivelaboururban = Iurban.describe()
sum_intensivelabourrural = Irural.describe()
print(sum_extensivelaboururban.to_latex())
print(sum_extensivelabourrural.to_latex())
print(sum_intensivelaboururban.to_latex())
print(sum_intensivelabourrural.to_latex())

#%% Question 2.1.2:
iu=np.asarray(Iurban)
ir=np.asarray(Irural)
eu=np.asarray(Eurban)
Er=np.asarray(Erural)

#Hist
plt.figure
plt.subplots_adjust(top=0.9, bottom=0, left=0.3, right=1.5, wspace=0.5)
plt.suptitle('Extensive and Intensive Histograms')
bins=50 #Adjust the number of bins
bins2=75
plt.subplot(1,2,1)
plt.hist(ir, bins, alpha=0.5, label='Rural_I')
plt.hist(iu, bins, alpha=0.5, label='Urban_I')
#pyplot.hist(wu, bins, alpha=0.5, label='Wealth')
plt.xlim([0,10000])
plt.legend(loc='upper right')

plt.subplot(1,2,2)
plt.hist(eu, bins, alpha=0.5, label='Urban_E')
plt.hist(Er, bins2, alpha=0.5, color='r', label='Rural_E')
plt.xlim([0,200])
#pyplot.hist(wu, bins, alpha=0.5, label='Wealth')
plt.legend(loc='upper right')
plt.show()

Iurban = Iurban.replace(0, 1)
lnIurban = np.log(Iurban)
varIurban=  np.var(lnIurban)
Eurban = Eurban.replace(0, 1)
lnEurban = np.log(Eurban)
varEurban=  np.var(lnEurban)
Irural = Irural.replace(0, 1)
lnIrural = np.log(Irural) 
varIrural =  np.var(lnIrural)
Erural = Erural.replace(0, 1)
lnErural = np.log(Erural) 
varErural =  np.var(lnErural)


#%% Question 2.1.3: CROSS-SECTION:
#I remove 0 consumption people:
#urban = urban.groupby(by='HHID')[["totalinturban", "totalextensiveurban"]].sum()
#urban = urban.dropna()
#rural = rural.dropna()

#1- Correlations Matrix (CM)
CIW_R=rural[["totalintrural","totalextensiverural"]]
CM_R= CIW_R.corr()
print(CM_R.to_latex())

CIW_U=urban[["totalinturban","totalextensiveurban"]]
CM_U= CIW_U.corr()
print(CM_U.to_latex())

rural['totalintrural'] = rural['totalintrural'].fillna(0)

#2.- Joint density graphs
with sns.axes_style('white'):
    sns.jointplot("totalintrural", "totalextensiverural", rural, kind='kde', xlim=(-600,2000),ylim=(0,200));

with sns.axes_style('white'):
    sns.jointplot("totalinturban", "totalextensiveurban", urban, kind='kde',xlim=(-600,2000),ylim=(0,150));






    

#%%3. REGIONAL INEQUALITY
#3.1. CWL agains income
import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as sm
os.chdir('C:/Users/Joana/Desktop/Cole/18-19/2.Development/ps1/data')

from statsmodels.iolib.summary2 import summary_col
pd.options.display.float_format = '{:,.2f}'.format
import seaborn as sns
sns.set()
import matplotlib.pyplot as plt
dollars = 2586.89 

data = pd.read_stata("Uganda.dta")
data.columns = ['HHID','hh_laboursupply_year_2013', 'region', 'urban','Total', 'hh_consu_year_2013', 'hh_ttincome_2013' ]
#Region 1
central = data.loc[data["region"]==1,["HHID","hh_consu_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]


#plt.figure()
#plt.subplots_adjust(top=0.9, bottom=0.1, left=0.3, right=1.5, wspace=0.5)
#plt.suptitle('CWL Central Region')
#plt.subplot(131)
#plt.scatter(central["hh_ttincome_2013"], central["hh_consumption_year_2013"])
#plt.xlabel('Income')
#plt.ylabel('Consumption')
#
#plt.subplot(132)
#plt.scatter(central["hh_ttincome_2013"],central['Total'])
#plt.xlabel('Income')
#plt.ylabel('Wealth')
#
#plt.subplot(133)
#plt.scatter(central["hh_ttincome_2013"],central["hh_laboursupply_year_2013"])
#plt.xlabel('Income')
#plt.ylabel('Hours')
#plt.show()



#Region 2
Eastern = data.loc[data["region"]==2,["HHID","hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]

plt.figure()
plt.subplots_adjust(top=0.9, bottom=0.1, left=0.3, right=1.5, wspace=0.5)
plt.suptitle('CWL Eastern Region')
plt.subplot(131)
plt.scatter(Eastern["hh_ttincome_2013"], Eastern["hh_consumption_year_2013"])
plt.xlabel('Income')
plt.ylabel('Consumption')

plt.subplot(132)
plt.scatter(Eastern["hh_ttincome_2013"],Eastern['Total'])
plt.xlabel('Income')
plt.ylabel('Wealth')

plt.subplot(133)
plt.scatter(Eastern["hh_ttincome_2013"],Eastern["hh_laboursupply_year_2013"])
plt.xlabel('Income')
plt.ylabel('Hours')
plt.show()



#Region 3
Northern = data.loc[data["region"]==3,["HHID","hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]

plt.figure()
plt.subplots_adjust(top=0.9, bottom=0.1, left=0.3, right=1.5, wspace=0.5)
plt.suptitle('CWL Northern Region')
plt.subplot(131)
plt.scatter(Northern["hh_ttincome_2013"],Northern["hh_consumption_year_2013"])
plt.xlabel('Income')
plt.ylabel('Consumption')

plt.subplot(132)
plt.scatter(Northern["hh_ttincome_2013"],Northern['Total'])
plt.xlabel('Income')
plt.ylabel('Wealth')

plt.subplot(133)
plt.scatter(Northern["hh_ttincome_2013"],Northern["hh_laboursupply_year_2013"])
plt.xlabel('Income')
plt.ylabel('Hours')
plt.show()

#Region 4 
Western = data.loc[data["region"]==4,["HHID","hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]

plt.figure()
plt.subplots_adjust(top=0.9, bottom=0.1, left=0.3, right=1.5, wspace=0.5)
plt.suptitle('CWL Western Region')
plt.subplot(131)
plt.scatter(Western["hh_ttincome_2013"],Western["hh_consumption_year_2013"])
plt.xlabel('Income')
plt.ylabel('Consumption')

plt.subplot(132)
plt.scatter(Western["hh_ttincome_2013"],Western['Total'])
plt.xlabel('Income')
plt.ylabel('Wealth')

plt.subplot(133)
plt.scatter(Western["hh_ttincome_2013"],Western["hh_laboursupply_year_2013"])
plt.xlabel('Income')
plt.ylabel('Hours')
plt.show()





#3.2.INEQUALITY
i1=np.asarray(central["hh_ttincome_2013"])
i2=np.asarray(Eastern["hh_ttincome_2013"])
i3=np.asarray(Northern["hh_ttincome_2013"])
i4=np.asarray(Western["hh_ttincome_2013"])
c1=np.asarray(central["hh_consumption_year_2013"])
c2=np.asarray(Eastern["hh_consumption_year_2013"])
c3=np.asarray(Northern["hh_consumption_year_2013"])
c4=np.asarray(Western["hh_consumption_year_2013"])
w1=np.asarray(central["Total"])
w2=np.asarray(Eastern["Total"])
w3=np.asarray(Northern["Total"])
w4=np.asarray(Western["Total"])
h1=np.asarray(central["hh_laboursupply_year_2013"])
h2=np.asarray(Eastern["hh_laboursupply_year_2013"])
h3=np.asarray(Northern["hh_laboursupply_year_2013"])
h4=np.asarray(Western["hh_laboursupply_year_2013"])



plt.figure
plt.subplots_adjust(top=0.9, bottom=0, left=0.3, right=1.5, wspace=0.5)
plt.suptitle('CIWL Histograms')
bins=25 #Adjust the number of bins

plt.subplot(2,2,1)
plt.hist(i1, bins, alpha=0.5, label='inc_c')
plt.hist(i2, bins, alpha=0.5, label='inc_e')
plt.hist(i3, bins, alpha=0.5, label='inc_n')
plt.hist(i4, bins, alpha=0.5, label='inc_w')
plt.legend(loc='upper right')

plt.subplot(2,2,2)
plt.hist(c1, bins, alpha=0.5, label='con_c')
plt.hist(c2, bins, alpha=0.5, label='con_e')
plt.hist(c3, bins, alpha=0.5, label='con_n')
plt.hist(c4, bins, alpha=0.5, label='con_w')
plt.legend(loc='upper right')

plt.subplot(2,2,3)
plt.hist(w1, bins, alpha=0.5, label='w_c')
plt.hist(w2, bins, alpha=0.5, label='w_e')
plt.hist(w3, bins, alpha=0.5, label='w_n')
plt.hist(w4, bins, alpha=0.5, label='w_w')
plt.legend(loc='upper right')

plt.subplot(2,2,4)
plt.hist(h1, bins, alpha=0.5, label='h_c')
plt.hist(h2, bins, alpha=0.5, label='h_e')
plt.hist(h3, bins, alpha=0.5, label='h_n')
plt.hist(h4, bins, alpha=0.5, label='h_w')
plt.legend(loc='upper right')
plt.show()


#3.3. JOINT DISTRIBUTION

CIWL_c=central[["hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]
CM_c= CIWL_c.corr()
print(CM_c.to_latex())

CIW_e=Eastern[["hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]
CM_U= CIW_e.corr()
print(CM_U.to_latex())

CIW_n=Northern[["hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]
CM_U= CIW_n.corr()
print(CM_U.to_latex())

CIW_w=Western[["hh_consumption_year_2013","Total","hh_ttincome_2013","hh_laboursupply_year_2013"]]
CM_U= CIW_w.corr()
print(CM_U.to_latex())
