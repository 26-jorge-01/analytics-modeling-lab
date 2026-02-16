from dagster import load_assets_from_package_module
from . import olist_public_ds as olist_pkg

olist_brz_assets = load_assets_from_package_module(
    package_module=olist_pkg
)
