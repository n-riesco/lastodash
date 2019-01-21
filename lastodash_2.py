import argparse
import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

import lasio


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


def generate_frontpage():
    lf = lasio.read(lasfile)

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

        
if __name__ == '__main__':
    app.layout = html.Div(id='frontpage', className='page',
                          children=generate_frontpage())
    app.run_server(debug=debug)
