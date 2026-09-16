"""
Zenodo Auto-Deploy Script
Hyperion DeepTech Research Group

Usage:
  set ZENODO_TOKEN=your_token_here
  python zenodo_deploy.py <path_to_pdf> <path_to_metadata.json>

Get your token at: https://zenodo.org/account/settings/applications/tokens/new/
Required scopes: deposit:write, deposit:actions
"""

import os
import sys
import json
import requests

ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions"
# For testing without real records:
# ZENODO_API_URL = "https://sandbox.zenodo.org/api/deposit/depositions"

ACCESS_TOKEN = os.environ.get("ZENODO_TOKEN")

if not ACCESS_TOKEN:
    print("Error: set environment variable ZENODO_TOKEN")
    sys.exit(1)


def deploy_to_zenodo(pdf_path, metadata_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    headers = {"Content-Type": "application/json"}
    params = {"access_token": ACCESS_TOKEN}

    # 1. Create empty deposition
    r = requests.post(ZENODO_API_URL, params=params, json={}, headers=headers)
    if r.status_code != 201:
        raise RuntimeError(f"Deposition creation failed: {r.text}")

    dep_data = r.json()
    deposition_id = dep_data["id"]
    bucket_url = dep_data["links"]["bucket"]
    print(f"[+] Deposition created: ID {deposition_id}")

    # 2. Upload PDF via Bucket API
    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as fp:
        upload_res = requests.put(
            f"{bucket_url}/{filename}",
            data=fp,
            params=params,
            headers={"Content-Type": "application/octet-stream"}
        )
    if upload_res.status_code not in (200, 201):
        raise RuntimeError(f"File upload failed: {upload_res.text}")
    print(f"[+] File {filename} uploaded")

    # 3. Set metadata
    meta_res = requests.put(
        f"{ZENODO_API_URL}/{deposition_id}",
        params=params,
        data=json.dumps({"metadata": meta}),
        headers=headers
    )
    if meta_res.status_code != 200:
        raise RuntimeError(f"Metadata update failed: {meta_res.text}")
    print("[+] Metadata attached")

    # 4. Publish
    publish_res = requests.post(
        f"{ZENODO_API_URL}/{deposition_id}/actions/publish",
        params=params
    )
    if publish_res.status_code != 202:
        raise RuntimeError(f"Publish failed: {publish_res.text}")

    published_data = publish_res.json()
    doi = published_data["doi"]
    doi_url = published_data["links"]["doi"]

    print("\n" + "=" * 50)
    print("DEPLOY COMPLETE")
    print(f"DOI: {doi}")
    print(f"URL: {doi_url}")
    print("=" * 50)
    return doi


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python zenodo_deploy.py <pdf_path> <metadata.json>")
        sys.exit(1)
    deploy_to_zenodo(sys.argv[1], sys.argv[2])
