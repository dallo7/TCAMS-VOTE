import plotly.graph_objects as go

from tcams.dash_app.chart_colors import CHART_COLORS, GREEN, NAVY, SKY, YELLOW


def _contrast_text_color(hex_color: str) -> str:
    color = hex_color.lstrip("#")
    red, green, blue = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    luminance = 0.299 * red + 0.587 * green + 0.114 * blue
    return NAVY if luminance > 150 else "#ffffff"


def _bar_count_positions(counts: list[int]) -> list[str]:
    if not counts:
        return []
    peak = max(counts) or 1
    return ["inside" if count >= peak * 0.18 else "outside" for count in counts]


def _horizontal_rank_bar(
    labels: list[str],
    counts: list[int],
    title: str,
    *,
    hover_labels: list[str] | None = None,
    color_offset: int = 0,
) -> go.Figure:
    colors = [CHART_COLORS[(index + color_offset) % len(CHART_COLORS)] for index in range(len(labels))]
    hover = hover_labels or labels
    peak = max(counts) if counts else 1
    text_colors = [_contrast_text_color(color) for color in colors]

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts,
                y=labels,
                orientation="h",
                marker={"color": colors, "line": {"width": 0}, "cornerradius": 4},
                text=[str(count) for count in counts],
                textposition=_bar_count_positions(counts),
                textfont={"size": 12, "color": text_colors, "family": "Montserrat, sans-serif"},
                outsidetextfont={"size": 12, "color": NAVY, "family": "Montserrat, sans-serif"},
                insidetextanchor="end",
                hovertext=hover,
                hovertemplate="<b>%{hovertext}</b><br>Idadi ya Kura: %{x}<extra></extra>",
                cliponaxis=False,
            )
        ]
    )

    layout = _base_layout(title)
    layout["showlegend"] = False
    layout["height"] = max(230, 56 * len(labels) + 88)
    layout["margin"] = {"l": 8, "r": 28, "t": 48, "b": 40}
    layout["xaxis"] = {
        "title": {"text": "Idadi ya Kura", "font": {"size": 11, "color": NAVY}},
        "gridcolor": "#e9eef5",
        "zeroline": False,
        "range": [0, peak * 1.15 + 0.35],
        "dtick": 1 if peak <= 6 else None,
        "tickfont": {"size": 11, "color": NAVY},
    }
    layout["yaxis"] = {
        "autorange": "reversed",
        "automargin": True,
        "tickfont": {"size": 11, "color": NAVY},
        "ticklabelstandoff": 6,
    }
    fig.update_layout(**layout)
    return fig


def _base_layout(title: str) -> dict:
    return {
        "title": {"text": title, "font": {"family": "Plus Jakarta Sans, Inter, sans-serif", "size": 13, "color": NAVY}},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"l": 8, "r": 8, "t": 28, "b": 8},
        "font": {"family": "Inter, sans-serif", "color": NAVY, "size": 11},
        "showlegend": True,
        "legend": {"orientation": "h", "yanchor": "bottom", "y": -0.22, "x": 0, "font": {"size": 10}},
        "height": 220,
    }


def gender_pie_chart(male: int, female: int) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Wanaume", "Wanawake"],
                values=[male, female],
                marker={"colors": [NAVY, SKY]},
                hole=0.42,
                textinfo="label+percent",
                textfont={"size": 12},
            )
        ]
    )
    layout = _base_layout("Usambazaji wa Jinsia")
    layout["title"] = {"text": ""}
    fig.update_layout(**layout)
    return fig


def sentiment_pie_chart(yes: int, no: int, not_sure: int) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Ndiyo", "Hapana", "Sijui"],
                values=[yes, no, not_sure],
                marker={"colors": [GREEN, NAVY, YELLOW]},
                hole=0.42,
                textinfo="label+percent",
                textfont={"size": 12},
            )
        ]
    )
    layout = _base_layout("Mgawanyo wa Maoni")
    layout["title"] = {"text": ""}
    fig.update_layout(**layout)
    return fig


def top_regions_bar(regions: list[str], counts: list[int]) -> go.Figure:
    return _horizontal_rank_bar(
        regions,
        counts,
        "Mkoa Ulioongoza (Kura 5 Bora)",
        color_offset=0,
    )


def top_stations_bar(stations: list[str], counts: list[int]) -> go.Figure:
    return _horizontal_rank_bar(
        stations,
        counts,
        "Kituo cha Forodha Kilichoongoza (Kura 5 Bora)",
        hover_labels=stations,
        color_offset=2,
    )


def gender_votes_bar(
    male_yes: float,
    male_no: float,
    female_yes: float,
    female_no: float,
) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Bar(name="Ndiyo", x=["Wanaume", "Wanawake"], y=[male_yes, female_yes], marker_color=GREEN),
            go.Bar(name="Hapana", x=["Wanaume", "Wanawake"], y=[male_no, female_no], marker_color=NAVY),
        ]
    )
    layout = _base_layout("Asilimia ya Jinsia: Ndiyo vs Hapana")
    layout["barmode"] = "group"
    layout["yaxis"] = {"title": "Asilimia (%)", "gridcolor": "#e9eef5", "range": [0, 100]}
    fig.update_layout(**layout)
    return fig


def empty_chart(title: str, message: str = "Hakuna data bado") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14, "color": NAVY},
    )
    fig.update_layout(**_base_layout(title))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig
