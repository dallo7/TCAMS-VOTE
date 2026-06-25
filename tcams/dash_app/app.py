from pathlib import Path

import dash
from sqlalchemy.orm import Session

from tcams.config import ASSETS_DIR
from tcams.dash_app.layout import build_layout
from tcams.models import Agent


def _load_region_data(db: Session) -> tuple[list[str], list[str]]:
    agents = db.query(Agent.region, Agent.customs_station).all()
    regions = sorted({region for region, _ in agents})
    stations = sorted({station for _, station in agents})
    return regions, stations


def create_dash_app(session_factory) -> dash.Dash:
    assets_path = str(ASSETS_DIR)
    db = session_factory()
    try:
        regions, stations = _load_region_data(db)
    finally:
        db.close()

    dash_app = dash.Dash(
        __name__,
        assets_folder=assets_path,
        suppress_callback_exceptions=True,
        title="TCAMS Uchaguzi",
    )
    dash_app.index_string = """<!DOCTYPE html>
<html lang="sw">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <link rel="icon" type="image/jpeg" href="/assets/tcams-logo.jpeg"/>
        <link rel="apple-touch-icon" href="/assets/tcams-logo.jpeg"/>
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;450;500;600&family=Space+Mono&display=swap" rel="stylesheet"/>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""
    dash_app.layout = build_layout(regions, stations)
    return dash_app
