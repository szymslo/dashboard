# -*- coding: utf-8 -*-
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from pandas import DataFrame as df
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#d41002'
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

data = [map_confirmed]
fig = go.Figure(data = data, layout=layout)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='COVID-19 Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Interaktywna analiza danych dotyczących koronawirusa na świecie', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div([
        html.Div([
            dcc.Graph(id='g1', figure=fig)
        ], className="six columns"),
        html.Div([
            dcc.Graph(
            id='example-graph-2',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            }
         )], className="six columns"),

    ], className="row")
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)