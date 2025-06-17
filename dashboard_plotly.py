import pandas as pd
from dash import Dash, dcc, html, dash_table, Output, Input
import plotly.graph_objects as go

# Carregar os dados
df = pd.read_csv("carregamentos.csv", sep=';', decimal=',')
for col in ['mm_4_75', 'mm_2', 'mm_1', 'fundo', 'peso_massa', 'mm_4_75_perc', 'mm_2_perc', 'mm_1_perc', 'fundo_perc', 'ton']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['granulos_por_tonelada'] = df['mm_2'] / (df['ton'] / 1000)

# Agrupamentos
fundo_produto = df.groupby('produto')['fundo_perc'].mean().reset_index()
fundo_box = df.groupby('box_consumo')['fundo_perc'].mean().reset_index()
granulos_prod_box = df.groupby(['produto', 'box_consumo'])['mm_2_perc'].mean().reset_index()
granulos_ton_produto = df.groupby('produto')['granulos_por_tonelada'].mean().reset_index()
eficiencia_maquinas = df.groupby('linha')[['mm_2_perc', 'fundo_perc']].mean().reset_index()
fundo_turno = df.groupby('turno')['fundo_perc'].mean().reset_index()
coletor_stats = df.groupby('linha')[['mm_4_75', 'mm_2', 'mm_1', 'fundo']].mean().reset_index()

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Img(src='assets/logo.png', style={'height': '80px', 'marginRight': '20px'}),
        html.H1("Fertalvo - Análise de Produção - Carregamento", style={'color': '#2c3e50', 'margin': '0', 'paddingTop': '20px'})
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'marginBottom': '10px'
    }),

    html.Div([
        dcc.Tabs(id='tabs-menu', value='tab1', children=[
            dcc.Tab(label='🌾 % Fundo por Produto', value='tab1'),
            dcc.Tab(label='🏭 % Fundo por Box', value='tab2'),
            dcc.Tab(label='📦 % Grânulos por Produto e Box', value='tab3'),
            dcc.Tab(label='🧱 Grânulos por Tonelada', value='tab4'),
            dcc.Tab(label='⚙️ Eficiência por Linha', value='tab5'),
            dcc.Tab(label='🕒 Fundo por Turno', value='tab6'),
            dcc.Tab(label='👷 Médias por Coletor', value='tab7'),
        ], style={
            'position': 'sticky',
            'top': '0',
            'backgroundColor': '#dfe6e9',
            'zIndex': '1000',
            'boxShadow': '0px 2px 5px gray'
        })
    ]),

    html.Div(id='conteudo-tabs', style={
        'maxHeight': '600px',
        'overflowY': 'auto',
        'padding': '10px'
    })
])

@app.callback(
    Output('conteudo-tabs', 'children'),
    Input('tabs-menu', 'value')
)
def render_content(tab):
    layout_style = {'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around'}
    colors = ['#e74c3c', '#3498db', '#f1c40f', '#2ecc71', '#9b59b6', '#e67e22', '#1abc9c', '#e84393']

    if tab == 'tab1':
        fig = go.Figure(data=[go.Bar(
            x=fundo_produto['produto'],
            y=fundo_produto['fundo_perc'],
            marker_color=fundo_produto['fundo_perc'],
            marker_colorscale='Viridis'
        )])
        fig.update_layout(title='% Fundo por Produto', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        tabela = dash_table.DataTable(
            data=fundo_produto.to_dict('records'),
            columns=[{"name": i, "id": i} for i in fundo_produto.columns],
            style_table={'overflowX': 'auto'},
        )

    elif tab == 'tab2':
        fig = go.Figure(data=[go.Bar(
            x=fundo_box['box_consumo'],
            y=fundo_box['fundo_perc'],
            marker_color=fundo_box['fundo_perc'],
            marker_colorscale='Plasma'
        )])
        fig.update_layout(title='% Fundo por Box', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        tabela = dash_table.DataTable(
            data=fundo_box.to_dict('records'),
            columns=[{"name": i, "id": i} for i in fundo_box.columns],
            style_table={'overflowX': 'auto'},
        )

    elif tab == 'tab3':
        fig = go.Figure()
        for idx, box in enumerate(granulos_prod_box['box_consumo'].unique()):
            df_box = granulos_prod_box[granulos_prod_box['box_consumo'] == box]
            fig.add_trace(go.Bar(
                x=df_box['produto'],
                y=df_box['mm_2_perc'],
                name=f'Box {box}',
                marker_color=colors[idx % len(colors)]
            ))
        fig.update_layout(
            title='Grânulos 2mm por Produto e Box',
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        tabela = dash_table.DataTable(
            data=granulos_prod_box.to_dict('records'),
            columns=[{"name": i, "id": i} for i in granulos_prod_box.columns],
            style_table={'overflowX': 'auto'},
        )

    elif tab == 'tab4':
        fig = go.Figure(data=[go.Bar(
            x=granulos_ton_produto['produto'],
            y=granulos_ton_produto['granulos_por_tonelada'],
            marker_colorscale='Cividis'
        )])
        fig.update_layout(title='Grânulos por Tonelada', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        tabela = dash_table.DataTable(
            data=granulos_ton_produto.to_dict('records'),
            columns=[{"name": i, "id": i} for i in granulos_ton_produto.columns],
            style_table={'overflowX': 'auto'},
        )

    elif tab == 'tab5':
        fig = go.Figure(data=[
            go.Bar(x=eficiencia_maquinas['linha'], y=eficiencia_maquinas['mm_2_perc'], name='mm_2_perc', marker_color='green'),
            go.Bar(x=eficiencia_maquinas['linha'], y=eficiencia_maquinas['fundo_perc'], name='fundo_perc', marker_color='orange')
        ])
        fig.update_layout(barmode='group', title='Eficiência por Linha', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        tabela = dash_table.DataTable(
            data=eficiencia_maquinas.to_dict('records'),
            columns=[{"name": i, "id": i} for i in eficiencia_maquinas.columns],
            style_table={'overflowX': 'auto'},
        )

    elif tab == 'tab6':
        fig = go.Figure(data=[go.Pie(labels=fundo_turno['turno'], values=fundo_turno['fundo_perc'], hole=0.3)])
        fig.update_layout(title='Fundo por Turno', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        tabela = dash_table.DataTable(
            data=fundo_turno.to_dict('records'),
            columns=[{"name": i, "id": i} for i in fundo_turno.columns],
            style_table={'overflowX': 'auto'},
        )

    elif tab == 'tab7':
        fig = go.Figure()
        for coluna in ['mm_4_75', 'mm_2', 'mm_1', 'fundo']:
            fig.add_trace(go.Bar(x=coletor_stats['linha'], y=coletor_stats[coluna], name=coluna))
        fig.update_layout(barmode='group', title='Médias por Coletor', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        tabela = dash_table.DataTable(
            data=coletor_stats.to_dict('records'),
            columns=[{"name": i, "id": i} for i in coletor_stats.columns],
            style_table={'overflowX': 'auto'},
        )

    return html.Div([
        html.Div(tabela, style={'width': '45%'}),
        html.Div(dcc.Graph(figure=fig), style={'width': '50%'})
    ], style=layout_style)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
