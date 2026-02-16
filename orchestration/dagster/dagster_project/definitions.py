from dagster import Definitions
from .assets.bronze import olist_brz_assets

defs = Definitions(
    assets=[
        *olist_brz_assets,
    ]
)
