import csv
import datetime
import uuid
from azure.data.tables import TableServiceClient
import config

def save_csv(results: list, filename: str = None):
    if not filename:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/run_{ts}.csv"

    import os
    os.makedirs("results", exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "prompt", "expected", "actual", "outcome", "layer", "confidence"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"CSV saved: {filename}")
    return filename

def save_azure(results: list):
    if not config.AZURE_STORAGE_CONNECTION_STRING:
        print("No Azure connection — skipping Azure log")
        return

    try:
        service = TableServiceClient.from_connection_string(
            config.AZURE_STORAGE_CONNECTION_STRING
        )
        table = service.get_table_client(config.AZURE_TABLE_NAME)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        for r in results:
            entity = {
                "PartitionKey": ts,
                "RowKey": str(uuid.uuid4()),
                "prompt": r["prompt"][:500],
                "expected": r["expected"],
                "actual": r["actual"],
                "outcome": r["outcome"],
                "layer": r["layer"],
                "confidence": float(r["confidence"])
            }
            table.create_entity(entity)

        print(f"Azure Table: {len(results)} entries logged")
    except Exception as e:
        print(f"Azure log failed: {e}")
