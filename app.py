# -*- coding: utf-8 -*-
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pandas import DataFrame as df
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#006eff'
}

r = requests.get('https://coronavirus-tracker-api.herokuapp.com/v2/locations')

r = df(r.json()['locations'])

lon = []
lat = []
for x in r['coordinates']:
    lon.append(x['longitude'])
    lat.append(x['latitude'])

r['lat'] = df(lat)
r['lon'] = df(lon)

confirmed = []
confirmed_size = []
deaths = []
deaths_size = []

for x in r['latest']:
    confirmed.append(x['confirmed'])
    confirmed_size.append(int((x['confirmed']/10000)+10))
    deaths.append(x['deaths'])
    deaths_size.append(int(x['deaths'])/100)

r['confirmed'] = df(confirmed)
r['confirmed_size'] = df(confirmed_size)
r['deaths'] = df(deaths)
r['deaths_size'] = df(deaths_size)

map_confirmed = go.Scattermapbox(
    customdata = r.loc[:, ['confirmed','deaths']],
    name = 'Potwierdzone przypadki',
    lon = r['lon'],
    lat = r['lat'],
    text = r['country'],
    hovertemplate=
        "<b>%{text}<b><br><br>"+
        "Przypadki: %{customdata[0]}<br>"+
        "Zgony: %{customdata[1]}<br>"+
        "<extra></extra>",
    mode = 'markers',
    marker = go.scattermapbox.Marker(
        size = r['confirmed_size'],
        color = 'red',
        opacity = 0.7
    )
)

map_deaths = go.Scattermapbox(
    name = 'Zgony',
    lon = r['lon'],
    lat = r['lat'],
)

layout = go.Layout(
    mapbox_style='white-bg',
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font= {'color': colors['text']},
    autosize=True,
    mapbox_layers=[
        {
            'below':'traces',
            'sourcetype': 'raster',
            'source': [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
    ]
)

layout2 = go.Layout(
    xaxis_title="Data",
    yaxis_title="Suma potwierdzonych przypadków",
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font=dict(
        family="Courier New, monospace",
        size=14,
        color=colors['text']
    )
)

layout3 = go.Layout(
    xaxis_title="Data",
    yaxis_title="Liczba nowych dziennych przypadków",
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font=dict(
        family="Courier New, monospace",
        size=14,
        color=colors['text']
    )
)

data = [map_confirmed]
fig = go.Figure(data = data, layout=layout)

coviddata = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/full_data.csv')
table = pd.pivot_table(coviddata, values='total_cases', index='date', columns=['location'])
table = table.fillna(0).astype(int)
coviddata.set_index('date', inplace=True)

"""
fig2 = px.line(table, x=table.index, y='World')
fig2.update_layout(
    title={
        'text': "Przypadki koronawirusa na świecie",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    xaxis_title="Data",
    yaxis_title="Suma potwierdzonych przypadków",
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font=dict(
        family="Courier New, monospace",
        size=14,
        color=colors['text']
    )
)
"""

fdata  =  go.Scatter(
              x = table.index,
              y = table.World,
              orientation='h',
              line=dict(color='red', width=4)
        )

fig2 = go.Figure(data=fdata, layout=layout2)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='COVID-19 Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': 'Courier New, monospace'
        }
    ),

    html.Div(children='Interaktywna analiza danych dotyczących koronawirusa na świecie', style={
        'textAlign': 'center',
        'color': colors['text'],
        'font-family': 'Courier New, monospace'
    }),

    html.Div([
        html.Div([
            dcc.Graph(id='g1', figure=fig)
        ], className="six columns"),
        html.Div([
            dcc.Graph(id='g2', figure=fig2)
        ], className="six columns"),
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Dropdown(id='dropdown1', options=[
                {'label': i, 'value': i} for i in table.columns], 
                multi=False, placeholder='Wybierz kraj...',
                style = {"background-color":colors['background']}),
            dcc.Graph(
                id='total',
                figure={
                'data': [],
                'layout': {
                    'xaxis':{
                            'showticklabels': False,
                            'ticks': '',
                            'showgrid': False,
                            'zeroline': False
                        },
                    'yaxis':{
                            'showticklabels': False,
                            'ticks': '',
                            'showgrid': False,
                            'zeroline': False
                        },
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font':dict(
                        family="Courier New, monospace",
                        size=14,
                        color=colors['text']
                    )
                }
            }
        )
        ], className="six columns"),
        html.Div([
            dcc.Dropdown(id='dropdown2', options=[
                {'label': i, 'value': i} for i in table.columns], 
                multi=False, placeholder='Wybierz kraj...',
                style = {"background-color":colors['background']}),
            dcc.Graph(
                id='daily',
                figure={
                'data': [],
                'layout': {
                    'xaxis':{
                            'showticklabels': False,
                            'ticks': '',
                            'showgrid': False,
                            'zeroline': False
                        },
                    'yaxis':{
                            'showticklabels': False,
                            'ticks': '',
                            'showgrid': False,
                            'zeroline': False
                        },
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font':dict(
                        family="Courier New, monospace",
                        size=14,
                        color=colors['text']
                    )
                }
            }
        )
        ], className="six columns"),
    ], className="row")
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('total', 'figure'),
    [Input('dropdown1', 'value')])
def update_figure(country):
    if not country:
        raise PreventUpdate
    filtered= table[country]
    udata  =  go.Scatter(
              x = filtered.index,
              y = filtered.values,
              orientation='h',
              line=dict(color='red', width=4)
        )
    fig3 = go.Figure(data=udata, layout=layout2)
    return fig3

@app.callback(
    Output('daily', 'figure'),
    [Input('dropdown2', 'value')])
def update_figure(country):
    if not country:
        raise PreventUpdate
    filtered = coviddata.new_cases[coviddata.location == country]
    fig4  =  px.bar(
        filtered,
        x = filtered.index,
        y = filtered.values,
        color='new_cases',
        labels={'new_cases':'Przypadki'}
        )
    fig4.update_layout(
    xaxis_title="Data",
    yaxis_title="Liczba nowych dziennych przypadków",
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font=dict(
        family="Courier New, monospace",
        size=14,
        color=colors['text']
        )
    )
    return fig4



if __name__ == '__main__':
    app.run_server(debug=True)