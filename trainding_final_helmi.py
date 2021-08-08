# -*- coding: utf-8 -*-
import pandas as pd
import os
import numpy as np
import pickle
import matplotlib.pyplot as plt 
from datetime import datetime
from time import time 
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
import base64
import ccxt
from fonctions import *
import time as tm



 
crypto ={}
market=['AAVE/USDT','LUNA/USDT','MATIC/USDT','THETA/USDT','VET/USDT','SOL/USDT','TRX/USDT',
        'EOS/USDT','BCH/USDT','LTC/USDT','LINK/USDT','XLM/USDT','ETH/USDT','BTC/USDT','UNI/USDT','ADA/USDT','DOT/USDT',
        'KSM/USDT','BNB/USDT','XRP/USDT','DOGE/USDT']#mettre ces crypto pour le cloud  (ETH , ADA, DOT, BNB, DOGE)


apiKey = '2CNNMG6X4XEJhXzEGVa3hVPztX83jpMldyUlks4c3XWNJz4Gn8fZKnRDZYtELO0M'
secret = 'vG4AJ9HifbF0X83cOn5qICUU4xB8Xs5eEpz0Y3Wp6qns7rq0KfMwc0qNmeRNpI5X'

i_iteration =4
delta_hour = '8h'
type_computing ='n-1' #  entrée possible,n-1, n-2 , none 

exchange = ccxt.binance({
    'apiKey': apiKey,
    'secret': secret,
    'enableRateLimit': True
    })


# initialisation temps 

start_time = datetime.now()
k=0
liste_principale=[]
liste_achat=[]
liste_vente=[]
temps=[]
comput_list=[]


while True:


        print("première iteration  : ",start_time)   
        print("horaire now",datetime.now())
        print ("iteration numéto : ", k)    

        comput_list=[]
        for elm in market :
            x =elm.lower()
            ohlcv = exchange.fetch_ohlcv(elm , limit = 4, timeframe = delta_hour)
            crypto[x] = pd.DataFrame(ohlcv,columns=['timestamp', x[:-5]+'_open', 'high','low', x[:-5]+'_close', 'volume'])            
            crypto[x] = convert_time(crypto[x])
            crypto[x] = crypto[x][['timestamp',x[:-5]+'_open',x[:-5]+'_close']] 
            crypto[x] = crypto[x].set_index('timestamp')        
            crypto[x] = crypto[x].merge(variation(crypto[x]),on ='timestamp',how='left')
            df_variation_computing = variation_computing(crypto[x], type_computing) 
            comput_list.append(df_variation_computing)           
            #df_variation_computing = df_variation_computing.merge(xz , on='delt_compt' , how= 'left')              
            #print(crypto[x].merge(variation_computing(crypto[x], type_computing), on ='delt_compt', how ='left'))
            crypto[x]['coef_multi_'+x[:-5]] = coef_multi(crypto[x])            
            crypto[x]  = fonction_cumul(crypto[x],x)        
            print(crypto[x])    
        df_liste_var =  fonction_tableau_var(crypto)          
        tableau_var = meilleur_varaition(df_liste_var) 
        concenate_computing = np.concatenate(comput_list, axis=1)
        print('\n\n\nLes cryptos  : ',market,'\n\nLe nombre de crypto :  ', np.shape(market)[0])
        df_computing = pd.DataFrame(concenate_computing ,index =df_variation_computing.index, columns=market)
        print('\n\n\nTableau computing\n',df_computing)
        
        if type_computing ==('n-2') or type_computing ==('n-1')  :
            max_var_computing, name_max_var_computing = meilleur_var_computing(df_computing, type_computing)
            print('\n\n\n\nLe nom de la crypto avec computing: ', name_max_var_computing,'\nType de computing: ', type_computing,'\nValeur Max_var_computing:', max_var_computing,'\n\n\n')
            
            print('Tableau variation \n',tableau_var)
            
            
            nom_crypto_vente= crypto_a_vendre(exchange, market ) 
            algo_achat_vente(exchange, nom_crypto_vente, name_max_var_computing) 
            print('\n\n\n\n la crypot à vendre est ',nom_crypto_vente)
            print('la crypot à acheter est ',name_max_var_computing)
            k=k+1
            liste_principale.append([datetime.now(), name_max_var_computing, nom_crypto_vente])
            print(pd.DataFrame(liste_principale, columns=['temps','crypto vente','crypto achat']))
        
            if name_max_var_computing ==  nom_crypto_vente:
                print('\n\n On reste sur la même crypto')
            else:
                print('\n\n Crypto à vendre ',nom_crypto_vente)
                print('crypto à acheter',name_max_var_computing)
            
            
        else :
            print('nous sommes dans le else')         
            tableau_var['algo'] = algo(tableau_var)        
            tableau_var['coef_multi'] = tableau_var['algo'].cumprod()   
            print(tableau_var )
            nom_crypto_achat =  nom_crypto_achat_vente(tableau_var)
            print ('le nom de la cripto à acheter ', nom_crypto_achat )             
            nom_crypto_vente= crypto_a_vendre(exchange, market )         
            algo_achat_vente(exchange, nom_crypto_vente, nom_crypto_achat)        
            print('la crypot à vendre est ',nom_crypto_vente)
            print('la crypot à acheter est ',nom_crypto_achat)
            k=k+1
            liste_principale.append([datetime.now(), nom_crypto_achat, nom_crypto_vente])
            print(tableau_var)
            print(pd.DataFrame(liste_principale, columns=['temps','crypto vente','crypto achat']))
        
            if nom_crypto_achat ==  nom_crypto_vente:
                print('On reste sur la même crypto')
            else:
                print('crypto à vendre ',nom_crypto_vente)
                print('crypto à acheter',nom_crypto_achat)
       


        tm.sleep(3600*i_iteration)

    




    
    
