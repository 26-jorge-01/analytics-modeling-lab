import pandas as pd
from dagster import asset

def read_csv(path: str):
    df = pd.read_csv(path)

    context.log.info(df.head().to_string())
    context.log.info(f"Columnas: {list(df.columns)}")
    context.log.info(f"Filas: {len(df)}")

    return df

@asset
def brz_customers(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_customers_dataset.csv")
    return df

@asset
def brz_geolocation(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_geolocation_dataset.csv")
    return df

@asset
def brz_order_items(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_order_items_dataset.csv")
    return df

@asset
def brz_order_payments(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_order_payments_dataset.csv")
    return df

@asset
def brz_order_reviews(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_order_reviews_dataset.csv")
    return df

@asset
def brz_orders(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_orders_dataset.csv")
    return df

@asset
def brz_products(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_products_dataset.csv")
    return df

@asset
def brz_sellers(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/olist_sellers_dataset.csv")
    return df

@asset
def brz_product_category_name_translation(context):
    df = read_csv("/app/data/brz/olistbr/olist-public-dataset/product_category_name_translation.csv")
    return df