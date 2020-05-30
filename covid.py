'''
Authors: Subramanian VEERAPPAN & Akshaya RAVI
Course: Data Visualization
Stream: MSc Artificial Intelligence Systems
'''

# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Plotly imports
import plotly.express as px
import plotly.graph_objects as go

# Other imports
import pandas as pd


# Data preprocessing
# read the data and parse the dates
dateParser = lambda x: pd.datetime.strptime(x, "%d/%m/%Y")
data = pd.read_excel("covidIndia.xlsx", parse_dates=['Date Announced'], date_parser=dateParser)

# replace missing data
data = data.fillna('NA')

# processing data for 'type of transmission' 
trans_type_pivot = pd.pivot_table(data, values="Patient Number", index=["Type of transmission","Gender"], aggfunc=len)

values = []
counter = 0 
type_of_transmission = ['Imported','Local','NotAvailable','ToBeDetermined']

while(counter < 3):
    temp = []
    for idx, i in enumerate(trans_type_pivot.values[counter::3]):
        temp.append(i[0])
    values.append(temp)
    counter = counter+1

tran_type_data=[
    {'x': type_of_transmission, 'y': values[0], 'type': 'bar', 'name': 'F'},
    {'x': type_of_transmission, 'y': values[1], 'type': 'bar', 'name': 'M'} ,
    {'x': type_of_transmission, 'y': values[2], 'type': 'bar', 'name': 'NotAvailable'},
]

# processing data for 'total number of cases by date'
date_pivot = pd.pivot_table(data,values="Patient Number",index=["Date Announced"],aggfunc=len)

fig_time_series = px.line(x = date_pivot.index[:-1], y = date_pivot.values.flatten()[:-1], title = 'Time Series with Rangeslider')
fig_time_series.update_xaxes(rangeslider_visible=True)
fig_time_series.update_layout(title = 'No of cases vs Date with rangeslider',
                xaxis = {'title': 'Date'},
                yaxis = {'title': 'No of cases'},
                hovermode = 'closest')

# processing data for 'statewise cases'
state_pivot = pd.pivot_table(data,values="Patient Number",index=["Detected State"],aggfunc=len).sort_values(by='Patient Number',ascending=False)

labels = state_pivot.index
values = state_pivot.values.flatten()

fig_state_data = {
    'data':[go.Pie(labels=labels, values=values, hole=.3, textinfo='none')],
    'layout' : {'title' : 'Statewise distribution of cases'}
 }

# processing data for 'age wise'
bins= [0, 13, 20, 60, 110]
labels = ['Kid','Teen', 'Adult', 'Senior citizen']

data_age = pd.to_numeric(data['Age Bracket'], errors='coerce')
data_age = data_age.replace('NA', -1)
age_categorical = pd.cut(data_age, bins=bins, labels=labels, right=False)
age_pivot = age_categorical.value_counts()

fig_age_data = px.funnel_area(names = age_pivot.index,
                    values = age_pivot.values.flatten())

fig_age_data.update_layout(title = 'Age wise distribution of cases')

# processing data for 'patient current status'
status_pivot = pd.pivot_table(data, values="Patient Number", index=["Current Status"], aggfunc=len).sort_values(by='Patient Number',ascending=False)

labels = status_pivot.index
values = status_pivot.values.flatten()

fig_status_data = {
    'data':[go.Pie(labels=labels, values=values)],
    'layout' : {'title' : 'Patient status'}
 }

# Graphs
transmission_graph = dcc.Graph(
        id = 'type_of_transmission_graph',
        figure = {
            'data': tran_type_data,
            'layout': {
                'title': 'Type of transmission'
            }
        }
    )

total_cases_graph = dcc.Graph(
    id = 'No_of_patients-vs-date',
    figure = fig_time_series
)

statewise_graph = dcc.Graph(
    id = 'Statewise Cases',
    figure = fig_state_data
)

agewise_graph = dcc.Graph(
    id = 'Age wise Cases',
    figure = fig_age_data
)

case_history_graph = dcc.Graph(
        id='No_of_patients-vs-date_stateinfo',
        figure={
            'data': [
                dict(
                    x=data[data['Detected State'] == i]['Date Announced'],
                    y=data[data['Detected State'] == i]['Patient Number'],
                    text=data[data['Detected State'] == i]['Detected State'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in data['Detected State'].unique()
            ],
            'layout': dict(
                title = 'Case emergence based on state',
                xaxis={'title': 'No of days'},
                yaxis={'title': 'Case No'},
                hovermode='closest'
            )
        }
)

patient_status_graph = dcc.Graph(
    id = 'Patient status',
    figure = fig_status_data
)


# CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Custom css
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(style={
    'backgroundColor': colors['background'],
    'color': colors['text'],
    'padding': '5%',
    'padding-left': '5%'
    }, 
    children=[
        html.H1(children='Novel Corona virus in India'),
    
        html.Div(children=['''
            Dashboard for analysing spread of corona in India
        ''',
        
        html.Div(children=[
            html.P(style={
                'color': 'white',
                'margin-top': '20px'
                },
                children='Please select a visualization from the below drop down:'
            ),
            dcc.Dropdown(id='drop-down',
                style={
                'color': 'black',
                'width': '65%',
                'margin-top': '10px',
                },
                options=[
                    {'label': 'Type of transmission', 'value': 'TRANS'},
                    {'label': 'Total number of cases by date', 'value': 'TOT'},
                    {'label': 'State wise cases', 'value': 'STATE'},
                    {'label': 'Age wise cases', 'value': 'AGE'},
                    {'label': 'Case emergence based on state', 'value': 'HIST'},
                    {'label': 'Patient current status', 'value': 'STATUS'}
                ],
                value='TRANS'
            )  
        ]),
        
        html.Div(style={
            'backgroundColor': 'white',
            'color': 'black',
            'margin': '5%'
            },
            children=[
                html.Div(id='graph')    
            ]),
    ])
])

@app.callback(
    Output(component_id='graph', component_property='children'),
    [Input(component_id='drop-down', component_property='value')]
)
def display_chart(data):
    if data == 'TRANS':
        return transmission_graph
    elif data == 'TOT':
        return total_cases_graph
    elif data == 'STATE':
        return statewise_graph
    elif data == 'AGE':
        return agewise_graph
    elif data == 'HIST':
        return case_history_graph
    elif data == 'STATUS':
        return patient_status_graph

if __name__ == '__main__':
    app.run_server(debug=False)