import subprocess
import datetime
import pandas as pd

# 1️⃣ Load your list of customer IDs
customer_ids = [308676862, 123456789, 987654321]

# 2️⃣ Check which IDs you have access to (optional pre-check)
# If you have a BigQuery or PLX table with valid access, filter here
def filter_valid_customers(ids):
    # Example placeholder — replace with actual access-check logic
    valid_ids = []
    for cid in ids:
        # Here you could call a lightweight PLX query or API check
        try:
            subprocess.run(
                ["plxquery", f"SELECT Customer.customer_id WHERE Customer.customer_id = {cid} FORMAT 'tangle';"],
                check=True,
                capture_output=True,
                text=True
            )
            valid_ids.append(cid)
        except subprocess.CalledProcessError:
            print(f"❌ No access to customer {cid}, skipping.")
    return valid_ids

valid_ids = filter_valid_customers(customer_ids)

# 3️⃣ Generate your PLX script dynamically
start_date = (datetime.date.today() - datetime.timedelta(days=90)).strftime("%Y%m%d")
end_date = datetime.date.today().strftime("%Y%m%d")

plx_script = f"""
SET queryrequest.accounting_group = 'toolsmarketplace-prod-cns-storage-owner';
SET fl_instance = '/fl/query/prod';
SET queryrequest.num_workers = 3000;

DEFINE TABLE Campaigns (
  FORMAT 'tangle',
  QUERY FORMAT ('''
    SELECT
      Customer.external_customer_id AS external_customer_id,
      Customer.currency_code AS currency_code,
      Customer.customer_id AS internal_customer_id,
      clicks,
      impressions,
      conversions,
      conversion_value,
      DayV2.day AS Day,
      cost,
      cost_usd
    WHERE
      DayV2.day >= {start_date}
      AND DayV2.day <= {end_date}
  '''),
  ROOTIDS PROTOS = [{', '.join(f"'customer_id: {cid}'" for cid in valid_ids)}]
);
"""

# 4️⃣ Run PLX script via CLI
with open("daily_campaigns.plx", "w") as f:
    f.write(plx_script)

subprocess.run(["plxrun", "daily_campaigns.plx"], check=True)

print("✅ Daily Tangle job executed successfully!")