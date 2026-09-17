import argparse
from neso_model_framework.common.config import load_settings
from neso_model_framework.common.spark import create_spark
from models.emissions_counting.pipeline import run

def main():
    p=argparse.ArgumentParser(); p.add_argument('--model',default='emissions_counting'); p.add_argument('--env',default='prod'); a=p.parse_args()
    if a.model!='emissions_counting': raise ValueError(f'Unsupported model: {a.model}')
    spark=create_spark(f'NESO-{a.model}')
    try: run(spark,load_settings(a.env))
    finally: spark.stop()
if __name__=='__main__': main()
