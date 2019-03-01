#%% PS3 Development BY Boyao, Joan and Pau
import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as sm
from numpy.linalg import inv
import matplotlib.pyplot as plt

#%% Question 1:
'''Idea of this estimation. First I will create new groups of families, I will make the groups
by creating an arbitrary value that is an estimation of the identity of the household.
This arbitrary indentity is computed by introducing family size and total income of the family
into a cobb-douglas function, with a parameter teta that set the importance that have these two features
to the identity. With this grouping structure we will be able to create artifically more 
degrees of freedom, we will try different values of teta to see if the distribution of betas
changes a lot. Data is from Albert dataUGA, we delete observations without income, family numbers, or consumption.'''

teta = 0.5

data = pd.read_stata("dataUGA.dta")
data = data[['hh','ctotal','familysize','inctotal','wave']]
data['lnc'] = np.log(data['ctotal'])
data['lnN'] = np.log(data['familysize'])
data['lni'] = np.log(data['inctotal'])
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna()
totalconsumption = data[['wave', 'ctotal']]
totalconsumption = data.groupby(by='wave')[['ctotal']].sum()
totalconsumption['wave'] = totalconsumption.index
totalconsumption.columns = ['total', 'wave']
totalconsumption['total'] = np.log(totalconsumption['total'])


'''Creating groups of families. '''
groups = data.groupby(by = "hh")[["familysize","inctotal"]].mean()
groups['hh'] = groups.index
groups['value'] = pow(groups['familysize'],teta)*pow(groups['inctotal'],1-teta)
groups = groups[['hh','value']]
groups = groups.sort_values(['value'], ascending=[1])
N = len(groups)
d = np.array([[i, i, i, i] for i in range(round(N/4))]).reshape(N-1,1)
d = np.append(0,d)
groups['group'] = d
groups = groups[['hh','group']]
data = data.sort_values(['hh', 'wave'], ascending=[1,1])

''' This data is the data with the groups. '''
data = data.merge(groups, on="hh", how="left")

data = data.merge(totalconsumption, on ='wave', how='left')

data2009 = data.loc[data['wave']=='2009-2010',['hh','lnc','lnN', 'lni','total']]
data2009.columns = ['hh', 'lnc2009', 'lnN2009', 'lni2009', 'total2009']
data2010 = data.loc[data['wave']=='2010-2011',['hh','lnc','lnN', 'lni','total']]
data2010.columns = ['hh', 'lnc2010', 'lnN2010', 'lni2010', 'total2010']
data2011 = data.loc[data['wave']=='2011-2012',['hh','lnc','lnN', 'lni', 'total']]
data2011.columns = ['hh', 'lnc2011', 'lnN2011', 'lni2011', 'total2011']
data2013 = data.loc[data['wave']=='2013-2014',['hh','lnc','lnN', 'lni', 'total']]
data2013.columns = ['hh', 'lnc2013', 'lnN2013', 'lni2013', 'total2013']

data2010 = data2009.merge(data2010, on='hh', how='outer')
data2010['Con2010'] = data2010['lnc2010']-data2010['lnc2009']
data2010['N2010'] = data2010['lnN2010']-data2010['lnN2009']
data2010['I2010'] = data2010['lni2010']-data2010['lni2009']
data2010['Total2010'] = data2010['total2010']-data2010['total2009']
data2010 = data2010.merge(data2011, on='hh', how='outer')
data2010['Con2011'] = data2010['lnc2011']-data2010['lnc2010']
data2010['N2011'] = data2010['lnN2011']-data2010['lnN2010']
data2010['I2011'] = data2010['lni2011']-data2010['lni2010']
data2010['Total2011'] = data2010['total2011']-data2010['total2010']
data2010 = data2010.merge(data2013, on='hh', how='outer')
data2010['Con2013'] = data2010['lnc2013']-data2010['lnc2011']
data2010['N2013'] = data2010['lnN2013']-data2010['lnN2011']
data2010['I2013'] = data2010['lni2013']-data2010['lni2011']
data2010['Total2013'] = data2010['total2013']-data2010['total2011']

data2010 = data2010[['hh','Con2010','N2010','I2010','Total2010','Con2011','N2011','I2011','Total2011','Con2013','N2013','I2013','Total2013']]
data10 = data2010[['hh','Con2010','N2010','I2010','Total2010']]
data11 = data2010[['hh','Con2011','N2011','I2011','Total2011']]
data13 = data2010[['hh','Con2013','N2013','I2013','Total2013']]

