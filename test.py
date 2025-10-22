import subprocess
import os

def test_customer_access(customer_id):
    """
    Tests if the current user can access a given customer_id in PLX.
    Returns True if access is valid, False otherwise.
    """

    # Create a temporary PLX script dynamically
    temp_script = f"/tmp/check_access_{customer_id}.plx"

    plx_query = f"""
    SET queryrequest.accounting_group = 'toolsmarketplace-prod-cns-storage-owner';

    DEFINE TABLE CheckAccess (
      FORMAT 'tangle',
      QUERY FORMAT ('''
        SELECT Customer.customer_id
      '''),
      ROOTIDS_PROTOS = ['customer_id: {customer_id}']
    );
    """

    # Write to temp file
    with open(temp_script, "w") as f:
        f.write(plx_query)

    # Run the PLX query
    result = subprocess.run(
        ["plxquery", "--file", temp_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )

    # Detect access failure
    if "AUTH_ERROR_USER_CANNOT_ACCESS_CUSTOMER" in result.stderr:
        print(f"❌ Access denied for customer_id: {customer_id}")
        return False
    elif result.returncode == 0:
        print(f"✅ Access OK for customer_id: {customer_id}")
        return True
    else:
        print(f"⚠️ Unexpected error for {customer_id}: {result.stderr}")
        return False


def main():
    customer_ids = [
        "308676862",
        "123456789",
        "987654321",
    ]

    valid_ids = []
    invalid_ids = []

    for cid in customer_ids:
        if test_customer_access(cid):
            valid_ids.append(cid)
        else:
            invalid_ids.append(cid)

    print("\nSummary:")
    print("✅ Accessible customer_ids:", valid_ids)
    print("❌ Unauthorized customer_ids:", invalid_ids)

    # Save valid IDs to a file for next step (main PLX query)
    with open("/tmp/valid_customer_ids.txt", "w") as f:
        for cid in valid_ids:
            f.write(f"{cid}\n")

    print("\nValid IDs saved to /tmp/valid_customer_ids.txt")


if __name__ == "__main__":
    main()