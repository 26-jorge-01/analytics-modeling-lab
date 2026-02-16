import pandas as pd
from dagster import asset

@asset
def brz_customers(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_customers_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_geolocation(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_geolocation_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_order_items(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_order_items_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_order_payments(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_order_payments_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_order_reviews(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_order_reviews_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_orders(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_orders_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_products(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_products_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_sellers(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_sellers_dataset.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_product_category_name_translation(context):
    df = pd.read_csv("/app/data/brz/olistbr/olist-public-dataset/product_category_name_translation.csv")

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df