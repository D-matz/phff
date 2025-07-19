#public fhir server will enforce a max size on requests (eg nginx)
#comes up when trying to upload large files, eg image with attachment.data
#to find limit, start at 1kb and double every time until fail. then use binary search to find limit
#honestly could simply do binary search but might be rude to start big?
#don't worry about precision beyond 0.5% of size

from fhirpy import SyncFHIRClient
import base64

FHIR_SERVER_URL = "https://r4.smarthealthit.org/"

client = SyncFHIRClient(FHIR_SERVER_URL)

def is_upload_successful(size_bytes):
    print(size_bytes)
    dummy_data = b'x' * size_bytes
    b64 = base64.b64encode(dummy_data).decode('ascii')
    resource = {
        "resourceType": "Binary",
        "contentType": "application/octet-stream",
        "data": b64
    }
    try:
        binary = client.resource("Binary", **resource)
        binary.save()
        return True
    except Exception as e:
        if "413" in str(e):
            return False
        raise  # re-raise if it's a different error

# Phase 1: Exponential ramp-up
size = 1024  # 1 KB
while True:
    if is_upload_successful(size):
        size *= 2
    else:
        break

# Phase 2: Binary search between last success and first failure
low = size // 2
high = size - 1
max_success = low

def percent_diff(a, b):
    return abs(b - a) / max(a, b)

while percent_diff(low, high) > 0.005:
    mid = (low + high) // 2
    if is_upload_successful(mid):
        max_success = mid
        low = mid + 1
    else:
        high = mid - 1

print(f'{FHIR_SERVER_URL} max request size {round(max_success / 1024, 2)}KB or {round(max_success / (1024 * 1024), 2)}MB')