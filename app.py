from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
from pandas.io.json import json_normalize
import datetime
from calendar import monthrange
# from __future__ import print_function

app = Flask(__name__)

@app.route('/')
def plot_price():
    # TODO: possible arguments - stock (ticker name), column (which data to plot), start & end dates?



    # TODO: stock should be the ticker chosen by user
    STOCK = 'AAPL'
    COLUMN = 'Adj. Close'

    def minus_one_month(current_date):
        '''return YYYY-MM-DD for current_date minus one month.'''
        last_month = datetime.date(current_date.year, current_date.month, 1) - datetime.timedelta(days=1)
        days_last_month = monthrange(last_month.year, last_month.month)[1]
        if current_date.day <= days_last_month:
            return last_month.replace(day=current_date.day).strftime('%Y-%m-%d')
        else:
            return last_month.replace(day=days_last_month).strftime('%Y-%m-%d')

    # get date range
    current_time = datetime.datetime.today()
    end_date = current_time.strftime('%Y-%m-%d')
    start_date = minus_one_month(current_time)

    api_url = 'https://www.quandl.com/api/v3/datasets/WIKI/{}.json'.format(STOCK) + \
              '?start_date={}&end_date={}'.format(start_date, end_date)
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)

    data = raw_data.json()
    columns = data['dataset']['column_names']
    # Load tabular price data into df_data
    df_data = json_normalize(data['dataset'], 'data')
    df_data.columns = columns
    df_data['Date'] = pd.to_datetime(df_data['Date'])

    plot = figure(title='Data from Quandle WIKI set',
                  x_axis_label='date',
                  x_axis_type='datetime')
    plot.line(df_data['Date'], df_data[COLUMN], legend=STOCK)

    script, div = components(plot)
    return render_template('graph.html', script=script, div=div)
    #return render_template('index.html')

# @app.route('/')
# def index():
#   return render_template('index.html')


if __name__ == '__main__':
  app.run(port=33507)
