import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np
from math import cos, sin, tan, acos, radians, pi, fabs

app = dash.Dash(__name__)
server = app.server  # Necessário para o deploy no Render

# Layout do app
app.layout = html.Div([
    html.H1("☀️ Duração da Luz Solar por Latitude", 
            style={'textAlign': 'center', 'color': '#2c3e50'}),
    
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
    
    dcc.Graph(id='world-map'),
    dcc.Graph(id='sunlight-graph')
])

# Função para criar o mapa
def criar_mapa(latitude):
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon = np.arange(-180, 181, 1),
        lat = [latitude] * 361,
        mode = 'lines',
        line = dict(width=2, color='red')
    ))
    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        landcolor="lightgray",
        oceancolor="azure",
	showocean=True
    )
    fig.update_layout(title_text=f'Linha de Latitude: {latitude}°')
    return fig

# SUA FÓRMULA PERSONALIZADA
def calcular_horas_luz(latitude_graus, dia_ano):
    # Passo 1: Converter latitude para radianos
    latitude = radians(latitude_graus)
    
    # Passo 2: Calcular Raio
    Raio = cos(latitude)
    
    # Passo 3: Calcular Declinação
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


# Callback
@callback(
    [Output('world-map', 'figure'),
     Output('sunlight-graph', 'figure')],
    [Input('latitude-slider', 'value')]
)
def update_graph(latitude):
    # Mapa (mantido igual)
    mapa = criar_mapa(latitude)
    
    # Gráfico 
    dias = np.arange(1, 366)
    horas_luz = [calcular_horas_luz(latitude, dia) for dia in dias]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dias,
        y=horas_luz,
        mode='lines',
        line=dict(color='orange', width=3)
    ))
    
    # Configurações do gráfico (mantidas)
    fig.update_layout(
        title=f'Duração Diária da Luz Solar (Latitude: {latitude}°)',
        xaxis_title='Dia do Ano',
        yaxis_title='Horas de Luz Solar',
        yaxis_range=[0, 25],
        template='plotly_white'
    )
    
    # Linhas para eventos astronômicos (mantidas)
    eventos = {
        'Equinócio Março': 81,
        'Solstício Junho': 172.5,
        'Equinócio Setembro': 264,
        'Solstício Dezembro': 355
    }
    
    for nome, dia in eventos.items():
        fig.add_vline(
            x=dia, line_width=1, line_dash="dash",
            annotation_text=nome, annotation_position="top right"
        )
    
    return mapa, fig

if __name__ == '__main__':
    app.run(debug=True)