data1 = np.concatenate((data10,data11), axis = 0)
data1 = np.concatenate((data1,data13), axis = 0)
data1 = pd.DataFrame(data1, columns = ['hh', 'Con', 'N', 'Inc', 'Aggregate'])
data1 = data1.merge(groups, on='hh', how='left').dropna()
data1 = data1[['Con', 'N', 'Inc', 'Aggregate', 'group']]
l = len(data1)
data1['constant'] = np.ones(l)
data1 = data1.reindex()

'''We have the data ready to be used in the regression. We make a loop for make
a regression for every group of family. We are not using groups that have less than 4 observations
we also need to separate groups for which there is no variance on size of family, an the
ones that have variance.'''
count = 0
betasfull = pd.DataFrame([],index=['constant','N','Inc', 'Aggregate'], columns=[1])
betas = pd.DataFrame([],index=['constant','Inc', 'Aggregate'], columns=[1])
for i in range(round(N/4)):
    if any(i==data1['group']) is True:
        family1 = data1.loc[data1['group']==i,['constant','Con', 'N', 'Inc', 'Aggregate']]
        if len(family1['Con'])>3:
            
            X = np.matrix(np.array(family1[['constant','N','Inc', 'Aggregate']]))
            
            if np.linalg.det(X.T@X)==0:
                 X = np.matrix(np.array(family1[['constant','Inc', 'Aggregate']]))
                 Y = np.matrix(np.array(family1[['Con']]))
                 b = inv(X.T*X)*(X.T@Y)
                 betas[i] = b
            else:                
                Y = np.matrix(np.array(family1[['Con']]))
                b = inv(X.T*X)*(X.T@Y)
                betasfull[i] = b
   
    count = count+1
   
betasfull = betasfull.T.dropna()
beta = betasfull['Inc']
ax = beta.plot.hist(bins=110, alpha=0.5)

#%% Rural and urban:

'''Urban '''
teta = 0.5

data = pd.read_stata("dataUGA.dta")
data = data[['hh','ctotal','familysize','inctotal','wave','urban']]
data = data.loc[data['urban']==1,['hh','ctotal','familysize','inctotal','wave']]
data['lnc'] = np.log(data['ctotal'])
data['lnN'] = np.log(data['familysize'])
data['lni'] = np.log(data['inctotal'])
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna()
totalconsumption = data[['wave', 'ctotal']]
totalconsumption = data.groupby(by='wave')[['ctotal']].sum()
totalconsumption['wave'] = totalconsumption.index
totalconsumption.columns = ['total', 'wave']
totalconsumption['total'] = np.log(totalconsumption['total'])


'''Creating groups of families. '''
groups = data.groupby(by = "hh")[["familysize","inctotal"]].mean()
groups['hh'] = groups.index
groups['value'] = pow(groups['familysize'],teta)*pow(groups['inctotal'],1-teta)
groups = groups[['hh','value']]
groups = groups.sort_values(['value'], ascending=[1])
N = len(groups)
d = np.array([[i, i, i, i] for i in range(round(N/4))]).reshape(936,1)
d = d[0:934]
groups['group'] = d
groups = groups[['hh','group']]
data = data.sort_values(['hh', 'wave'], ascending=[1,1])

''' This data is the data with the groups. '''
data = data.merge(groups, on="hh", how="left")

data = data.merge(totalconsumption, on ='wave', how='left')

data2009 = data.loc[data['wave']=='2009-2010',['hh','lnc','lnN', 'lni','total']]
data2009.columns = ['hh', 'lnc2009', 'lnN2009', 'lni2009', 'total2009']
data2010 = data.loc[data['wave']=='2010-2011',['hh','lnc','lnN', 'lni','total']]
data2010.columns = ['hh', 'lnc2010', 'lnN2010', 'lni2010', 'total2010']
data2011 = data.loc[data['wave']=='2011-2012',['hh','lnc','lnN', 'lni', 'total']]
data2011.columns = ['hh', 'lnc2011', 'lnN2011', 'lni2011', 'total2011']
data2013 = data.loc[data['wave']=='2013-2014',['hh','lnc','lnN', 'lni', 'total']]
data2013.columns = ['hh', 'lnc2013', 'lnN2013', 'lni2013', 'total2013']

