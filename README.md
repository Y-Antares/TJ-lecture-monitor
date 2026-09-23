

# 某大学高等讲堂 - 新讲座自动监控与微信提醒

本项目通过提取某大学研究生院“高等讲堂”公众号内置网页的认证凭证与 API，利用 **GitHub Actions** 实现云端无人值守监控。每当有新讲座发布时，将自动通过 **Server酱** 向手机微信推送详细提醒。

---

## 监控方式

1. **接口凭证提取**
通过抓包获取高等讲堂列表 API `GetLectureHallList` 的请求头（包含授权信息 `Authorization` 与 Cookie 中的 Session 凭证）。
2. **云端无服务器轮询**
利用 GitHub Actions 的 `cron` 定时任务，在北京时间每天 **8:00 – 21:00**（讲座发布高峰期）每 **15 分钟** 触发一次 Python 监控脚本，无需个人电脑开机或购买云服务器。
3. **本地状态比对与持久化**
脚本比对最新接口返回的讲座 `DataId` 与仓库中 `known_lectures.json` 记录的历史 ID。如发现新 ID，则提取讲座题目、地点、时间及抢票时间，并将更新后的历史记录写回 GitHub 仓库。
4. **微信即时推送**
发现新讲座或凭证失效（HTTP 401/403）时，自动调用 Server酱 Webhook 接口发送消息，秒级送达手机微信。

---

## 项目结构

```text
.
├── .github/
│   └── workflows/
│       └── run_monitor.yml   # GitHub Actions 定时任务配置（每天 8-21 点每 15 分钟运行）
├── main.py                    # 监控核心逻辑脚本
├── requirements.txt           # Python 依赖依赖（requests）
└── known_lectures.json        # 存储已记录的讲座 DataId 列表（自动生成与更新）

```

---

## 部署与配置指南

### 1. 克隆与提交项目

将本仓库代码拉取至本地或直接在 GitHub 新建项目并上传：

```bash
git add .
git commit -m "feat: initial commit"
git push -u origin main

```

### 2. 配置仓库环境变量（Secrets）

在 GitHub 仓库中依次进入 `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`，添加以下 3 个环境变量：

| Variable | 说明 |
| --- | --- |
| `SERVERCHAN_KEY` | Server酱 得到的 SendKey |
| `SESSION_ID` | 抓包获取的 `PG.ASP.Session.ID` |
| `WEIXIN_CODE_ID` | 抓包获取的 `PG.ASP.WeiXinCode.ID` |

### 3. 开启仓库写入权限

进入仓库 `Settings` -> `Actions` -> `General` -> `Workflow permissions`，勾选 **Read and write permissions** 并保存，确保 Actions 能够自动保存 `known_lectures.json`。

---

## 注意

* **凭证时效**：微信 Session/Cookie 具有一定有效期限。若收到“Cookie 已失效”的微信推送，只需在微信中重新进入讲座页面抓包，并在 GitHub Secrets 中更新对应的 `SESSION_ID` 与 `WEIXIN_CODE_ID` 即可。
