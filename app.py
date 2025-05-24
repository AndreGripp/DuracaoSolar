import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np
from math import cos, sin, acos, radians, tan

app = dash.Dash(__name__)
server = app.server

# Layout do app
app.layout = html.Div([
    html.H1("☀️ Duração da Luz Solar por Latitude", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        # Controle deslizante
        html.Div([
            html.Label("Selecione a latitude:", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='latitude-slider',
                min=-90,
                max=90,
                step=1,
                value=0,
                marks={i: f'{i}°' for i in range(-90, 91, 15)},
            )
        ], style={'width': '80%', 'margin': '20px auto'}),
        
        # Mapa com linha de latitude
        dcc.Graph(id='world-map', style={'height': '400px'}),
        
        # Gráfico de duração
        dcc.Graph(id='sunlight-graph', style={'height': '400px'})
    ])
])

# Função para criar o mapa com linha de latitude
def criar_mapa(latitude):
    fig = go.Figure()
    
    # Linha de latitude (vermelha)
    fig.add_trace(go.Scattergeo(
        lon = np.arange(-180, 181, 1),
        lat = [latitude] * 361,
        mode = 'lines',
        line = dict(width=2, color='red'),
        name = f'Latitude {latitude}°'
    ))
    
    # Configurações do mapa
    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        landcolor="lightgray",
        oceancolor="azure",
        showocean=True
    )
    
    fig.update_layout(
        title_text=f'Linha de Latitude: {latitude}°',
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    return fig

# Função para calcular a duração do dia
def calcular_horas_luz(latitude_graus, dia_ano):
    # Passo 1: Converter latitude para radianos
    latitude = radians(latitude_graus)
    
    # Passo 2: Calcular Raio
    Raio = cos(latitude)
    
    # Passo 3: Calcular Declin
    Declin = radians(23.45*sin((dia_ano-81)*2*pi/365))
    
    # Passo 4: Calcular Corda
    Corda = sin(latitude) * tan(Declin)
    Corda = max(min(Corda, 1), -1)  # Limitando entre -1 e 1    
    
    # Passo 5: Calcular horas de luz
    razao = Corda / Raio
    
    if razao <= -1:
        HLuz = 0
    elif razao >= 1:
        HLuz = 24
    else:
        HLuz = 24 * (1 - (2 * acos(razao) / (2 * pi)))
    
    return HLuz

# Callbacks
@callback(
    [Output('world-map', 'figure'),
     Output('sunlight-graph', 'figure')],
    [Input('latitude-slider', 'value')]
)
def update_graph(latitude):
    # Atualiza o mapa
    mapa = criar_mapa(latitude)
    
    # Atualiza o gráfico de duração
    dias = np.arange(1, 366)
    horas_luz = [calcular_horas_luz(latitude, dia) for dia in dias]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dias,
        y=horas_luz,
        mode='lines',
        line=dict(color='orange', width=3),
        name='Horas de luz solar'
    ))
    
    fig.update_layout(
        title=f'Duração Diária da Luz Solar (Latitude: {latitude}°)',
        xaxis_title='Dia do Ano',
        yaxis_title='Horas de Luz Solar',
        yaxis_range=[0, 25],
        template='plotly_white'
    )
    
    # Adiciona marcações de eventos astronômicos
    for dia, nome in [(80, 'Equinócio Março'), (172, 'Solstício Junho'), 
                     (266, 'Equinócio Setembro'), (356, 'Solstício Dezembro')]:
        fig.add_vline(
            x=dia, line_width=1, line_dash="dash",
            annotation_text=nome, annotation_position="top right"
        )
    
    return mapa, fig
    
if __name__ == '__main__':
    app.run(debug=True)
