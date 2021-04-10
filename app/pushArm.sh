#!/bin/bash
docker buildx build --platform linux/arm/v7 -t ioticproject/main-server --push .