#!/usr/bin/env bash
# 启动 GLM 双实例方案的第二个推理实例（38102）
# 第一个实例用 run.sh 启动在 38101；本实例全局闸门=1，两实例由 router 逗号分隔 base_url 轮询分发
cd "$(dirname "$0")"
PYTHONPATH="$PWD/../py-genai-loadmodel:$PWD/../py-genai-apigateway-client-sdk:$PYTHONPATH" \
INFER_MAX_GLOBAL_INFLIGHT=1 \
  nohup uvicorn app.main:app --host 127.0.0.1 --port 38102 > /tmp/genai-infer-38102.log 2>&1 &
echo "instance2(38102) started, pid=$!"
