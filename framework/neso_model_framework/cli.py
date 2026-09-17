import argparse
from neso_model_framework.common.config import load_settings
from neso_model_framework.common.spark import create_spark
def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="command",required=True); r=s.add_parser("run"); r.add_argument("model"); r.add_argument("--env",default="dev",choices=["dev","test","prod"]); r.add_argument("--local",action="store_true"); a=p.parse_args()
    if a.model!="emissions_counting": raise ValueError("Add the model under models/<model_name>")
    from models.emissions_counting.pipeline import run
    spark=create_spark(f"NESO-{a.model}-{a.env}",local=a.local)
    try: run(spark,load_settings(a.env)).show(truncate=False)
    finally: spark.stop()
if __name__=="__main__": main()
