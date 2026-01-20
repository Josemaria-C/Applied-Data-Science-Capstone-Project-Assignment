# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For ALL sites: Count successful launches per site (class=1 means success)
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        
        plot_df = pd.DataFrame({
            'Launch Site': success_counts.index,
            'Success Count': success_counts.values
        })
        
        fig = px.pie(
            plot_df,
            values='Success Count',
            names='Launch Site',
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # For specific site: Show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count success (1) vs failure (0)
        outcome_counts = filtered_df['class'].value_counts().sort_index()
        
        # Create labels
        labels = ['Failure', 'Success'] if 0 in outcome_counts.index else ['Success']
        
        fig = px.pie(
            values=outcome_counts.values,
            names=labels,
            title=f'Success vs Failure for {entered_site}'
        )
        return fig


# TASK 4: Callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    # First filter by payload range (applies to both ALL and specific sites)
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Then filter by site if not ALL
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs. Launch Outcome for {entered_site if entered_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
        hover_data=['Launch Site', 'Payload Mass (kg)']
    )
    
    # Customize y-axis to show 0 and 1 clearly
    fig.update_yaxes(tickvals=[0, 1], ticktext=['Failure', 'Success'])
    
    return fig


# Run the app - FIXED FOR DASH 2.0+
if __name__ == '__main__':
    # Use app.run() instead of app.run_server() for Dash 2.0+
    app.run(debug=True, host='0.0.0.0', port=8050)