data2010 = data2009.merge(data2010, on='hh', how='outer')
data2010['Con2010'] = data2010['lnc2010']-data2010['lnc2009']
data2010['N2010'] = data2010['lnN2010']-data2010['lnN2009']
data2010['I2010'] = data2010['lni2010']-data2010['lni2009']
data2010['Total2010'] = data2010['total2010']-data2010['total2009']
data2010 = data2010.merge(data2011, on='hh', how='outer')
data2010['Con2011'] = data2010['lnc2011']-data2010['lnc2010']
data2010['N2011'] = data2010['lnN2011']-data2010['lnN2010']
data2010['I2011'] = data2010['lni2011']-data2010['lni2010']
data2010['Total2011'] = data2010['total2011']-data2010['total2010']
data2010 = data2010.merge(data2013, on='hh', how='outer')
data2010['Con2013'] = data2010['lnc2013']-data2010['lnc2011']
data2010['N2013'] = data2010['lnN2013']-data2010['lnN2011']
data2010['I2013'] = data2010['lni2013']-data2010['lni2011']
data2010['Total2013'] = data2010['total2013']-data2010['total2011']

data2010 = data2010[['hh','Con2010','N2010','I2010','Total2010','Con2011','N2011','I2011','Total2011','Con2013','N2013','I2013','Total2013']]
data10 = data2010[['hh','Con2010','N2010','I2010','Total2010']]
data11 = data2010[['hh','Con2011','N2011','I2011','Total2011']]
data13 = data2010[['hh','Con2013','N2013','I2013','Total2013']]

data1 = np.concatenate((data10,data11), axis = 0)
data1 = np.concatenate((data1,data13), axis = 0)
data1 = pd.DataFrame(data1, columns = ['hh', 'Con', 'N', 'Inc', 'Aggregate'])
data1 = data1.merge(groups, on='hh', how='left').dropna()
data1 = data1[['Con', 'N', 'Inc', 'Aggregate', 'group']]
l = len(data1)
data1['constant'] = np.ones(l)
data1 = data1.reindex()

'''We have the data ready to be used in the regression. We make a loop for make
a regression for every group of family. We are not using groups that have less than 4 observations
we also need to separate groups for which there is no variance on size of family, an the
ones that have variance.'''
count = 0
betasfull = pd.DataFrame([],index=['constant','N','Inc', 'Aggregate'], columns=[1])
betas = pd.DataFrame([],index=['constant','Inc', 'Aggregate'], columns=[1])
for i in range(round(N/4)):
    if any(i==data1['group']) is True:
        family1 = data1.loc[data1['group']==i,['constant','Con', 'N', 'Inc', 'Aggregate']]
        if len(family1['Con'])>3:
            
            X = np.matrix(np.array(family1[['constant','N','Inc', 'Aggregate']]))
            
            if np.linalg.det(X.T@X)==0:
                 X = np.matrix(np.array(family1[['constant','Inc', 'Aggregate']]))
                 Y = np.matrix(np.array(family1[['Con']]))
                 b = inv(X.T*X)*(X.T@Y)
                 betas[i] = b
            else:                
                Y = np.matrix(np.array(family1[['Con']]))
                b = inv(X.T*X)*(X.T@Y)
                betasfull[i] = b
   
    count = count+1
   
betasfull = betasfull.T.dropna()
betasfull = betasfull.sort_values(['Inc'], ascending=[1])
betaurban = betasfull['Inc'][0:144]

ax = beta.plot.hist(bins=110, alpha=0.5, label='Urban')

                
'''Rural '''
teta = 0.5

data = pd.read_stata("dataUGA.dta")
data = data[['hh','ctotal','familysize','inctotal','wave','urban']]
data = data.loc[data['urban']==0,['hh','ctotal','familysize','inctotal','wave']]
data['lnc'] = np.log(data['ctotal'])
data['lnN'] = np.log(data['familysize'])
data['lni'] = np.log(data['inctotal'])
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna()
totalconsumption = data[['wave', 'ctotal']]
totalconsumption = data.groupby(by='wave')[['ctotal']].sum()
totalconsumption['wave'] = totalconsumption.index
totalconsumption.columns = ['total', 'wave']
totalconsumption['total'] = np.log(totalconsumption['total'])


'''Creating groups of families. '''
groups = data.groupby(by = "hh")[["familysize","inctotal"]].mean()
groups['hh'] = groups.index
groups['value'] = pow(groups['familysize'],teta)*pow(groups['inctotal'],1-teta)
groups = groups[['hh','value']]
groups = groups.sort_values(['value'], ascending=[1])
N = len(groups)
d = np.array([[i, i, i, i] for i in range(round(N/4))]).reshape(2528,1)
d = np.append(np.zeros(2),d)
groups['group'] = d
groups = groups[['hh','group']]
data = data.sort_values(['hh', 'wave'], ascending=[1,1])

''' This data is the data with the groups. '''
data = data.merge(groups, on="hh", how="left")

data = data.merge(totalconsumption, on ='wave', how='left')

