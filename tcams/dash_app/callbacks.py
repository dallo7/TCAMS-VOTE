import dash
from dash import Input, Output, State, clientside_callback, ctx, html, no_update

from tcams.dash_app import i18n_sw as sw
from tcams.dash_app.charts import empty_chart, gender_pie_chart, sentiment_pie_chart
from tcams.dash_app.layout import build_rank_rows
from tcams.dash_app.sentiment import build_sentiment_message
from tcams.database import SessionLocal
from tcams.services.analytics_service import get_analytics
from tcams.services.vote_service import get_tallies, get_time_remaining, is_poll_open, record_vote

_ALERT_CLASS = {
    "green": "tcams-alert tcams-alert--success",
    "red": "tcams-alert tcams-alert--error",
    "orange": "tcams-alert tcams-alert--closed",
}


def register_callbacks(dash_app: dash.Dash) -> None:
    @dash_app.callback(
        Output("vote-feedback", "children"),
        Output("vote-feedback", "style"),
        Output("vote-feedback", "className"),
        Output("input-name", "value"),
        Output("input-gender", "value"),
        Output("input-region", "value"),
        Output("input-station", "value"),
        Output("input-reason", "value"),
        Output("animation-trigger", "data"),
        Input("btn-vote-yes", "n_clicks"),
        Input("btn-vote-no", "n_clicks"),
        Input("btn-vote-not-sure", "n_clicks"),
        State("input-name", "value"),
        State("input-gender", "value"),
        State("input-region", "value"),
        State("input-station", "value"),
        State("input-reason", "value"),
        State("valid-regions-store", "data"),
        State("valid-stations-store", "data"),
        prevent_initial_call=True,
    )
    def submit_vote(yes_clicks, no_clicks, ns_clicks, name, gender, region, station, reason, valid_regions, valid_stations):
        triggered = ctx.triggered_id
        if triggered is None:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        choice_map = {
            "btn-vote-yes": "yes",
            "btn-vote-no": "no",
            "btn-vote-not-sure": "not_sure",
        }
        choice = choice_map.get(triggered)
        if not choice:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        if not name or not gender or not region or not station:
            return sw.VALIDATION_ERROR, {"display": "block"}, _ALERT_CLASS["red"], name, gender, region, station, reason, no_update

        if valid_regions and region not in valid_regions:
            return (
                "Tafadhali chagua mkoa halali kutoka kwenye orodha.",
                {"display": "block"},
                _ALERT_CLASS["red"],
                name,
                gender,
                region,
                station,
                reason,
                no_update,
            )

        if valid_stations and station not in valid_stations:
            return (
                "Tafadhali chagua kituo cha forodha halali kutoka kwenye orodha.",
                {"display": "block"},
                _ALERT_CLASS["red"],
                name,
                gender,
                region,
                station,
                reason,
                no_update,
            )

        db = SessionLocal()
        try:
            if not is_poll_open(db):
                return sw.POLL_CLOSED, {"display": "block"}, _ALERT_CLASS["orange"], name, gender, region, station, reason, no_update

            record_vote(
                db,
                choice=choice,
                voter_name=name.strip(),
                gender=gender,
                region=region,
                customs_station=station,
                reason=reason.strip() if reason else None,
                is_synthetic=False,
                source="public",
            )
            return (
                sw.VOTE_SUCCESS,
                {"display": "block"},
                _ALERT_CLASS["green"],
                "",
                None,
                None,
                None,
                "",
                {"choice": choice, "ts": ctx.triggered[0]["value"] if ctx.triggered else 0},
            )
        except Exception:
            return sw.VOTE_ERROR, {"display": "block"}, _ALERT_CLASS["red"], name, gender, region, station, reason, no_update
        finally:
            db.close()

    @dash_app.callback(
        Output("timer-label", "children"),
        Output("timer-label-secondary", "children"),
        Output("poll-status-alert", "children"),
        Output("poll-status-alert", "className"),
        Output("poll-status-alert", "style"),
        Output("timer-banner", "style"),
        Output("total-votes-badge", "children"),
        Output("pct-yes", "children"),
        Output("pct-no", "children"),
        Output("pct-not_sure", "children"),
        Output("fill-yes", "style"),
        Output("fill-no", "style"),
        Output("fill-not_sure", "style"),
        Output("count-yes", "children"),
        Output("count-no", "children"),
        Output("count-not_sure", "children"),
        Output("analytics-total", "children"),
        Output("analytics-sentiment", "children"),
        Output("chart-gender-pie", "figure"),
        Output("chart-sentiment-pie", "figure"),
        Output("rank-regions", "children"),
        Output("rank-stations", "children"),
        Input("refresh-interval", "n_intervals"),
    )
    def refresh_dashboard(_n):
        db = SessionLocal()
        try:
            tallies = get_tallies(db)
            time_info = get_time_remaining(db)
            analytics = get_analytics(db)
            pct = tallies["percentages"]
            counts = tallies["counts"]
            time_label = time_info["label"]

            if time_info["status"] == "pending":
                status_msg = sw.POLL_PENDING
                status_class = "tcams-alert tcams-alert--pending"
                status_style = {"display": "block"}
                banner_style = {"display": "none"}
            elif time_info["status"] == "closed" or time_info["seconds"] == 0:
                status_msg = sw.POLL_CLOSED
                status_class = "tcams-alert tcams-alert--closed"
                status_style = {"display": "block"}
                banner_style = {"display": "none"}
            else:
                status_msg = ""
                status_class = "tcams-alert tcams-alert--active"
                status_style = {"display": "none"}
                banner_style = {"display": "flex"}

            sentiment_body = build_sentiment_message(counts, pct)
            sentiment = html.Span([html.B(f"{sw.SENTIMENT}: "), sentiment_body])

            if analytics["total"] == 0:
                gender_fig = empty_chart("Usambazaji wa Jinsia")
                sentiment_fig = empty_chart("Mgawanyo wa Maoni")
                region_rows = build_rank_rows([])
                station_rows = build_rank_rows([])
            else:
                gender_fig = gender_pie_chart(analytics["gender"]["male"], analytics["gender"]["female"])
                sentiment_fig = sentiment_pie_chart(counts["yes"], counts["no"], counts["not_sure"])
                region_rows = build_rank_rows(analytics["top_regions"])
                station_rows = build_rank_rows(analytics["top_stations"])

            return (
                time_label,
                time_label,
                status_msg,
                status_class,
                status_style,
                banner_style,
                f"JUMLA YA KURA: {tallies['total']}",
                f"{pct['yes']}%",
                f"{pct['no']}%",
                f"{pct['not_sure']}%",
                {"width": f"{pct['yes']}%"},
                {"width": f"{pct['no']}%"},
                {"width": f"{pct['not_sure']}%"},
                f"{counts['yes']} kura",
                f"{counts['no']} kura",
                f"{counts['not_sure']} kura",
                str(analytics["total"]),
                sentiment,
                gender_fig,
                sentiment_fig,
                region_rows,
                station_rows,
            )
        finally:
            db.close()

    clientside_callback(
        """
        function(trigger) {
            if (!trigger || !trigger.choice) {
                return window.dash_clientside.no_update;
            }
            if (window.tcamsAnimateVote) {
                window.tcamsAnimateVote(trigger.choice);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("animation-layer", "children"),
        Input("animation-trigger", "data"),
    )
