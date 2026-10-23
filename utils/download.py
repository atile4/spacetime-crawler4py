import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    host, port = config.cache_server
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", url), ("u", config.user_agent)],
        timeout=(5, 30),
    )
    resp.raise_for_status()
    try:
        if resp.content:
            return Response(cbor.loads(resp.content))
    except (EOFError, ValueError):
        pass
    if logger:
        logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({"error": f"Spacetime Response error {resp} with url {url}.",
                     "status": resp.status_code, "url": url})