data2009 = data.loc[data['wave']=='2009-2010',['hh','lnc','lnN', 'lni','total']]
data2009.columns = ['hh', 'lnc2009', 'lnN2009', 'lni2009', 'total2009']
data2010 = data.loc[data['wave']=='2010-2011',['hh','lnc','lnN', 'lni','total']]
data2010.columns = ['hh', 'lnc2010', 'lnN2010', 'lni2010', 'total2010']
data2011 = data.loc[data['wave']=='2011-2012',['hh','lnc','lnN', 'lni', 'total']]
data2011.columns = ['hh', 'lnc2011', 'lnN2011', 'lni2011', 'total2011']
data2013 = data.loc[data['wave']=='2013-2014',['hh','lnc','lnN', 'lni', 'total']]
data2013.columns = ['hh', 'lnc2013', 'lnN2013', 'lni2013', 'total2013']

data2010 = data2009.merge(data2010, on='hh', how='outer')
data2010['Con2010'] = data2010['lnc2010']-data2010['lnc2009']
data2010['N2010'] = data2010['lnN2010']-data2010['lnN2009']
data2010['I2010'] = data2010['lni2010']-data2010['lni2009']
data2010['Total2010'] = data2010['total2010']-data2010['total2009']
data2010 = data2010.merge(data2011, on='hh', how='outer')
data2010['Con2011'] = data2010['lnc2011']-data2010['lnc2010']
data2010['N2011'] = data2010['lnN2011']-data2010['lnN2010']
data2010['I2011'] = data2010['lni2011']-data2010['lni2010']
data2010['Total2011'] = data2010['total2011']-data2010['total2010']
data2010 = data2010.merge(data2013, on='hh', how='outer')
data2010['Con2013'] = data2010['lnc2013']-data2010['lnc2011']
data2010['N2013'] = data2010['lnN2013']-data2010['lnN2011']
data2010['I2013'] = data2010['lni2013']-data2010['lni2011']
data2010['Total2013'] = data2010['total2013']-data2010['total2011']

data2010 = data2010[['hh','Con2010','N2010','I2010','Total2010','Con2011','N2011','I2011','Total2011','Con2013','N2013','I2013','Total2013']]
data10 = data2010[['hh','Con2010','N2010','I2010','Total2010']]
data11 = data2010[['hh','Con2011','N2011','I2011','Total2011']]
data13 = data2010[['hh','Con2013','N2013','I2013','Total2013']]

data1 = np.concatenate((data10,data11), axis = 0)
data1 = np.concatenate((data1,data13), axis = 0)
data1 = pd.DataFrame(data1, columns = ['hh', 'Con', 'N', 'Inc', 'Aggregate'])
data1 = data1.merge(groups, on='hh', how='left').dropna()
data1 = data1[['Con', 'N', 'Inc', 'Aggregate', 'group']]
l = len(data1)
data1['constant'] = np.ones(l)
data1 = data1.reindex()

'''We have the data ready to be used in the regression. We make a loop for make
a regression for every group of family. We are not using groups that have less than 4 observations
we also need to separate groups for which there is no variance on size of family, an the
ones that have variance.'''
count = 0
betasfull = pd.DataFrame([],index=['constant','N','Inc', 'Aggregate'], columns=[1])
betas = pd.DataFrame([],index=['constant','Inc', 'Aggregate'], columns=[1])
for i in range(round(N/4)):
    if any(i==data1['group']) is True:
        family1 = data1.loc[data1['group']==i,['constant','Con', 'N', 'Inc', 'Aggregate']]
        if len(family1['Con'])>3:
            
            X = np.matrix(np.array(family1[['constant','N','Inc', 'Aggregate']]))
            
            if np.linalg.det(X.T@X)==0:
                 X = np.matrix(np.array(family1[['constant','Inc', 'Aggregate']]))
                 Y = np.matrix(np.array(family1[['Con']]))
                 b = inv(X.T*X)*(X.T@Y)
                 betas[i] = b
            else:                
                Y = np.matrix(np.array(family1[['Con']]))
                b = inv(X.T*X)*(X.T@Y)
                betasfull[i] = b
   
    count = count+1
   
betasfull = betasfull.T.dropna()
betasfull = betasfull.sort_values(['Inc'], ascending=[1])
betarural = betasfull['Inc']

betarural = betarural.sort_values(['Inc'], ascending=[1])
betaurban = betaurban.sort_values(['Inc'], ascending=[1])

urban = betaurban.plot.hist(bins=110, alpha=0.5)
rural = betarural.plot.hist(bins=110, alpha=0.5)        
    