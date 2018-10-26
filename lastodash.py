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
        html.H1('LAS Report'),
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
    graphs = []

    dgr = build_graph_dgr(las)
    if dgr is not None:
        graphs.append(dgr)

    rp = build_graph_rp(las)
    if rp is not None:
        graphs.append(rp)

    ald = build_graph_ald(las)
    if ald is not None:
        graphs.append(ald)

    ctn = build_graph_ctn(las)
    if ctn is not None:
        graphs.append(ctn)

    bat = build_graph_bat(las)
    if bat is not None:
        graphs.append(bat)

    return html.Div(
        [html.H2('Section: curves')] + graphs,
        className='las-curves'
    )


SCATTER_LINE_LINE_BLACK = dict(color='black', width=1)
SCATTER_LINE_LINE_RED = dict(color='red', width=1)
SCATTER_LINE_LINE_GREEN = dict(color='green', width=1)
SCATTER_LINE_LINE_BLUE = dict(color='blue', width=1)
SCATTER_LINE_LINE_MAGENTA = dict(color='magenta', width=1)

SCATTER_LINE_DASH_BLACK = dict(color='black', dash='dash', width=1)
SCATTER_LINE_DASH_RED = dict(color='red', dash='dash', width=1)
SCATTER_LINE_DASH_GREEN = dict(color='green', dash='dash', width=1)
SCATTER_LINE_DASH_BLUE = dict(color='blue', dash='dash', width=1)
SCATTER_LINE_DASH_MAGENTA = dict(color='magenta', dash='dash', width=1)

SCATTER_LINE_DOT_BLACK = dict(color='black', dash='dot', width=1)
SCATTER_LINE_DOT_RED = dict(color='red', dash='dot', width=1)
SCATTER_LINE_DOT_GREEN = dict(color='green', dash='dot', width=1)
SCATTER_LINE_DOT_BLUE = dict(color='blue', dash='dot', width=1)
SCATTER_LINE_DOT_MAGENTA = dict(color='magenta', dash='dot', width=1)

SCATTER_LINE_DASHDOT_BLACK = dict(color='black', dash='dashdot', width=1)
SCATTER_LINE_DASHDOT_RED = dict(color='red', dash='dashdot', width=1)
SCATTER_LINE_DASHDOT_GREEN = dict(color='green', dash='dashdot', width=1)
SCATTER_LINE_DASHDOT_BLUE = dict(color='blue', dash='dashdot', width=1)
SCATTER_LINE_DASHDOT_MAGENTA = dict(color='magenta', dash='dashdot', width=1)


def build_graph_dgr(las):
    data, yaxis, yaxis2 = [], None, None

    if 'BTVPVS' in las.curves:
        btvpvs_trace, btvpvs_axis = build_trace(
            las.curves['BTVPVS'],
            line=SCATTER_LINE_LINE_MAGENTA,
            yaxis='y'
        )
        data.append(btvpvs_trace)
        yaxis = btvpvs_axis

    if 'DGRC' in las.curves:
        dgrc_trace, dgrc_axis = build_trace(
            las.curves['DGRC'],
            line=SCATTER_LINE_LINE_GREEN,
            yaxis='y2' if yaxis else 'y'
        )
        data.append(dgrc_trace)
        if yaxis:
            yaxis2 = dgrc_axis
        else:
            yaxis = dgrc_axis

    return build_graph('las-curves-dgr', las, data, yaxis, yaxis2)


