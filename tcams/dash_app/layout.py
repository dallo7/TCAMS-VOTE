import dash_mantine_components as dmc
from dash import dcc, html

from tcams.dash_app import i18n_sw as sw
from tcams.dash_app.theme import TCAMS_THEME


def _svg_icon(uri: str) -> html.Img:
    return html.Img(src=uri, style={"width": "16px", "height": "16px"}, alt="")


_ICON_CLOCK = _svg_icon(
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232f7d39' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M12 7v5l3 2'/%3E%3C/svg%3E"
)
_ICON_YES = _svg_icon(
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2.4'%3E%3Cpath d='M5 13l4 4L19 7'/%3E%3C/svg%3E"
)
_ICON_NO = _svg_icon(
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2.4'%3E%3Cpath d='M6 6l12 12M18 6 6 18'/%3E%3C/svg%3E"
)
_ICON_UNSURE = _svg_icon(
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23c9a414' stroke-width='2.2'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.8.4-1 .9-1 1.7M12 17h.01'/%3E%3C/svg%3E"
)


def build_layout(regions: list[str], stations: list[str]) -> dmc.MantineProvider:
    return dmc.MantineProvider(
        theme=TCAMS_THEME,
        forceColorScheme="light",
        children=[
            dcc.Store(id="valid-regions-store", data=regions),
            dcc.Store(id="valid-stations-store", data=stations),
            dcc.Store(id="animation-trigger", data=None),
            dcc.Interval(id="refresh-interval", interval=3000, n_intervals=0),
            html.Div(
                className="tcams-page",
                children=[
                    html.Div(
                        className="container",
                        children=[
                            html.Div(
                                className="head reveal",
                                children=[
                                    html.H1(sw.APP_TITLE),
                                    html.P(sw.POLL_QUESTION),
                                    html.Div(className="flag-rule"),
                                ],
                            ),
                            html.Div(
                                id="poll-status-alert",
                                className="tcams-alert tcams-alert--pending",
                                style={"display": "none"},
                                children=sw.POLL_PENDING,
                            ),
                            html.Div(
                                id="vote-feedback",
                                className="tcams-alert tcams-alert--success",
                                style={"display": "none"},
                            ),
                            html.Div(
                                id="timer-banner",
                                className="banner reveal",
                                children=[
                                    _ICON_CLOCK,
                                    html.Span(f"{sw.TIMER_LABEL}:"),
                                    html.B(id="timer-label", children="00:00:00"),
                                ],
                            ),
                            html.Div(
                                className="poll-grid",
                                children=[
                                    html.Section(
                                        className="card pad reveal",
                                        children=[
                                            html.H2("Fomu ya Kupiga Kura", className="card-title"),
                                            html.Div(
                                                className="field-wrap",
                                                children=[
                                                    dmc.TextInput(
                                                        id="input-name",
                                                        label=sw.LABEL_NAME,
                                                        placeholder=sw.PLACEHOLDER_NAME,
                                                        required=True,
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="field-wrap",
                                                children=[
                                                    dmc.Select(
                                                        id="input-gender",
                                                        label=sw.LABEL_GENDER,
                                                        data=sw.GENDER_OPTIONS,
                                                        placeholder="Chagua jinsia…",
                                                        required=True,
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="field-wrap",
                                                children=[
                                                    dmc.Autocomplete(
                                                        id="input-region",
                                                        label=sw.LABEL_REGION,
                                                        data=regions,
                                                        placeholder=sw.PLACEHOLDER_REGION,
                                                        limit=20,
                                                        required=True,
                                                        comboboxProps={"withinPortal": True},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="field-wrap",
                                                children=[
                                                    dmc.Autocomplete(
                                                        id="input-station",
                                                        label=sw.LABEL_STATION,
                                                        data=stations,
                                                        placeholder=sw.PLACEHOLDER_STATION,
                                                        limit=20,
                                                        required=True,
                                                        comboboxProps={"withinPortal": True},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="field-wrap",
                                                children=[
                                                    dmc.Textarea(
                                                        id="input-reason",
                                                        label=sw.LABEL_REASON,
                                                        placeholder=sw.PLACEHOLDER_REASON,
                                                        minRows=3,
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="vote-row",
                                                children=[
                                                    html.Button(
                                                        [_ICON_YES, sw.BTN_YES],
                                                        id="btn-vote-yes",
                                                        className="tcams-btn tcams-btn--green vote-btn",
                                                        n_clicks=0,
                                                        type="button",
                                                    ),
                                                    html.Button(
                                                        [_ICON_NO, sw.BTN_NO],
                                                        id="btn-vote-no",
                                                        className="tcams-btn vote-btn",
                                                        n_clicks=0,
                                                        type="button",
                                                    ),
                                                ],
                                            ),
                                            html.Button(
                                                [_ICON_UNSURE, sw.BTN_NOT_SURE],
                                                id="btn-vote-not-sure",
                                                className="tcams-btn tcams-btn--ghost vote-btn",
                                                n_clicks=0,
                                                type="button",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="stack",
                                        children=[
                                            html.Section(
                                                className="card pad reveal d2",
                                                children=[
                                                    html.Div(
                                                        className="results-head",
                                                        children=[
                                                            html.Div(
                                                                className="t",
                                                                children=[
                                                                    sw.TIMER_LABEL,
                                                                    ": ",
                                                                    html.Span(
                                                                        id="timer-label-secondary",
                                                                        className="mono",
                                                                        children="00:00:00",
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Span(
                                                                id="total-votes-badge",
                                                                className="pill",
                                                                children="JUMLA YA KURA: 0",
                                                            ),
                                                        ],
                                                    ),
                                                    _tally_bar(sw.TALLY_YES, "yes", "c-green", "f-green"),
                                                    _tally_bar(sw.TALLY_NO, "no", "c-navy", "f-navy"),
                                                    _tally_bar(sw.TALLY_NOT_SURE, "not_sure", "c-gold", "f-gold"),
                                                ],
                                            ),
                                            html.Section(
                                                className="card pad reveal d2",
                                                children=[
                                                    html.H3(sw.ANALYTICS_TITLE, className="card-title sm"),
                                                    html.Div(
                                                        className="summary",
                                                        children=[
                                                            html.Div(sw.TOTAL_VOTERS, className="k"),
                                                            html.Div(id="analytics-total", className="big", children="0"),
                                                            html.Div(id="analytics-sentiment", className="note"),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        className="duo",
                                                        children=[
                                                            html.Div(
                                                                className="mini",
                                                                children=[
                                                                    html.H4(sw.GENDER_DIST),
                                                                    html.Div(
                                                                        className="chart-card",
                                                                        children=[
                                                                            dcc.Graph(
                                                                                id="chart-gender-pie",
                                                                                config={"displayModeBar": False},
                                                                            )
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="mini",
                                                                children=[
                                                                    html.H4("Mgawanyo wa Maoni"),
                                                                    html.Div(
                                                                        className="chart-card",
                                                                        children=[
                                                                            dcc.Graph(
                                                                                id="chart-sentiment-pie",
                                                                                config={"displayModeBar": False},
                                                                            )
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        className="duo",
                                                        style={"marginTop": "16px"},
                                                        children=[
                                                            html.Div(
                                                                className="mini",
                                                                children=[
                                                                    html.H4("Mkoa Ulioongoza (5 Bora)"),
                                                                    html.Div(id="rank-regions"),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="mini",
                                                                children=[
                                                                    html.H4(sw.TOP_STATION),
                                                                    html.Div(id="rank-stations"),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(id="animation-layer", className="animation-layer"),
                ],
            ),
        ],
    )


def _tally_bar(label: str, choice: str, label_class: str, fill_class: str) -> html.Div:
    return html.Div(
        className="tally-row",
        children=[
            html.Div(
                className="tally-label-row",
                children=[
                    html.Span(label, className=f"tally-label {label_class}"),
                    html.Span(id=f"pct-{choice}", className="tally-pct", children="0.0%"),
                ],
            ),
            html.Div(
                id=f"bar-{choice}",
                className="tally-bar",
                **{"data-choice": choice},
                children=[
                    html.Div(id=f"fill-{choice}", className=f"tally-fill {fill_class}", style={"width": "0%"}),
                ],
            ),
            html.Span(id=f"count-{choice}", className="tally-count", children="0 kura"),
        ],
    )


def build_rank_rows(items: list[dict]) -> list:
    if not items:
        return [html.Div("Hakuna data bado", className="rank-empty")]
    return [
        html.Div(
            className="rank",
            children=[
                html.Span(str(index), className="n"),
                html.Span(item["name"], className="nm", title=item["name"]),
                html.Span(f'{item["count"]} kura', className="ct"),
            ],
        )
        for index, item in enumerate(items, start=1)
    ]
