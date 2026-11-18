#!/usr/bin/env bash
# 启动 知识图谱服务（开发环境）
cd "$(dirname "$0")"
PYTHONPATH="$PWD/../py-genai-apigateway-client-sdk:$PYTHONPATH" uvicorn app.main:app --host 0.0.0.0 --reload --port 38107
