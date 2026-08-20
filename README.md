# Data API Service
# 自动赚钱的 API 服务平台

## 快速部署

### Railway (推荐)
1. 访问 https://railway.app/
2. 登录 GitHub 账号
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 导入项目: `data-api-service`
6. 点击 "Deploy"

### 本地运行
```bash
cd ~/桌面/data-api-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API 端点

| 端点 | 方法 | 说明 | 价格 |
|------|------|------|------|
| `/api/v1/shorten` | POST | 创建短链接 | $0.001/次 |
| `/api/v1/resolve/{code}` | GET | 解析短链接 | $0.001/次 |
| `/api/v1/stats` | GET | 获取统计 | 免费 |
| `/health` | GET | 健康检查 | 免费 |

## 收入模式
- 按调用次数收费: $0.001-0.01/次
- 预计月收入: $500-2000
