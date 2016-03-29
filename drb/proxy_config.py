
import os

PROXY_VARIABLES = ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "NO_PROXY", "no_proxy"]

def configure_proxies(logger, docker):
    configured = False
    for var in PROXY_VARIABLES:
        if var in os.environ:
            docker.env(var, os.environ[var])
            configured = True

    if configured:
        logger.info("Set proxy variables for build.")
