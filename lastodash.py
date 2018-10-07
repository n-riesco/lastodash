#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright 2018 Nicolas Riesco
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

import lasio


def main():
    lasfile, debug = parse_args()

    app = dash.Dash(__name__)
    app.layout = build_layout(lasfile)
    app.run_server(debug=debug)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description='Launch a Dash app to view a LAS log.'
    )

    parser.add_argument(
        'lasfile',
        type=argparse.FileType(mode='r'),
        help='Log ASCII Standard (LAS) file'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='enable debug mode'
    )

    args = parser.parse_args()

    return args.lasfile, args.debug


def build_layout(lasfile):
    las = lasio.read(lasfile)

    return html.Div([
        html.H1('LAS Viewer'),
        build_section_version(las, lasfile),
        build_section_well(las),
        build_section_curves(las)
    ], className='las')


def build_section_version(las, lasfile):
    filename = lasfile.name

    description = (
        las.version['VERS'].descr
        if 'VERS' in las.version
        else 'unknown version'
    )

    return html.Div([
        html.H2('Section: version'),
        html.Table(html.Tr([
            html.Td(filename, className='las-version-filename'),
            html.Td(description, className='las-version-description')
        ]))
    ], className='las-version')


def build_section_well(las):
    return html.Div([
        html.H2('Section: well'),
        html.Table([
            build_section_well_entry(e) for e in las.well
        ])
    ], className='las-well')


def build_section_well_entry(entry):
    return html.Tr([
        html.Td([
            html.B(
                entry.descr,
                className='las-well-entry-description'
            ),
            html.Span(
                '[{0}]'.format(entry.unit) if entry.unit else '',
                className='las-well-entry-unit'
            ),
        ]),
        html.Td(
            entry.value,
            className='las-well-entry-value'
        )
    ], className='las-well-entry')


def build_section_curves(las):
    x = las.depth_ft
    xaxis = dict(
        title='depth [ft]'
    )

    line_black = dict(color='black', width=1)
    line_red = dict(color='red', width=1)
    line_green = dict(color='green', width=1)
    line_blue = dict(color='blue', width=1)
    line_magenta = dict(color='magenta', width=1)

    dash_black = dict(color='black', dash='dash', width=1)
    dash_red = dict(color='red', dash='dash', width=1)
    dash_green = dict(color='green', dash='dash', width=1)
    dash_blue = dict(color='blue', dash='dash', width=1)
    dash_magenta = dict(color='magenta', dash='dash', width=1)

    dot_black = dict(color='black', dash='dot', width=1)
    dot_red = dict(color='red', dash='dot', width=1)
    dot_green = dict(color='green', dash='dot', width=1)
    dot_blue = dict(color='blue', dash='dot', width=1)
    dot_magenta = dict(color='magenta', dash='dot', width=1)

    dashdot_black = dict(color='black', dash='dashdot', width=1)
    dashdot_red = dict(color='red', dash='dashdot', width=1)
    dashdot_green = dict(color='green', dash='dashdot', width=1)
    dashdot_blue = dict(color='blue', dash='dashdot', width=1)
    dashdot_magenta = dict(color='magenta', dash='dashdot', width=1)


    btvpvs_axis, btvpvs_trace = build_plot(
        las, 'BTVPVS', line=line_magenta, x=x, yaxis='y'
    )
    btvpvs_axis['side'] = 'right'
    btvpvs_axis['showgrid'] = False
    dgrc_axis, dgrc_trace = build_plot(
        las, 'DGRC', line=line_green, x=x, yaxis='y2'
    )
    dgr_graph = dcc.Graph(figure={
        'data': [
            btvpvs_trace,
            dgrc_trace
        ],
        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            xaxis=xaxis,
            yaxis=btvpvs_axis,
            yaxis2=dgrc_axis
        )
    }, id='las-curves-dgr')

    ewxt_axis, ewxt_trace = build_plot(
        las, 'EWXT', line=dashdot_magenta, x=x, yaxis='y'
    )
    ewxt_axis['type'] = 'log'
    ewxt_axis['side'] = 'right'
    ewxt_axis['showgrid'] = False
    r09p_axis, r09p_trace = build_plot(
        las, 'R09P', line=dashdot_green, x=x, yaxis='y2'
    )
    r15p_axis, r15p_trace = build_plot(
        las, 'R15P', line=line_black, x=x, yaxis='y2'
    )
    r27p_axis, r27p_trace = build_plot(
        las, 'R27P', line=dot_blue, x=x, yaxis='y2'
    )
    r39p_axis, r39p_trace = build_plot(
        las, 'R39P', line=dash_red, x=x, yaxis='y2'
    )
    rp_axis = dict(
        title='RxxP [ohmm]',
        type='log'
    )
    rp_graph = dcc.Graph(figure={
        'data': [
            ewxt_trace,
            r09p_trace,
            r15p_trace,
            r27p_trace,
            r39p_trace
        ],
        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            xaxis=xaxis,
            yaxis=ewxt_axis,
            yaxis2=rp_axis
        )
    }, id='las-curves-rp')

    aldclc_axis, aldclc_trace = build_plot(
        las, 'ALDCLC', line=dash_black, x=x, yaxis='y'
    )
    alcdlc_axis, alcdlc_trace = build_plot(
        las, 'ALCDLC', line=line_red, x=x, yaxis='y2'
    )
    alcdlc_axis['side'] = 'right'
    alcdlc_axis['showgrid'] = False
    ald_graph = dcc.Graph(figure={
        'data': [
            alcdlc_trace,
            aldclc_trace
        ],
        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            xaxis=xaxis,
            yaxis=aldclc_axis,
            yaxis2=alcdlc_axis
        )
    }, id='las-curves-ald')

    tnps_axis, tnps_trace = build_plot(
        las, 'TNPS', line=line_blue, x=x, yaxis='y'
    )
    ctn_graph = dcc.Graph(figure={
        'data': [
            tnps_trace
        ],
        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            xaxis=xaxis,
            yaxis=tnps_axis
        )
    }, id='las-curves-ctn')

    btcss_axis, btcss_trace = build_plot(
        las, 'BTCSS', line=line_magenta, x=x, yaxis='y'
    )
    btcs_axis, btcs_trace = build_plot(
        las, 'BTCS', line=line_green, x=x, yaxis='y2'
    )
    btcs_axis['side'] = 'right'
    btcs_axis['showgrid'] = False
    bat_graph = dcc.Graph(figure={
        'data': [
            btcss_trace,
            btcs_trace
        ],
        'layout': go.Layout(
            hovermode='x',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            xaxis=xaxis,
            yaxis=btcss_axis,
            yaxis2=btcs_axis
        )
    }, id='las-curves-bat')

    return html.Div([
        html.H2('Section: curves'),
        dgr_graph,
        rp_graph,
        ald_graph,
        ctn_graph,
        bat_graph
    ], className='las-curves')


def build_plot(las, key, **kwargs):
    axis = None
    trace = None

    try:
        curve = las.curves[key]
        data = curve.data
        unit = ' [{0}]'.format(curve.unit) if curve.unit != 'NONE' else ''
        descr = curve.descr

        axis = dict(
            title=key+unit
        )

        trace = go.Scatter(
            y=data,
            mode='lines',
            name=descr,
            **kwargs
        )

    except Exception as e:
        print('Warning: Missing curve {0}: {1}'.format(key, e))

    return axis, trace


if __name__ == '__main__':
    main()
