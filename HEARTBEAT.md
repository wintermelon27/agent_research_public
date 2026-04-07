# HEARTBEAT.md

## 价格监控提醒

检查文件 `/tmp/intc_alert_flag.txt`，如果存在且包含 `TRIGGERED`，则：
1. 读取触发时间和价格
2. 通过 message 工具发送微信通知到当前渠道（账号: c51a50e32c7c-im-bot, 渠道: openclaw-weixin, to: o9cq80xQoFLXZnk9P4l90kFrxLzs@im.wechat）
3. 发送完毕后删除该文件

通知内容格式：
"📢 INTC $60 Call (2026-06-18) 价格提醒
当前价格: $X.XX
监控价: $2.45
状态: 已触及限价附近，请前往 IBKR 挂单买入！"

## 其他

HEARTBEAT_OK 在无其他任务时返回。
