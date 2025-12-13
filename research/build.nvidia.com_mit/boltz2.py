#!/usr/bin/env python3
import asyncio
import json
from typing import Any, Dict, Optional
import os
from pathlib import Path
from enum import StrEnum
import logging
import sys
import keyring

# ref: https://build.nvidia.com/mit/boltz2?snippet_tab=Python
print(f"current python {sys.executable}")

NVIDIA_API_KEY=keyring.get_password("NVIDIA_API_KEY", "NVIDIA_API_KEY")
# Check for required dependencies
missing_deps = []
try:
    import httpx
except ImportError:
    missing_deps.append("httpx")
try:
    from fastapi import HTTPException
except ImportError:
    missing_deps.append("fastapi")

if missing_deps:
    print("Error: Missing required dependencies. Please install them using:")
    print(f"pip install {' '.join(missing_deps)}")
    sys.exit(1)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

STATUS_URL = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status/{task_id}"

PUBLIC_URL = "https://health.api.nvidia.com/v1/biology/mit/boltz2/predict"


async def make_nvcf_call(function_url: str,
                         data: Dict[str, Any],
                         additional_headers: Optional[Dict[str, Any]] = None,
                         NVCF_POLL_SECONDS: int = 300,
                         MANUAL_TIMEOUT_SECONDS: int = 400) -> Dict:
    """
    Make a call to NVIDIA Cloud Functions using long-polling,
    which allows the request to patiently wait if there are many requests in the queue.
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "NVCF-POLL-SECONDS": f"{NVCF_POLL_SECONDS}",
            "Content-Type": "application/json"
        }
        if additional_headers is not None:
            headers.update(additional_headers)
        logger.debug(f"Headers: {dict(**{h: v for h, v in headers.items() if 'Authorization' not in h})}")
        # TIMEOUT must be greater than NVCF-POLL-SECONDS
        logger.debug(f"Making NVCF call to {function_url}")
        logger.debug(f"Data: {data}")
        response = await client.post(function_url,
                                     json=data,
                                     headers=headers,
                                     timeout=MANUAL_TIMEOUT_SECONDS)
        logger.debug(f"NVCF response: {response.status_code, response.headers}")

        if response.status_code == 202:
            # Handle 202 Accepted response
            task_id = response.headers.get("nvcf-reqid")
            while True:
                ## Should return in 5 seconds, but we set a manual timeout in 10 just in case
                status_response = await client.get(STATUS_URL.format(task_id=task_id),
                                                   headers=headers,
                                                   timeout=MANUAL_TIMEOUT_SECONDS)
                if status_response.status_code == 200:
                    return status_response.status_code, status_response
                elif status_response.status_code in [400, 401, 404, 422, 500]:
                    raise HTTPException(status_response.status_code,
                                        "Error while waiting for function: ",
                                        response.text)
        elif response.status_code == 200:
            return response.status_code, response
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)


async def main():
    # Example protein sequence
    sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    output_file = Path("../output.json")

    # Prepare the request payload
    data = {
        "polymers": [
            {
                "id": "A",
                "molecule_type": "protein",
                "sequence": sequence,
                "msa": {
                    "uniref90": {
                        "a3m": {
                            "alignment": f">seq1\n{sequence}",
                            "format": "a3m"
                        }
                    }
                }
            }
        ],
        "ligands": [
            {
                "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
                "id": "L1",
                "predict_affinity": True
            }
        ],
        "recycling_steps": 1,
        "sampling_steps": 50,
        "diffusion_samples": 3,
        "step_scale": 1.2,
        "without_potentials": True
    }

    print("Making request...")
    code, response = await make_nvcf_call(function_url=PUBLIC_URL,
                                          data=data)

    if code == 200:
        print(f"Request succeeded, returned {code}")
        response_dict = response.json()
        output_file.write_text(json.dumps(response_dict, indent=4))

        # Print information about the returned structures
        print(f"Number of structures returned: {len(response_dict['structures'])}")
        print(f"Number of confidence scores: {len(response_dict['confidence_scores'])}")

        # Print the first structure's format and length
        if response_dict['structures']:
            first_structure = response_dict['structures'][0]
            print(f"First structure format: {first_structure['format']}")
            print(f"First structure length: {len(first_structure['structure'])} characters")

        # Print confidence scores
        print(f"Confidence scores: {response_dict['confidence_scores']}")


if __name__ == "__main__":
    asyncio.run(main())

