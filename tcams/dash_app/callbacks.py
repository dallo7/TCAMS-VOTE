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


def _agent_debug_log(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    import json
    import time
    from pathlib import Path

    payload = {
        "sessionId": "a99dd8",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
        "runId": "celebrate-fix",
    }
    for log_path in (
        Path(__file__).resolve().parents[2] / "debug-a99dd8.log",
        Path.cwd() / "debug-a99dd8.log",
    ):
        try:
            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(payload) + "\n")
            break
        except OSError:
            continue
    # #endregion


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

            voter_name = name.strip()
            record_vote(
                db,
                choice=choice,
                voter_name=voter_name,
                gender=gender,
                region=region,
                customs_station=station,
                reason=reason.strip() if reason else None,
                is_synthetic=False,
                source="public",
            )
            vote_ts = ctx.triggered[0]["value"] if ctx.triggered else 0
            success_message = sw.vote_success_message(voter_name)
            animation = {
                "choice": choice,
                "ts": vote_ts,
                "name": voter_name,
                "fireworks": True,
                "source": "public",
            }
            _agent_debug_log(
                "A",
                "callbacks.py:submit_vote",
                "vote success",
                {"voter_name": voter_name, "message": success_message, "animation": animation},
            )
            return (
                success_message,
                {"display": "block"},
                f"{_ALERT_CLASS['green']} tcams-alert--celebrate",
                "",
                None,
                None,
                None,
                "",
                animation,
            )
        except Exception as exc:
            _agent_debug_log(
                "B",
                "callbacks.py:submit_vote",
                "vote failed",
                {"error": type(exc).__name__, "name": name},
            )
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
        Output("prev-counts-store", "data"),
        Output("animation-trigger", "data", allow_duplicate=True),
        Input("refresh-interval", "n_intervals"),
        State("prev-counts-store", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def refresh_dashboard(_n, prev_counts):
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

            prev = prev_counts or {"yes": 0, "no": 0, "not_sure": 0}
            animation = no_update
            if _n > 0:
                choices_to_animate: list[str] = []
                for choice in ("yes", "no", "not_sure"):
                    delta = counts[choice] - int(prev.get(choice, 0))
                    if delta > 0:
                        choices_to_animate.extend([choice] * min(delta, 4))
                if choices_to_animate:
                    animation = {"choices": choices_to_animate[:8], "ts": _n, "source": "refresh"}

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
                {"yes": counts["yes"], "no": counts["no"], "not_sure": counts["not_sure"]},
                animation,
            )
        finally:
            db.close()

    clientside_callback(
        """
        function(trigger) {
            if (!trigger) {
                return window.dash_clientside.no_update;
            }
            var choices = trigger.choices;
            if (!choices && trigger.choice) {
                choices = [trigger.choice];
            }
            if (choices && choices.length && window.tcamsAnimateVote) {
                choices.forEach(function(choice, index) {
                    setTimeout(function() {
                        window.tcamsAnimateVote(choice);
                    }, index * 320);
                });
            }
            if (trigger.fireworks && trigger.name && window.tcamsCelebrateVote) {
                fetch('http://127.0.0.1:7413/ingest/3fef14f3-8cd2-4979-b2ac-b4d59f7e43ee',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'a99dd8'},body:JSON.stringify({sessionId:'a99dd8',location:'callbacks.py:clientside_animation',message:'celebrate vote',data:{name:trigger.name,hasFireworks:!!window.tcamsFireworks,hasCelebrate:!!window.tcamsCelebrateVote},timestamp:Date.now(),hypothesisId:'C',runId:'celebrate-fix'})}).catch(function(){});
                window.tcamsCelebrateVote("vote-feedback");
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("animation-layer", "children"),
        Input("animation-trigger", "data"),
    )
