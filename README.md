# 股票涨跌幅监控机器人

## 功能
- 在中国股市开盘时间（工作日 9:30-11:30, 13:00-15:00）每半小时检查上证指数
- 当涨跌幅超过 ±1.5% 时通过 PushDeer 发送通知

## 配置方法
1. 在仓库 Settings > Secrets > Actions 添加 Secret：
   - 名称：`PUSHDEER_PUSHKEY`
   - 值：您的 PushDeer 推送密钥

2. 将代码推送到 GitHub 仓库即可自动生效
