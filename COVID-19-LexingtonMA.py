# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:49:42 2020

@author: Su
"""
import pandas as pd
import numpy as np
import panel as pn
import hvplot.pandas
import holoviews as hv
import datetime as dt
import os.path, time

from bokeh.models import HoverTool

pn.extension()

Input_csv_flename = "COVID19_Lexington_2020.csv"
#Input_csv_filename = "https://github.com/air-wenzheng/covid-19-lexingtonMA/blob/master/COVID19_Lexington_2020.csv"

tickers = ['Lexington', 'Middlesex', 'Massachusetts','Death_in_MA']

#tickers = ['Lexington', 'Massachusetts','Death_in_MA']
ticker = pn.widgets.Select(name='Selection', options=tickers,value=tickers[0],width=200)

# this creates the date range slider
date_range_slider = pn.widgets.DateRangeSlider(
name='Date Range',
start=dt.datetime(2020,8,19), end=dt.datetime(2021, 12, 31),
value=(dt.datetime(2020,8,19), dt.datetime(2021, 12, 31)),width=300)

checkbox = pn.widgets.Checkbox(name='Log Scale',width=100)

#semilogy = hv.Scatter(df,['Date','Lexington'], label='Lexington').opts(logy=True)
title = '### COVID-19 in Lexington, MA (Weekly Update)'

subtitle = 'This dashboard shows COVID-19 confirmed cases in Lexington, Middlesex and Massachusetts, and deaths in Massachusetts. Data sources come from mass.gov COVID-19 Weekly Update.'

subtitle2 = 'Note: Only show data after August 12, 2020, due to data source updated by MassHealth.'


text = """
#  COVID-19 in Lexington, MA


Note: Starts from June 29, 2002, Town of Lexington only provides weekly data. To be consistant with the MassHealth data, we will only cite weekly data from MassHealth COVID-19 dataset.

The map of Town/City weekly COVID-19 cases in MA can be found from: http://covid-19-ma-town.herokuapp.com/covid-19-ma-town

