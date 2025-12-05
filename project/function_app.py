# __init__.py
import logging
import os
import json
from urllib.parse import urlparse
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
app = func.FunctionApp()

@app.event_grid_trigger(arg_name="event")
@app.service_bus_queue_output(
    arg_name="msg",
    queue_name="INGESTION_QUEUE_NAME",
    connection="SERVICEBUS_CONNECTION"
)
def blob_to_queue(event: func.EventGridEvent, msg: func.Out[str]):
    logging.info("New file arrived → sending to Service Bus (count will be +1)")

    data = event.get_json()
    blob_url = data["url"]

    # Parse container and blob name
    parsed = urlparse(blob_url)
    container = parsed.path.lstrip("/").split("/", 1)[0]
    blob_name = parsed.path.lstrip("/").split("/", 1)[1]

    logging.info(f"File: {container}/{blob_name}")

    # Connect to storage
    if os.getenv("STORAGE_CONNECTION_STRING", "").startswith("DefaultEndpointsProtocol=http"):
        # Local Azurite
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(
            os.getenv("STORAGE_CONNECTION_STRING")
        )
    else:
        # Azure - Managed Identity
        from azure.storage.blob import BlobServiceClient
        from azure.identity import DefaultAzureCredential
        account = os.getenv("STORAGE_ACCOUNT_NAME")
        blob_service_client = BlobServiceClient(
            account_url=f"https://{account}.blob.core.windows.net",
            credential=DefaultAzureCredential()
        )

    # Read full file
    blob_client = blob_service_client.get_blob_client(container, blob_name)
    content_bytes = blob_client.download_blob().readall()

    # Show first 15 lines in log
    try:
        text = content_bytes.decode("utf-8-sig", errors="replace")
        lines = text.splitlines()[:15]
        logging.info(f"Size: {len(content_bytes):,} bytes")
        logging.info("First 15 lines:")
        for i, line in enumerate(lines, 1):
            logging.info(f"  {i:02d}: {line}")
    except:
        logging.info("Binary file – content not shown")

    # Create message with full content
    message_body = {
        "blob_url": blob_url,
        "container": container,
        "blob_name": blob_name,
        "size_bytes": len(content_bytes),
        "content_base64": content_bytes.hex(),
        "timestamp": func.EventGridEvent.get_current_utc_datetime().isoformat()
    }

    # This sends ONE message → queue count increases by 1
    msg.set(json.dumps(message_body))

    logging.info("Message successfully sent → Service Bus Active Messages = 1 per file")