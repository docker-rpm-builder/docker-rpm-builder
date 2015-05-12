#!/bin/bash
grep -q 'packagecloud.io/alanfranz/docker-rpm-builder-v1' /etc/apt/sources.list.d/*.list && echo "WARNING: you're using outdated repositories for docker-rpm-builder. Head to https://github.com/alanfranz/docker-rpm-builder for updates."
exit 0
