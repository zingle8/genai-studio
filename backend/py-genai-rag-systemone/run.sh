#!/usr/bin/env bash
# 启动 SystemOne 判断模型服务（laya + nanojev，开发环境）
cd "$(dirname "$0")"
PYTHONPATH="$PWD/../py-genai-loadmodel:$PWD/../py-genai-apigateway-client-sdk:$PYTHONPATH" uvicorn app.main:app --host 0.0.0.0 --reload --port 38109
