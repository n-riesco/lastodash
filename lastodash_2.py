import argparse
import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

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

for curve in lf.curves:
    print(curve.mnemonic)
    

def generate_frontpage():

    filename = os.path.basename(lasfile.name)
    
    frontpage = []
    
    # get the header
    frontpage.append(
        html.Div(id='las-header', children=[
            html.H1("LAS Report"),
            html.Div([
                html.B(id='las-filename',
                       children=filename),
                html.Span('({0})'.format(lf.version['VERS'].descr
                                         if 'VERS' in lf.version
                                         else 'Unknown version'))
            ])
        ])
    )
    
    return frontpage


def generate_curves():
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
                              shared_yaxes=True)

    for i in range(len(plots)):
        for column in plots[i]: 
            fig.append_trace(go.Scatter(
                x=lf.curves[column].data,
                y=lf.curves[yvals].data,
                name=column,
                line={'width': 1}
            ), row=1, col=i+1)
            fig['layout']['xaxis{}'.format(i+1)].update(
                showgrid=False,
                zeroline=False,
                type='log' if column in plots[1] else 'linear'
            )

    fig['layout'].update(
        height=800,
        hovermode='y'
    )

    fig['data'][1]['xaxis'] = 'x6'
    fig['data'][6]['xaxis'] = 'x7'
    fig['data'][8]['xaxis'] = 'x8'
    fig['data'][11]['xaxis'] = 'x9'

    fig['layout']['xaxis6'] = dict(
        overlaying='x1',
        anchor='y',
        side='top'
    )

    fig['layout']['xaxis7'] = dict(
        overlaying='x2',
        anchor='y',
        side='top'
    )

    fig['layout']['xaxis8'] = dict(
        overlaying='x3',
        anchor='y',
        side='top'
    )

    fig['layout']['xaxis9'] = dict(
        overlaying='x5',
        anchor='y',
        side='top'
    )
        
    return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.layout = html.Div([
        html.Div(id='frontpage', className='page',
                 children=generate_frontpage()),
        html.Div(generate_curves())
    ])
    
    app.run_server(debug=debug)
