# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import time

# Read the airline data into pandas dataframe
start = time.time()
spacex_df = pd.read_csv("spacex_launch_dash.csv")
end = time.time()

print(f"File with {round(spacex_df.memory_usage(index=True, deep=True).sum()/1e6, 2)} Mb \
downloaded in {round(end-start, 3)}s!")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# print(spacex_df['class'].tail())
# print(spacex_df.dtypes)
# filtered_df = spacex_df[spacex_df['class']==1].groupby(['Launch Site'], as_index=False)# .mean()
# print(filtered_df)

# Create a dash application
app = dash.Dash(__name__)
# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True 

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#0F52BA',  # 503D36
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                # Cape Canaveral Space Launch Complex 40 VAFB SLC 4E, 
                                # Vandenberg Air Force Base Space Launch Complex 4E (SLC-4E),
                                # Kennedy Space Center Launch Complex 39A KSC LC 39A
                                            options=[{'label': 'All Sites', 'value': 'ALL'},
                                                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):", style={'font-size': 30}),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000,
                                step=1000, value=[1000, 9000],
                                marks={n: n for n in range(0, 11000, 1000)}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df['class']==1].groupby(['Launch Site'], as_index=False).sum()
        fig = px.pie(filtered_df, values='class', names='Launch Site', 
            title='Total Success Launches By Site')
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        counts = filtered_df['class'].value_counts()
        site_df = filtered_df.groupby('class').count().reset_index()
        # print(site_df)

        fig = px.pie(site_df, values='Mission Outcome', names='class', 
            title=f'Total Success Launches for site {entered_site}')      

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart','figure'),
             [Input('site-dropdown', 'value'), 
             Input('payload-slider', 'value')])

def draw_scatter_plot(site, payload):
    if site == 'ALL':
        filtered_df = spacex_df[spacex_df["Payload Mass (kg)"].between(payload[0],payload[1])]
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
         color="Booster Version Category", symbol="Booster Version Category")

    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==site]
        filtered_df = filtered_df[filtered_df["Payload Mass (kg)"].between(payload[0],payload[1])]
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
        color="Booster Version Category", symbol="Booster Version Category")
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
