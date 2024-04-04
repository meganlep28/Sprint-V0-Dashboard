#loading cleaned data
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
df = pd.read_csv("dataFIPS.csv", header = 0, dtype={"5-digit FIPS Code": str} )

#loading regions data to merge
regions = pd.read_csv("us census bureau regions and divisions.csv")
regions

#rename the regions State Code col to State Abbreviation to match grouped df
regions.rename(columns = {'State Code':'State Abbreviation'}, inplace=True) #need to have inplace otherwise need to create a new object or merge wont work

###loading JSON file that has the geometry information for US counties

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

counties["features"][0]

#####getting the average PHS by county##### 

#create new df that's grouped by county
grouped = df.groupby(['5-digit FIPS Code', 'Name', 'State Abbreviation'], as_index=False).mean(numeric_only=True) #need the as_index=F bc groupby column gets put on diff col as index
#display(grouped)
#avg all values 
display(grouped)

groupedRace = df.groupby(['5-digit FIPS Code', 'Name', 'State Abbreviation', 'Race'], as_index=False).mean(numeric_only=True) #need the as_index=F bc groupby column gets put on diff col as index
#display(grouped)
#avg all values 
display(groupedRace)

merged = pd.merge(grouped, regions, on="State Abbreviation")
merged


from dash import Dash, dcc, html, Input, Output, State, callback

stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app

server = app.server


app.layout = html.Div([
    html.Div([
        html.Div([dcc.Dropdown(
                merged['Region'].unique(),
                'West', #default
                id='drop_select_region'
            )
        ])
    ]),
#put submit button here
    html.Div([ 
        html.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='container-button-basic',
             children='Select a region and press submit') #puts text under submit button intially 
    ]),

#graph
    html.Div([dcc.Graph(id='region-chloro')])
])

@callback(
    Output('region-chloro', 'figure'),
    Input('drop_select_region', 'value'), #submit-val is when you hit submit button
    #State('drop_select_region', 'value'), #id needs to be what user chooses
    #prevent_initial_call=True
    #Output('region-chloro', 'figure'),
)
def update_output(region_selected):
    filtered_region = merged[merged.Region == region_selected] #filter data based on region selected --> taken from multiple inputs class10

    #create fig
    fig = px.choropleth(filtered_region, geojson=counties, locations='5-digit FIPS Code', color='Preventable Hospital Stay Value',
                        color_continuous_scale="Viridis",
                           range_color=(0, 10000),
                           scope="usa",
                           labels={'Preventable Hospital Stay Value':'Avg PHS rate'},
                           title = "Average PHS rate by County in Selected Region"
                          )
    return fig

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)

