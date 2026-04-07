#!/bin/bash
# 库氏管家 - 每日天气推送
# 发送上海当天天气给库哥

WEATHER=$(curl -s "wttr.in/Shanghai?format=%l:+%c+%t+(feels+like+%f),+%w+wind,+%h+humidity,+%p+precipitation")
curl -s -X POST "http://localhost:8080/api/send" \
  -H "Content-Type: application/json" \
  -d "{\"to\":\"o9cq80xQoFLXZnk9P4l90kFrxLzs@im.wechat\",\"message\":\"☀️ 早安库哥！今日天气：$WEATHER\"}"