def build_graph_rp(las):
    data, yaxis, yaxis2 = [], None, None

    if 'EWXT' in las.curves:
        ewxt_trace, ewxt_axis = build_trace(
            las.curves['EWXT'],
            line=SCATTER_LINE_DASHDOT_MAGENTA,
            yaxis='y'
        )
        ewxt_axis['type'] = 'log'
        data.append(ewxt_trace)
        yaxis = ewxt_axis

    rp_axis = dict(
        title='RxxP [ohmm]',
        type='log'
    )
    rp_keys = ['R09P', 'R15P', 'R27P', 'R39P']
    rp_lines = [
        SCATTER_LINE_DASHDOT_GREEN,
        SCATTER_LINE_LINE_BLACK,
        SCATTER_LINE_DOT_BLUE,
        SCATTER_LINE_DASH_RED
    ]
    has_rp = False

    for key, line in zip(rp_keys, rp_lines):
        if key in las.curves:
            rp_trace, _ = build_trace(
                las.curves[key],
                line=line,
                yaxis='y2' if yaxis else 'y'
            )
            data.append(rp_trace)
            has_rp = True

    if has_rp:
        if yaxis:
            yaxis2 = rp_axis
        else:
            yaxis = rp_axis

    return build_graph('las-curves-rp', las, data, yaxis, yaxis2)


def build_graph_ald(las):
    data, yaxis, yaxis2 = [], None, None

    if 'ALDCLC' in las.curves:
        aldclc_trace, aldclc_axis = build_trace(
            las.curves['ALDCLC'],
            line=SCATTER_LINE_DASH_BLACK,
            yaxis='y'
        )
        data.append(aldclc_trace)
        yaxis = aldclc_axis

    if 'ALCDLC' in las.curves:
        alcdlc_trace, alcdlc_axis = build_trace(
            las.curves['ALCDLC'],
            line=SCATTER_LINE_LINE_RED,
            yaxis='y2' if yaxis else 'y'
        )
        data.append(alcdlc_trace)
        if yaxis:
            yaxis2 = alcdlc_axis
        else:
            yaxis = alcdlc_axis

    return build_graph('las-curves-ald', las, data, yaxis, yaxis2)


def build_graph_ctn(las):
    data, yaxis = [], None

    if 'TNPS' in las.curves:
        tnps_trace, tnps_axis = build_trace(
            las.curves['TNPS'],
            line=SCATTER_LINE_LINE_BLUE,
            yaxis='y'
        )
        data.append(tnps_trace)
        yaxis = tnps_axis

    return build_graph('las-curves-ctn', las, data, yaxis)


def build_graph_bat(las):
    data, yaxis, yaxis2 = [], None, None

    if 'BTCSS' in las.curves:
        btcss_trace, btcss_axis = build_trace(
            las.curves['BTCSS'],
            line=SCATTER_LINE_LINE_MAGENTA,
            yaxis='y'
        )
        data.append(btcss_trace)
        yaxis = btcss_axis

    if 'BTCS' in las.curves:
        btcs_trace, btcs_axis = build_trace(
            las.curves['BTCS'],
            line=SCATTER_LINE_LINE_GREEN,
            yaxis='y2' if yaxis else 'y'
        )
        data.append(btcs_trace)
        if yaxis:
            yaxis2 = btcs_axis
        else:
            yaxis = btcs_axis

    return build_graph('las-curves-bat', las, data, yaxis, yaxis2)


def build_trace(curve, **kwargs):
    key = curve.original_mnemonic
    data = curve.data
    unit = ' [{0}]'.format(curve.unit) if curve.unit != 'NONE' else ''
    descr = curve.descr

    trace = go.Scatter(
        y=data,
        mode='lines',
        name=descr,
        **kwargs
    )

    axis = dict(
        title=key+unit
    )

    return trace, axis


def build_graph(id, las, data, yaxis=None, yaxis2=None):
    if not data:
        return None

    x = las.depth_ft
    xaxis = dict(
        title='depth [ft]'
    )

    for trace in data:
        trace['x'] = x

    if yaxis2 is not None:
        # since yaxis2 is drawn on top of yaxis
        yaxis['side'] = 'right'
        yaxis['showgrid'] = False

    # Note: xaxis, yaxis and yaxis2 must be set before creating layout.
    layout = go.Layout(
        hovermode='x',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        xaxis=xaxis,
        yaxis=yaxis
    )

    if yaxis2 is not None:
        layout['yaxis2'] = yaxis2

    return dcc.Graph(figure={'data': data, 'layout': layout}, id=id)


if __name__ == '__main__':
    main()
