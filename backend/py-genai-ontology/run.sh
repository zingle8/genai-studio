#!/usr/bin/env bash
# 启动 本体知识服务（开发环境）
cd "$(dirname "$0")"
PYTHONPATH="$PWD/../py-genai-apigateway-client-sdk:$PYTHONPATH" uvicorn app.main:app --host 0.0.0.0 --reload --port 38105