This dashboard shows COVID-19 confirmed cases in Lexington and Massachusetts, and deaths in Massachusetts. 
Data sources come from Town of Lexington and mass.gov COVID-19 Daily Update and NYTimes database.
"""

#footnote = '(Last updated on 4:30pm July 1, 2020)'
os.environ['TZ'] = 'US/Eastern'
modTimesinceEpoc = os.path.getmtime(Input_csv_flename)
modificationTime = dt.datetime.fromtimestamp(modTimesinceEpoc).strftime('%Y-%m-%d %H:%M:%S')

footnote = "Last updated at: %s (EDT time) by Wenzheng Yang (wenzhengy 'at' gmail.com) " % modificationTime

@pn.depends(ticker.param.value, date_range_slider.param.value,checkbox.param.value)
def get_plot(ticker, date_range, log_scale):

     df= pd.read_csv(Input_csv_flename,skiprows=1)
     df['date'] = pd.to_datetime(df['date'])
     df['daystr'] = df['date'].dt.strftime('%Y-%B-%d')

     print('log scale switch= ', log_scale)
     print('ticker selection = ',ticker)
     # Load and format the data
     # create date filter using values from the range slider
     # store the first and last date range slider value in a var
     start_date = date_range_slider.value[0] 
     end_date = date_range_slider.value[1] 
     # create filter mask for the dataframe
     mask = (df['date'] > start_date) & (df['date'] <= end_date)
     df = df.loc[mask] # filter the dataframe
     
     if ticker!='Death_in_MA':
         tooltips0 = [
                 ('Date','@daystr'),
                 ('Confirmed Cases in ' + ticker,'@'+ticker)
                 ]
         cum_hover = HoverTool(tooltips=tooltips0,
                               toggleable=False,
                               formatters={
                                'Date':'datetime',
                                'Confirmed Cases':'numeral'},mode='vline'
                              )      
     if ticker=='Death_in_MA':
        tooltips0 = [
                 ('Date','@daystr'),
                 ('Deaths in MA','@'+ticker)
                 ]
        cum_hover = HoverTool(tooltips=tooltips0,
                              toggleable = False,
                               formatters={
                                'Date':'datetime',
                                'Deaths in MA':'numeral'},mode='vline'
                              )
      # not show hover and corshair tools=[cum_hover,'crosshair'],
     semilogy1 = hv.Scatter(df,['date',ticker],vdims=['daystr',ticker]).opts(logy=log_scale,color="red",tools=[cum_hover])
#     semilogy2 = hv.Scatter(df,['date','MiddleSex'], label='MiddleSex').opts(logy=log_scale)
#     semilogy3 = hv.Scatter(df,['date','Massachusetts'], label='Massachusetts').opts(logy=log_scale)
     curveplot0 = hv.Curve(df,['date',ticker]).opts(color="green")

     if ticker!='Death_in_MA':
          semilogy1.opts(logy=log_scale,width=650,height=600,xlabel='Date',ylabel='COVID-19 Confirmed Cases',
                         title=ticker, show_grid=True, fontscale=1.5,size=5, padding=0.1,
                         line_width=5,legend_position='top_left',bgcolor='lightgray')
     if ticker=='Death_in_MA':
          semilogy1.opts(logy=log_scale,width=650,height=600,xlabel='Date',ylabel='COVID-19 Deaths in Mass',
                         show_grid=True, fontscale=1.5,size=5, padding=0.1, line_width=5,
                         legend_position='top_left',bgcolor='lightgray')
     # also show daily increasement
     temp_diff =  np.diff(df[ticker])
     daily_increase = np.append([0],temp_diff)
#     daily_data =pd.DataFrame()
#     daily_data['date'] = df['date']
#     daily_data['di'] = daily_increase
#     table = hv.Table((df['date'], daily_increase), 'date', 'daily_increase')
     df['di']  =  daily_increase

     if ticker!='Death_in_MA':     
         tooltips = [
                 ('Date','@daystr'),
                 ('Weekly Increment in '+ ticker,'@di')
                 ]
     elif ticker=='Death_in_MA':
         tooltips = [
                 ('Date','@daystr'),
                 ('Weekly Increment in deaths','@di')
                 ]
     di_hover = HoverTool(tooltips=tooltips,toggleable=False)
     
#     barplot = hv.Bars(table).opts(width=800,height=200,xlabel='Date',ylabel='Daily Increase', show_grid=True,color="red")
     if ticker!='Death_in_MA':
         # not show hover and corshair tools=[di_hover,'crosshair'],
         barplot = hv.Scatter(df,['date','di'], vdims=['daystr','di']).opts(tools=[di_hover],width=650,height=300,
                                                                            xlabel='Date',ylabel='Weekly Cases Increment',title=ticker,
                                                                            show_grid=True, fontscale=1.5,size=5, padding=0.1,
                                                                            line_width=5,color="red",bgcolor='lightgray')
     if ticker=='Death_in_MA':
         # not show hover and corshair tools=[di_hover,'crosshair'],
         barplot = hv.Scatter(df,['date','di'], vdims=['daystr','di']).opts(tools = [di_hover],width=650,height=300,
                                                                            xlabel='Date',ylabel='Weekly Deaths Increment',show_grid=True,
                                                                            fontscale=1.5,size=5, padding=0.1, line_width=5,
                                                                            color="red",bgcolor='lightgray')

     curveplot = hv.Curve(df,['date','di']).opts(color="green")
     return pn.Column(barplot*curveplot, semilogy1*curveplot0)
 
dashboard = pn.Column(title,pn.Row(date_range_slider,checkbox,ticker,background="WhiteSmoke"),get_plot,subtitle,subtitle2,footnote,sizing_mode="stretch_height")

dashboard.servable('COVID-19-LexingtonMA')
    
