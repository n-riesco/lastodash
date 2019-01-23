import argparse
import os
import pandas
import dash
import dash_daq as daq
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import base64

from plotly import tools
import plotly.graph_objs as go

import lasio

import re

app = dash.Dash(__name__)

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch a Dash app to view a LAS log."
    )

    parser.add_argument(
        "lasfile",
        type=argparse.FileType(mode="r"),
        help="Log ASCII Standard (LAS) file"
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="enable debug mode"
    )

    args = parser.parse_args()

    return args.lasfile, args.debug


lasfile, debug = parse_args()
lf = lasio.read(lasfile)


def generate_frontpage():

    filename = os.path.basename(lasfile.name)
    
    frontpage = []
    
    # get the header
    frontpage.append(
        html.Div(id='las-header', children=[

            html.Img(
                id='las-logo',
                src='data:image/png;base64,{}'.format(
                    base64.b64encode(
                        open('assets/adnoc_logo.png', 'rb').read()
                    ).decode()
                )
            ), 

            html.Div(
                id='las-header-text',
                children=[
                    html.H1("LAS Report"),
                    html.Div(id='las-file-info', children=[
                        html.B(id='las-filename',
                               children=filename),
                        html.Span('({0})'.format(lf.version['VERS'].descr
                                                 if 'VERS' in lf.version
                                                 else 'Unknown version'))
                    ])
                ])
            ])
        )
    
    return frontpage


def generate_curves(
        height=1400, width=1000,
        bg_color='white',
        font_size=10
):
    # include one graph for all curves, since they have the same x axis
    yvals = 'DEPT'

    cols = list(lf.curves.keys())

    plots = []
    
    plots.append(['BTVPVS', 'DGRC'])
    plots.append(list(filter(
        lambda x: x == 'EWXT' or re.search(r'R[0-9][0-9]P', x),
        cols)
    ))
    plots.append(['ALCDLC', 'ALDCLC'])
    plots.append(['TNPS'])
    plots.append(['BTCSS', 'BTCS'])
    
    fig = tools.make_subplots(rows=1, cols=len(plots),
                              shared_yaxes=True,
                              horizontal_spacing=0)

    for i in range(len(plots)):
        for column in plots[i]: 
            fig.append_trace(go.Scatter(
                x=lf.curves[column].data,
                y=lf.curves[yvals].data,
                name=column,
                line={'width': 0.5,
                      'dash': 'dashdot' if column in plots[1] else 'solid'},
            ), row=1, col=i+1)
            fig['layout']['xaxis{}'.format(i+1)].update(
                title='{} ({})'.format(
                    lf.curves[plots[i][0]]['descr'],
                    lf.curves[plots[i][0]]['unit']
                ),
                type='log' if column in plots[1] else 'linear'
            )

    fig['data'][1]['xaxis'] = 'x6'
    fig['data'][6]['xaxis'] = 'x7'
    fig['data'][8]['xaxis'] = 'x8'
    fig['data'][11]['xaxis'] = 'x9'

    # DGRC on graph 1
    fig['layout']['xaxis6'] = dict(
        overlaying='x1',
        anchor='y',
        side='top',
        title='{} ({})'.format(
            lf.curves['DGRC']['descr'],
            lf.curves['DGRC']['unit']
        )
    )

    # EWXT on graph 2 
    fig['layout']['xaxis7'] = dict(
        overlaying='x2',
        anchor='y',
        side='top',
        title='{} ({})'.format(
            lf.curves['EWXT']['descr'],
            lf.curves['EWXT']['unit']
        )
    )

    # ALDCLC on graph 3
    fig['layout']['xaxis8'] = dict(
        overlaying='x3',
        anchor='y',
        side='top',
        title='{} ({})'.format(
            lf.curves['ALDCLC']['descr'],
            lf.curves['ALDCLC']['unit']
        )
    )

    # BTCS on graph 5
    fig['layout']['xaxis9'] = dict(
        overlaying='x5',
        anchor='y',
        side='top',
        title='{} ({})'.format(
            lf.curves['BTCS']['descr'],
            lf.curves['BTCS']['unit']
        )
    )

    # y axis title 
    fig['layout']['yaxis'].update(
        title='{} ({})'.format(
            lf.curves[yvals]['descr'],
            lf.curves[yvals]['unit']
        )
    )

    for axis in fig['layout']:
        if re.search(r'[xy]axis[0-9]*', axis):
            fig['layout'][axis].update(
                mirror='all',
                showline=True,
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=font_size
                ),
            )
    
    fig['layout'].update(
        height=height,
        width=width,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        hovermode='y'
    )

    return dcc.Graph(figure=fig)


def generate_table():
    cols = ['mnemonic', 'descr', 'unit', 'value']
    data = {
        lf.well[i]['mnemonic']: {
            col: lf.well[i][col]
            for col in cols
        }
        for i in range(len(lf.well))
    }

    df = pandas.DataFrame(
        data=data
    )

    df = df.transpose()
    df = df[cols]
    return dt.DataTable(
        id='table',
        sorting=True,
        filtering=True,
        row_deletable=True,
        style_cell={
            'padding': '5px',
            'width': 'auto',
            'textAlign': 'left'
        },
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows")
    )

    return html.Table(
        [html.Tr([
            html.Td([
                col.upper() if col is not 'descr'
                else 'description'.upper()
            ], className='col-name')
            for col in cols
        ])] + [
            html.Tr([
                html.Td([
                    lf.well[i][col]
                ], className='col-entry')
                for col in cols
            ])
            for i in range(len(lf.well))
        ])


app.layout = html.Div([
    html.Div(
        id='controls',
        children=[
            "Graph size", 
            daq.ToggleSwitch(
                id='graph-size',
                label=['web', 'print'],
                value=False
            ), 
            html.Button(
                "Print",
                id='las-print'
            ),
        ]
    ),
    
    html.Div(
        id='frontpage',
        className='page',
        children=generate_frontpage()
    ),

    html.Div(
        className='section-title',
        children="LAS well"
    ), 
    html.Div(
        id='las-table',
        className='page',
        children=generate_table()
    ),

    html.Div(
        className='section-title',
        children="LAS curves"
    ), 
    html.Div(
        id='las-curves',
        className='page',
        children=generate_curves()
    )
])


@app.callback(
    Output('las-curves', 'children'),
    [Input('graph-size', 'value')]
)
def graph_size(printsize):
    if(printsize):
        return generate_curves(2700, 2000, font_size=20)
    else:
        return generate_curves()


if __name__ == '__main__':
        
    app.run_server(debug=debug)
