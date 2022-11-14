from dash import Dash, dcc, html

from dash.dependencies import Input, Output

app = Dash(__name__)
server = app.server
DATA_SOURCE = ''
app.layout = html.Div([
    # Title
    html.H1('Welcome to Trading Algorithm Testbench'),
    # Data Source
    html.Div(
        [
            html.Tbody('Please select data source'),
            dcc.Dropdown(['Yahoo', 'IBKR'], 'Yahoo', id='data_source', clearable=False)
        ],
        style={'width': '20%', 'justify-content': 'left'}
    ),
    html.Div(id='disp_data_source')
],
)


@app.callback(
    Output('disp_data_source', 'children'),
    Input('data_source', 'value')
)
def update_output(value):
    global DATA_SOURCE
    DATA_SOURCE = value
    return f'You have selected {value}'


if __name__ == '__main__':
    app.run_server(debug=True)
