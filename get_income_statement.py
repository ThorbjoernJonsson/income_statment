import json
import requests
import pandas as pd
import dash
import dash_table

import numpy as np
from dash_table.Format import Format
import dash_table.FormatTemplate as FormatTemplate

from dash_table.Format import Sign
from dash_table.Format import Group
from dash_table.Format import Scheme
from dash_table.Format import Symbol

import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Output, State, Input

mill = 1000000
hund = 100

def get_income_statement(ticker):
    ticker = ticker.upper()
    url = "https://financialmodelingprep.com/api/v3/income-statement/{}?period=quarter&apikey=c92d837b902bad4813ce892dc7607e63".format(ticker)
    r = requests.get(url)
    r = r.json()
    d = r[0]
    list_d = list(d.items())
    d_changed = list(zip(*list_d))

    income_statement = pd.DataFrame(d_changed[0], columns = ['item'])

    for idx, val in enumerate(r[0:]):
        list_d = list(val.items())
        d_changed = list(zip(*list_d))
        #income_statement[str(idx + 1)] = d_changed[1]
        quarter = d_changed[1][4]
        if d_changed[1][4] == 'FY':
            quarter = 'Q4'
        income_statement[quarter +'-'+d_changed[1][0][0:4]] = d_changed[1]
    return income_statement

def clean_df(df):
    idx = []
    idx_100 = []
    divide_by_mill = ['revenue', 'costOfRevenue', 'grossProfit', 'researchAndDevelopmentExpenses', 'generalAndAdministrativeExpenses',
                      'sellingAndMarketingExpenses', 'otherExpenses', 'operatingExpenses', 'costAndExpenses', 'interestExpense',
                      'depreciationAndAmortization', 'ebitda', 'operatingIncome', 'totalOtherIncomeExpensesNet', 'incomeBeforeTax',
                      'incomeTaxExpense', 'netIncome', 'weightedAverageShsOut', 'weightedAverageShsOutDil']
    multiply_by_100 = ['grossProfitRatio', 'ebitdaratio', 'operatingIncomeRatio', 'incomeBeforeTaxRatio', 'netIncomeRatio']
    for i in divide_by_mill:
        idx_item = df[df['item']==i].index.values
        idx.append(idx_item[0])
    for i in multiply_by_100:
        idx_item = df[df['item'] == i].index.values
        idx_100.append(idx_item[0])



    df.set_index('item', inplace=True)
    for i in idx:
        df.iloc[i] = df.iloc[i]/mill
    for i in idx_100:
        df.iloc[i] = df.iloc[i] * hund

    pd.options.display.float_format = "{:,.2f}".format
    rows_to_drop = ['fillingDate', 'acceptedDate', 'link', 'finalLink', 'period']
    for item in rows_to_drop:
        df = df.drop(item)
    return df

def create_is(df):
    df.loc['D&A'] = df.loc['depreciationAndAmortization'].T
    new_index = ['date', 'revenue', 'costOfRevenue', 'researchAndDevelopmentExpenses',
                 'generalAndAdministrativeExpenses', 'sellingAndMarketingExpenses', 'otherExpenses',
                 'operatingExpenses', 'depreciationAndAmortization', 'totalOtherIncomeExpensesNet', 'costAndExpenses',
                 'grossProfit', 'ebitda', 'D&A', 'operatingIncome', 'interestExpense', 'incomeBeforeTax',
                 'incomeTaxExpense', 'netIncome', 'grossProfitRatio', 'ebitdaratio', 'operatingIncomeRatio',
                 'incomeBeforeTaxRatio', 'netIncomeRatio', 'eps', 'epsdiluted', 'weightedAverageShsOut',
                 'weightedAverageShsOutDil']
    df = df.reindex(new_index)
    return df


if __name__ == '__main__':
    df = get_income_statement('AMZN')
    df = clean_df(df)
    df = create_is(df)
    df = df.reset_index()

    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.Div(dcc.Input(id='input-box', type='text')),
        html.Button('Submit', id='button'),
        dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i, 'type': 'numeric', "format": Format(group = Group.yes, precision = 2, scheme = Scheme.fixed)} for i in df.columns],
        data=df.to_dict('records'),
        ),
        html.Div(id='output-container-button', children=' ')
    ])

    @app.callback(Output('output-container-button', 'children'),
                  [Input('button', 'n_clicks')],
                  [State('input-box', 'value')],
                  )

    def update_output(clicks, input_value):
        if clicks is not None:
            print(clicks, input_value)


    app.run_server(debug=True)
