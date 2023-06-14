import random
import gunicorn
from dash import dash, html, callback_context
from dash.dependencies import Input, Output, State

# List of Bingo items
bingo_items = ['talk about v6, v7, v18', 'Smoothie', 'ALIENS', 
               'my last question is...', 'Copyright', 'Midjourney Movies, when?', 
               ' "100x better" ',  'someone asking for a job',  'connection problems', 
               'discord breaking', 'in/outpainting', 'flowers and bees',  
               '"why no NSFW"', '"why word X banned?"', 'How did u make Midjourney, exactly?', 
               'cats per seconds',  '"stable characters, when?"', 'post-scarcity talk', 
               'long ADHD ramble', 'API!?!',  'vehicle for imagination',  
               'Ancient Chinese Philosophy', 'Dream Game Engine', 'Free tier', 
               '"Can you hear me?"', 'Shout Out', 'Self Promotion', 'AI Bias', 
               '3D, when?', '"not commercial"', '100K/month guy',  'liquid imagination', 
               'the three pillars', '*pet noises*', 'more visual exploration in the next 10 years', 
               '1% bad actors is still a lot', 'smol training data', 'MJ should not be like social media', 
               '*David giggles*', 'cat bois']

# Initialize the app
app = dash.Dash(__name__)

# Reference the underlying flask app (Used by gunicorn webserver for deployment)
server = app.server

# Define the layout of the app
app.layout = html.Div([
    html.H1('Midjourney Office Hours Bingo', style={'font-size': '36px', 'color':'white'}),
    html.Div(id='bingo-message', style={'font-size': '24px', 'color': '#47958A', 'font-style': 'bold'}),
    html.Button('Randomize Board', id='button-randomize', style={
        'font-size': '24px', 
        'background-color': '#1F1E4D', 
        'color': 'white'
        }),
    html.Table([
        html.Tr([
            html.Td(html.Div(item), id=f'cell-{i}-{j}', style={
                'color':'white',
                'border': '1px solid black',
                'height': '120px',
                'width': '120px',
                'text-align': 'center',
                'background-color': '#010612',
                'font-size': '20px',
                'font-family': 'Arial'
            }, n_clicks=0)
            for j, item in enumerate([''] * 5)
        ])
        for i in range(5)
    ]),
    html.Div('Created by Tina Tiresome with much help from ChatGTP and #vc-chat', style={'font-size': '14px', 'font-style': 'italic', 'color':'white'})
])


# Define the callback to randomize the board when the button is clicked
@app.callback(
    [Output(f'cell-{i}-{j}', 'children') for i in range(5) for j in range(5)],
    [Input('button-randomize', 'n_clicks')],
)
def randomize_board(n_clicks):
    # Shuffle the Bingo items and return the first 25 of them
    selected_items = random.sample(bingo_items, 25)
    return [[item] for item in selected_items]

def get_styles(n_clicks, randomize_clicks, style):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    # Reset the background color when the button is clicked
    if triggered_input == 'button-randomize':
        style['background-color'] = '#010612'
    # Change the background color to a nice color when the cell is clicked
    elif n_clicks % 2 == 1:
        style['background-color'] = '#75014B'
    else:
        style['background-color'] = '#010612'
    return style

def check_bingo(matrix):
    # Check rows
    for row in matrix:
        if all(cell == 1 for cell in row):
            return True

    # Check columns
    for col in range(5):
        if all(matrix[row][col] == 1 for row in range(5)):
            return True

    # Check diagonals
    if all(matrix[i][i] == 1 for i in range(5)):
        return True
    if all(matrix[i][4 - i] == 1 for i in range(5)):
        return True

    return False

 #Handle Clicks
@app.callback(
    [
        Output(f'cell-{i}-{j}', 'style') for i in range(5) for j in range(5)
    ] +
    [
        Output(f'cell-{i}-{j}', 'n_clicks') for i in range(5) for j in range(5)
    ] +
    [
        Output('bingo-message', 'children')
    ],
    [
        Input(f'cell-{i}-{j}', 'n_clicks') for i in range(5) for j in range(5)
    ] +
    [
        Input('button-randomize', 'n_clicks')
    ],
    [
        State(f'cell-{i}-{j}', 'style') for i in range(5) for j in range(5)
    ]
)
def handle_clicks(*args):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    cell_clicks = args[:25]
    randomize_clicks = args[25]
    cell_styles = args[26:]

   
    output_styles = []
    output_n_clicks = []

    # Update styles and n_clicks based on the triggered input
    for idx, (clicks, style) in enumerate(zip(cell_clicks, cell_styles)):
        if triggered_input == f"cell-{idx // 5}-{idx % 5}":
            if style["background-color"] == "#010612":
                style["background-color"] = "#75014B" #nice color
                output_n_clicks.append(1)
            else:
                style["background-color"] = "#010612"
                output_n_clicks.append(0)
        elif triggered_input == "button-randomize":
            style["background-color"] = "#010612"
            output_n_clicks.append(0)
        else:
            output_n_clicks.append(clicks)

        output_styles.append(style)

    clicks_matrix = [output_n_clicks[i * 5: (i + 1) * 5] for i in range(5)]
    for i in range(5):
        for j in range(5):
            clicks_matrix[i][j] = 1 if cell_styles[i * 5 + j]["background-color"] == "#75014B" else 0

    bingo_message = "BINGO! BINGO! BINGO! BINGO! BINGO!" if check_bingo(clicks_matrix) else ""

    if triggered_input == "button-randomize":
        bingo_message = ""

    return output_styles + output_n_clicks + [bingo_message]

# Start the Dash app server
if __name__ == "__main__": app.run_server(debug=False, host='0.0.0.0', port=8050)
