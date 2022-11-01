import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"
import dash
from dash import dash_table
from dash import dcc
from dash.dependencies import Input, Output
from dash import html
import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash
import plotly.graph_objects as go

def bayut(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    data =[]
    for i in soup.find_all('div',class_='d6e81fd0'):
        d =[soup.find('span', class_ ="fontCompensation").text,
            i.find('span', class_ ="f343d9ce").text,
                i.find('div', class_='_7afabd84').text,
                i.find('h2',{"aria-label": "Title"}).text,
                i.find('span', class_='b6a29bc0').text,
                i.find('span',{"aria-label": "Area"}).text,
                i.find('img', class_='_062617f4')['title']]
        data.append(d)
    return data

def scrap():
    for t in range(2):
        if t == 0:
            condition = "to-rent"
            url1 = f"https://www.bayut.com/{condition}/property/dubai/business-bay/damac-towers-by-paramount-hotels-and-resorts/"
            rent = bayut(url1)
        else:
            condition = "for-sale"
            url2 = f"https://www.bayut.com/{condition}/property/dubai/business-bay/damac-towers-by-paramount-hotels-and-resorts/"
            sale = bayut(url2)
    info =[]
    info.append(rent)
    info.append(sale)
    return(info)

gg = scrap()
gf1 = pd.DataFrame(gg[0], columns = ['Status','Price','Location','Key Words','Bedrooms','Area (sqft)','Agency'])
gf2 = pd.DataFrame(gg[1], columns = ['Status','Price','Location','Key Words','Bedrooms','Area (sqft)','Agency'])
gf = pd.concat([gf1, gf2], axis=0)
gf.reset_index(drop=True, inplace=True)
print(gf)

for_sale_total = len(gf2['Status'])
print(for_sale_total)
rent_total = len(gf1['Status'])
print(rent_total)
all_total = for_sale_total + rent_total

gf['Area (sqft)'] = gf['Area (sqft)'].str.replace(r'[A-Z ,:a-z]', '').astype(float)
gf['Price'] = gf['Price'].replace('\$|,', '', regex=True)
gf['Price'] = pd.to_numeric(gf['Price'])
pd.options.display.float_format = '{:.0f}'.format
print(gf)

filter1 = gf['Status'] == 'Buy'
buy = gf[filter1]
ABS1 = buy['Price'].mean()
ABS =format(ABS1, ".2f")
print(f'Average Price of Buy segment:- {ABS}')

filter2 = gf['Status'] == 'Rent'
rent = gf[filter2]
ARS1 = rent['Price'].mean()
ARS =format(ARS1, ".2f")
print(f'Average Price of Rent segment:- {ARS}')

ROI1 = (ARS1*12)/ABS1
print(ROI1)
ROI =format(ROI1, ".2f")
print(f'ROI is:- {ROI}')

dat =[[ABS,ARS,ROI]]
print(dat)
df = pd.DataFrame(dat, columns = ['ABS','ARS','ROI'])
print(df)

df = gf
df['id'] = df['Status']+df.index.astype('str')
df.set_index('id', inplace=True, drop=False)
print(df)


def fig_bed(st, bdd):
    colors = ['rgb(102,255,255)', 'rgb(255,0,127)']
    if st == 'All':
        data = df[(df['Status'] == 'Buy') & (df['Bedrooms'] == bdd)]
        a = data['Bedrooms'].count()
        data2 = df[(df['Status'] == 'Rent') & (df['Bedrooms'] == bdd)]
        b = data2['Bedrooms'].count()
        x = [a, b]
        y = ['Buy', 'Rent']
        xaxis_title = f"Number of {bdd} Bedroom"

    elif bdd == 'All' and st == 'All':
        apa = list(df['Bedrooms'].unique())
        x = []
        y = []
        for i in range(len(apa)):
            data = df[(df['Bedrooms'] == apa[i])]
            a = data['Bedrooms'].count()
            x.append(a)
            b = data['Bedrooms'].unique()[0]
            y.append(b)
            xaxis_title = f"Number of {bdd} Bedrooms"

    elif bdd == 'All' and st == 'Buy':
        data = df[(df['Status'] == 'Buy')]
        apa = list(data['Bedrooms'].unique())
        x = []
        y = []
        for i in range(len(apa)):
            data2 = data[(data['Bedrooms'] == apa[i])]
            a = data2['Bedrooms'].count()
            x.append(a)
            b = data2['Bedrooms'].unique()[0]
            y.append(b)
            xaxis_title = f"Number of {bdd} Bedrooms"

    elif bdd == 'All' and st == 'Rent':
        data = df[(df['Status'] == 'Rent')]
        apa = list(data['Bedrooms'].unique())
        x = []
        y = []
        for i in range(len(apa)):
            data2 = data[(data['Bedrooms'] == apa[i])]
            a = data2['Bedrooms'].count()
            x.append(a)
            b = data2['Bedrooms'].unique()[0]
            y.append(b)
            xaxis_title = f"Number of {bdd} Bedrooms"

    else:
        data = df[(df['Status'] == st) & (df['Bedrooms'] == bdd)]
        a = data['Bedrooms'].count()
        b = data['Status'].unique()
        x = [a]
        y = b
        xaxis_title = f"Number of {bdd} Bedroom"

    fig = go.Figure(data=[go.Bar(x=x, y=y, orientation='h')])
    fig.update_traces(marker_color=colors, marker_line_color='rgb(0,0,0)',
                      marker_line_width=1, opacity=0.8)
    fig.update_layout(title_text='Status Vs Bedrooms')
    fig.update_layout(title_x=0.5, plot_bgcolor='#F2DFCE', paper_bgcolor='#F2DFCE', xaxis_title=xaxis_title)
    return fig

apa = list(df['Bedrooms'].unique())
x=[]
y =[]
for i in range(len(apa)):
    data=df[(df['Bedrooms']== apa[i])]
    a = data['Bedrooms'].count()
    x.append(a)
    b = data['Bedrooms'].unique()[0]
    y.append(b)
    xaxis_title = f"Number of  Bedrooms"


def fig_abs_ars(sel):
    if sel == 'Rent':
        x = ['ABS', 'ARS']
        y = [ABS1, ARS1]
        colors = ['rgb(102,255,255)', 'rgb(255,0,127)']
        # Use the hovertext kw argument for hover text
        fig = go.Figure(
            data=[go.Bar(x=x, y=y, hovertext=['Average Price of Buy Segment', 'Average Price of Rent Segment'])])

    else:
        x = ['ARS', 'ABS']
        y = [ARS1, ABS1]
        colors = ['rgb(255,0,127)', 'rgb(102,255,255)']
        # Use the hovertext kw argument for hover text
        fig = go.Figure(
            data=[go.Bar(x=x, y=y, hovertext=['Average Price of Rent Segment', 'Average Price of Buy Segment'])])

    fig.update_traces(marker_color=colors, marker_line_color='rgb(0,0,0)',
                      marker_line_width=1, opacity=0.8)
    fig.update_layout(title_text='ABS & ARS')
    fig.update_layout(title_x=0.5, plot_bgcolor='#F2DFCE', paper_bgcolor='#F2DFCE')
    return fig

external_stylesheets = [dbc.themes.BOOTSTRAP]

#*****************************************#
#app = JupyterDash(__name__,external_stylesheets=external_stylesheets)
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server
#*****************************************#

app.title = 'DAMAC Towers Bayout.com'
colors = {
    'background': '#111111',
    'bodyColor':'#F2DFCE',
    'text': '#7FDBFF'
}
def get_page_heading_style():
    return {'backgroundColor': colors['background']}


def get_page_heading_title():
    return html.H1(children='Data Insights From Bayout.com',
                                        style={
                                        'textAlign': 'center',
                                        'color': colors['text']
                                    })

def get_page_heading_subtitle():
    return html.Div(children='Insights of DAMAC Towers by Paramount Hotels and Resort',
                                         style={
                                             'textAlign':'center',
                                             'color':colors['text']
                                         })

def generate_page_header():
    main_header =  dbc.Row(
                            [
                                dbc.Col(get_page_heading_title(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    subtitle_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_subtitle(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    header = (main_header,subtitle_header)
    return header

def get_status():
    at =list(gf['Status'].unique())
    at.append('All')
    at
    return at


def get_bed():
    ap =list(gf['Bedrooms'].unique())
    ap.append('All')
    ap
    return ap

def create_dropdown_list(status):
    dropdown_list = []
    for stat in sorted(status):
        tmp_dict = {'label':stat,'value':stat}
        dropdown_list.append(tmp_dict)
    return dropdown_list

def create_dropdown_list2(bedrooms):
    dropdown_list2= []
    for bed in sorted(bedrooms):
        tmp_dict2 = {'label':bed,'value':bed}
        dropdown_list2.append(tmp_dict2)
    return dropdown_list

def get_status_dropdown(nd):
    return html.Div([
                        html.Label('Select Status'),
                        dcc.Dropdown(id='my-id'+str(nd),
                            options=create_dropdown_list(get_status()),
                            value='Buy'
                        ),
                        html.Div(id='my-div'+str(nd))
                    ])

def get_bed_dropdown(bd):
    return html.Div([
                        html.Label('Number of Bedrooms'),
                        dcc.Dropdown(id='my-bd'+str(bd),
                            options=create_dropdown_list(get_bed()),
                            value='1'
                        ),
                        html.Div(id='my-biv'+str(bd))
                    ])

def graph1():
    return dcc.Graph(id='graph1',figure=fig_abs_ars('Rent'))
def graph2():
    return dcc.Graph(id='graph2',figure=fig_bed('Rent','All'))

def generate_card_content(card_header,card_value,overall_value):
    card_head_style = {'textAlign':'center','fontSize':'150%'}
    card_body_style = {'textAlign':'center','fontSize':'200%'}
    card_header = dbc.CardHeader(card_header,style=card_head_style)
    card_body = dbc.CardBody(
        [
            html.H5(f"{float(card_value):,}", className="card-title",style=card_body_style),
            html.P(
                "Number of Property: {:,}".format(overall_value),
                className="card-text",style={'textAlign':'center'}
            ),
        ]
    )
    card = [card_header,card_body]
    return card

def data_table():
    table = html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
                if i == "Key Words" or i == "Location" or i == "id"
                else {"name": i, "id": i, "deletable": True, "selectable": True}
                for i in df.columns
            ],
            data=df.to_dict('records'),  # the contents of the table
            editable=False,              # allow editing of data inside all cells
            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",         # sort across 'multi' or 'single' columns
            column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            #row_selectable="multi",     # allow users to select 'multi' or 'single' rows
            row_deletable=False,         # choose if user can delete a row (True) or not (False)
            selected_columns=[],        # ids of columns that user selects
            selected_rows=[],           # indices of rows that user selects
            page_action="native",       # all data is passed to the table up-front or not ('none')
            page_current=0,             # page number that user is on
            page_size=20,                # number of rows visible per page
            fixed_rows={'headers': True, 'data': 0 },
            style_cell={
                'height': 'auto',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_cell_conditional=[    # align text columns to left. By default they are aligned to right
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Status', 'Location']
            ],
            style_data={                # overflow cells' content into multiple lines
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_table={
                'maxHeight': '300px',
                'overflowX': 'scroll'},
        ),

        html.Br(),
        html.Br()])
    return table


def generate_cards():
    abs_val = ABS
    ars_val = ARS
    # roi_val = int("{:.2%}".format(ROI1))
    roi_val = ROI

    cards = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(generate_card_content("Average Price of Buy segment", abs_val, for_sale_total),
                                     color="success", inverse=True), md=dict(size=2, offset=3)),
                    dbc.Col(dbc.Card(generate_card_content("Average Price of Rent segment", ars_val, rent_total),
                                     color="warning", inverse=True), md=dict(size=2)),
                    dbc.Col(dbc.Card(generate_card_content("Return On Investment", roi_val, all_total), color="dark",
                                     inverse=True), md=dict(size=2)),
                ],
                className="mb-4",
            ),
        ], id='card1'
    )
    return cards


def generate_layout():
    page_header = generate_page_header()
    layout = dbc.Container(
        [
            page_header[0],
            page_header[1],
            html.Hr(),
            generate_cards(),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(get_status_dropdown(1), md=dict(size=2, offset=3)),
                    dbc.Col(get_bed_dropdown(1), md=dict(size=2, offset=3))
                ]

            ),
            data_table(),
            dbc.Row(
                [
                    dbc.Col(graph1(), md=dict(size=3, offset=0)),
                    dbc.Col(graph2(), md=dict(size=5, offset=2))

                ], align="center",

            ),
        ], fluid=True, style={'backgroundColor': colors['bodyColor']}
    )
    return layout

app.layout = generate_layout()

@app.callback(
    [Output(component_id='graph1',component_property='figure'), #line chart
    Output(component_id='graph2',component_property='figure')], #overall card numbers
    [Input(component_id='my-id1',component_property='value'),
    Input(component_id='my-bd1',component_property='value')])


def update_output_div(input_value1,input_value2):
    ggg = fig_abs_ars(input_value1)
    ttt = fig_bed(input_value1,input_value2)
    return ggg,ttt

#app.run_server(mode='external')

if __name__ == '__main__':
    app.run_server(debug=True)

