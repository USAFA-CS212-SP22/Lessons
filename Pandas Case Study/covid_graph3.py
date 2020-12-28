# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 09:12:51 2020

@author: douglas.wickert
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime
import scipy.optimize as optim
import numpy as np



url1 = ('https://raw.githubusercontent.com/'+
      'CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')
url2 = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

ccon = pd.read_csv(url2, error_bad_lines=False)  #COVID-19 confirmed cases
ccon = ccon.rename(columns={'Province/State': 'State',
                            'Country/Region': 'Country'})

#countries of interest to plot
coint  = ['US', 'China', 'Italy', 'Spain', 'France', 'Germany','Korea, South', 'United Kingdom', 'Australia', 'India']

graph_start_date = '1/22/20'
time_stamp_obj = datetime.datetime.utcnow()
time_stamp = time_stamp_obj.strftime('%Y-%m-%d %H:%M GMT')

c2 = ccon.columns.get_loc(graph_start_date)

fig, ax = plt.subplots(1, figsize=(9,6), dpi=300)

for c in coint:
    k = ccon.loc[ccon['Country']==c,:].index[:]  #row indices for country c
    y = ccon.iloc[k,c2:ccon.shape[1]].sum(axis=0)  #sums every region in country c
    
#    ax.semilogy(y, linestyle='-.', label = c)
#    ax.annotate(c,xy=(ccon.columns[-1],y[-1]),fontsize = 8)


    if c == 'US':
        ax.semilogy(y, linestyle='-', linewidth=3.0, label = 'US Total')#,color='r')
#        ax.annotate('US Total',xy=(ccon.columns[c2+5],y[5]+10),color='r',weight='bold',fontsize = 8)
    elif c == 'China':
        ax.semilogy(y, linestyle='-.', linewidth=2.0, label = 'China')#,color='orange')
#        ax.annotate('China',xy=(20,y[5]-15000),color='orange',weight='bold',fontsize = 8)
    else:
        ax.semilogy(y, linestyle='-', label = c)
#        ax.annotate(c,xy=(ccon.columns[-1],y[-1]),fontsize = 8)
    ax.annotate(c,xy=(ccon.columns[-1],y[-1]),fontsize = 8)

 
legend = ax.legend(loc='upper left')
ax.set_title('Confirmed COVID-19 cases (data from Johns Hopkins CSSE - '+
                                        time_stamp + ')',fontsize = 9)
plt.xticks(rotation=90, fontsize=8)
plt.ylim([10,1.0E6])
plt.ylabel('Confirmed Cases', fontsize=9)
plt.show()
plt.tight_layout()

every_nth = 3
for n, label in enumerate(ax.xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)
        
time_stamp = time_stamp_obj.strftime('%Y_%m_%d_%H00GMT')
plt.savefig('covid' + time_stamp + '.png', dpi = 300)
plt.close()


################################################################
# Fit logistic curve to data

def logistic_model(t, t0, a0, b, K):
    return K / (1 + a0 * np.exp(-b*(t-t0)))

fig, ax = plt.subplots(1, figsize=(10,4), dpi=300)

#loop over countries of interest

for c in coint:
    # Randomly initialize the coefficients
    p0 = np.random.exponential(size=4)
    # Set min bound and max on all coefficients (min = 0, max varies)
    bounds = (0, [100, 100000., 10., 1.0E9])  # [t0, a0, b, K]
    
    # Create np.Array  from data frame
    N = len(ccon.columns[c2:].tolist())  #number of days

    k = ccon.loc[ccon['Country']==c,:].index[:]  #row indices for country c
    yy = ccon.iloc[k,c2:ccon.shape[1]].sum(axis=0)  #sums every region in country c

    xx = np.arange(1,N+1)
#    yy = ccon.loc[ccon['Country']==c,:].values[0,c2:]  #slice starting from column 5 which is first date
    
    
    #Scipy nonlinear least-squares curve fit 
    (t0,a0,b,K),cov = optim.curve_fit(logistic_model, xx, yy, bounds=bounds, p0=p0, maxfev=1000000)
                    
    # The time step at which the growth is fastest
    t_fastest = np.log(a0) / b
    i_fastest = logistic_model(t_fastest, t0, a0, b, K)
    
    
    ax.scatter(xx,yy,s=5)
    N2 = 120 #number of days to forecast
    tt_fore = np.arange(1,N2)
    ax.plot(tt_fore,logistic_model(tt_fore, t0, a0, b, K), label = c)
    #ax.set_yscale('log')

legend = ax.legend(loc='upper left', fontsize=8)
plt.ylim([100,0.6E6])
plt.ylabel('Confirmed Cases', fontsize=10)
ax.tick_params(axis='y', labelcolor='k', labelsize=8)
plt.xticks(tt_fore, pd.date_range(ccon.columns[c2],periods=N2).strftime('%m/%d'),rotation=90,fontsize=8)  
ax.set_title('Nonlinear Least-Squares Curve Fit to Logistic Eqn (COVID-19 data from Johns Hopkins CSSE - '+
                                        time_stamp + ')',fontsize = 8)
every_nth = 3
for n, label in enumerate(ax.xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)

plt.savefig('logistic' + time_stamp + '.png', dpi = 300)
plt.close()
