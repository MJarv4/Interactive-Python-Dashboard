import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.express as px

# Create dash app and clear the layout
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Read data from the airline, data was provided through IBM via the coursera IBM professional data analyst course
flight_data = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv',
    encoding="ISO-8859-1",
    dtype={'Div1Airport': str, 'Div1TailNum': str,
           'Div2Airport': str, 'Div2TailNum': str})

# Years of data being accessed
years = [i for i in range(2005, 2021)]

# Yearly airline performance report computation
def performance(df):
    # Reading data from the source for each map-type
    # Barchart data including cancellations by month
    barchart_data = df.groupby(['Month', 'CancellationCode'])['Flights'].sum().reset_index()
    # Line chart data for airtime by airline and month
    linechart_data = df.groupby(['Month', 'Reporting_Airline'])['AirTime'].mean().reset_index()
    # Data on diverted landings
    diversion_data = df[df['DivAirportLandings'] != 0.0]
    # Map chart Data including location flights left from
    mapchart_data = df.groupby(['OriginState'])['Flights'].sum().reset_index()
    # Tree map data of flight destinations
    treemap_data = df.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()
    return barchart_data, linechart_data, diversion_data, mapchart_data, treemap_data

# Delay reports for airlines by year
def delays(df):
    # delay averages
    # carrier delays by airline
    carrier = df.groupby(['Month', 'Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    # Weather delays by airline reported
    weather = df.groupby(['Month', 'Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    # NAS delays by reported airline
    NAS = df.groupby(['Month', 'Reporting_Airline'])['NASDelay'].mean().reset_index()
    # Security delays by reporting airline
    security = df.groupby(['Month', 'Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    # In flight delays by airline/aircraft
    delay = df.groupby(['Month', 'Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return carrier, weather, NAS, security, delay


# Application layout
app.layout = html.Div(children=[html.H1(
    # Dashboard Title
    'US Domestic Airline Flights Performance',
    style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    html.Div([
        html.Div([
            html.Div(
                [
                    html.H2('Report Type:', style={'margin-right': '2em'}),
                ]
            ),
            dcc.Dropdown(id='input-type',
                         options=[
                             # dropdown tab titles
                             {'label': 'Yearly Airline Performance Report', 'value': 'OPT1'},
                             {'label': 'Yearly Airline Delay Report', 'value': 'OPT2'}
                         ],
                         placeholder='Select a report type',
                         style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'})

        ], style={'display': 'flex'}),

        html.Div([
            # Division to add dropdown for choosing year
            html.Div(
                [
                    html.H2('Choose Year:', style={'margin-right': '2em'})
                ]
            ),
            dcc.Dropdown(id='input-year',
                         # Update dropdown values
                         options=[{'label': i, 'value': i} for i in years],
                         placeholder="Select a year",
                         style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}),
        ], style={'display': 'flex'}),
    ]),

    # Add completed graphs and empty divisions
    html.Div([], id='plot1'),

    html.Div([
        html.Div([], id='plot2'),
        html.Div([], id='plot3')
    ], style={'display': 'flex'}),

    html.Div([
        html.Div([], id='plot4'),
        html.Div([], id='plot5')
    ], style={'display': 'flex'}),
])


# Callback function
@app.callback([Output(component_id='plot1', component_property='children'),
               Output(component_id='plot2', component_property='children'),
               Output(component_id='plot3', component_property='children'),
               Output(component_id='plot4', component_property='children'),
               Output(component_id='plot5', component_property='children')],
              [Input(component_id='input-type', component_property='value'),
               Input(component_id='input-year', component_property='value')],
              [State("plot1", 'children'), State("plot2", "children"),
               State("plot3", "children"), State("plot4", "children"),
               State("plot5", "children")
               ])
# Callback function/return graph
def make_graph(chart, year, children1, children2, c3, c4, c5):
    # Select data
    df = flight_data[flight_data['Year'] == int(year)]

    if chart == 'OPT1':
        # Compute required information for creating graph from the data
        barchart_data, linechart_data, diversion_data, mapchart_data, treemap_data = performance(df)

        # Cancellation category barchart
        barchart = px.bar(barchart_data, x='Month', y='Flights', color='CancellationCode',
                         title='Monthly Flight Cancellation')

        # Average flight time by reporting airline
        linechart = px.line(linechart_data, x='Month', y='AirTime', color='Reporting_Airline',
                           title='Average monthly flight time (minutes) by airline')

        # Diversion data for flights by airline reporting
        piechart = px.pie(diversion_data, values='Flights', names='Reporting_Airline',
                         title='% of flights by reporting airline')

        # Choropleth map of flights by origin state
        mapchart = px.choropleth(mapchart_data,  # Input data
                                locations='OriginState',
                                color='Flights',
                                hover_data=['OriginState', 'Flights'],
                                locationmode='USA-states',  # Set to plot as US States
                                color_continuous_scale='GnBu',
                                range_color=[0, mapchart_data['Flights'].max()])
        mapchart.update_layout(
            title_text='Number of flights from origin state',
            geo_scope='usa')  # USA plot, not global

        # Treemap of flight destination by reporting airline
        treemap = px.treemap(treemap_data, path=['DestState', 'Reporting_Airline'], values='Flights',
                              color='Flights', color_continuous_scale='YlGnBu',
                              title='Flight count by airline to destination state')

        return [dcc.Graph(figure=treemap),
                dcc.Graph(figure=piechart),
                dcc.Graph(figure=mapchart),
                dcc.Graph(figure=barchart),
                dcc.Graph(figure=linechart)
                ]
    else:
        carrier, weather, NAS, security, delay = delays(df)

        # Give parameters to the graphs/create them
        # Line graph of carrier delay time
        carriergraph = px.line(carrier, x='Month', y='CarrierDelay', color='Reporting_Airline',
                              title='Average carrrier delay time (minutes) by airline')
        # Line graph of weather delay time
        weathergraph = px.line(weather, x='Month', y='WeatherDelay', color='Reporting_Airline',
                              title='Average weather delay time (minutes) by airline')
        # Line graph of NAS delay time
        NASgraph = px.line(NAS, x='Month', y='NASDelay', color='Reporting_Airline',
                          title='Average NAS delay time (minutes) by airline')
        # Line graph of security delay time
        securitygraph = px.line(security, x='Month', y='SecurityDelay', color='Reporting_Airline',
                          title='Average security delay time (minutes) by airline')
        # Line graph of flight delay time
        delaygraph = px.line(delay, x='Month', y='LateAircraftDelay', color='Reporting_Airline',
                           title='Average late aircraft delay time (minutes) by airline')

        return [dcc.Graph(figure = carriergraph),
                dcc.Graph(figure = weathergraph),
                dcc.Graph(figure = NASgraph),
                dcc.Graph(figure = securitygraph),
                dcc.Graph(figure = delaygraph)]


# Run the app
if __name__ == '__main__':
    app.run_server()