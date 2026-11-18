#!/usr/bin/env bash
# 启动 向量化服务（开发环境）
cd "$(dirname "$0")"
PYTHONPATH="$PWD/../py-genai-loadmodel:$PWD/../py-genai-apigateway-client-sdk:$PYTHONPATH" uvicorn app.main:app --host 0.0.0.0 --reload --port 38103
