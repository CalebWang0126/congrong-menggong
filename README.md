# 从容猛攻助手

> 英文项目名：AFK Buddy（后续多平台扩展用）

游戏时微信自动报备工具。打游戏前打开，预设回复话术，女友发微信 → 自动回复 + 可选截图，安心猛攻不被打断。

## 一键启动

双击 `launch.bat` 即可。首次运行会自动安装依赖（约 1-2 分钟）。

## 手动安装

```bash
pip install -r requirements.txt
python -m src.main
```

## 使用步骤

1. **打开微信 PC 版**并登录
2. 双击 `launch.bat` 启动助手
3. 在界面中编辑**预设回复话术**
4. 勾选需要的选项：自动回复 / 截屏 / 展示消息内容
5. 在 `config.json` 中添加监控对象（首次使用需手动编辑）
6. 点击 **「开始监听」**
7. 开打游戏

## 配置说明

配置文件位置：`%APPDATA%/congrong-menggong/config.json`

```json
{
  "preset_reply": "在打排位，这把很快，打完找你 ❤️",
  "auto_reply": true,
  "screenshot": true,
  "show_content": true,
  "targets": [
    {"nickname": "宝贝老婆", "remark": ""}
  ],
  "wechat_window_title": "微信"
}
```

| 配置项 | 说明 |
|--------|------|
| `preset_reply` | 自动回复的预设话术 |
| `auto_reply` | 是否自动回复 |
| `screenshot` | 回复时是否附带屏幕截图 |
| `show_content` | 界面中是否展示对方消息内容 |
| `targets` | 监控对象列表，`nickname` 填微信昵称 |
| `wechat_window_title` | 微信窗口标题，默认"微信" |

## 系统要求

- Windows 10/11
- Python 3.11+
- 微信 PC 版 3.9.x+
