# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                         options=[
                                             {'label': 'All Sites', 'value': 'ALL'},
                                             {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                             {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                             {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                             {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                         ],
                                         value='ALL',
                                         placeholder="Select a Launch Site",
                                         searchable=True
                                         ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                 min=0,
                                                 max=10000,
                                                 step=1000,
                                                 value=[min_payload, max_payload],
                                                 marks={i: str(i) for i in range(0, 10001, 1000)},
                                                 pushable=True
                                                 ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Pie chart: Total de éxitos por sitio de lanzamiento
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total de lanzamientos exitosos por sitio'
        )
        return fig
    else:
        # Pie chart: Éxitos vs Fallos para el sitio seleccionado
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['Outcome', 'Count']
        counts['Outcome'] = counts['Outcome'].replace({1: 'Success', 0: 'Failed'})
        fig = px.pie(
            counts, 
            values='Count', 
            names='Outcome', 
            title=f'Lanzamientos exitosos vs fallidos en {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, payload_range):
    # Filtra por rango de carga útil
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    # Filtra por sitio si no es 'ALL'
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Payload vs Success para {entered_site}'
    else:
        title = 'Payload vs Success para todos los sitios'

    # Gráfico de dispersión con Booster Version Category como color
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Éxito', 'Payload Mass (kg)': 'Carga útil (kg)'},
        hover_data=['Booster Version']
    )
    return fig
# Run the app
if __name__ == '__main__':
    app.run()
