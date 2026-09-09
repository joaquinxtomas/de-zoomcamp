import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

prefix = 'data/'

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')


def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):

    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    first = True

    df_iter= pd.read_csv(
        prefix + 'yellow_tripdata_2021-01.csv',
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=100000
    )

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace'
            )
            first=False
            print("table created")

        df_chunk.to_sql(
            name='yellow_taxi_data',
            con=engine,
            if_exists='append'
        )

        print('Inserted: ', len(df_chunk))

if __name__ =='__main__':
    run()