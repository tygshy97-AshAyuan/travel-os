# Travel OS

Travel OS is an AI Agent Skill for maintaining a travel plan as a versioned, collaborative source of truth.

它解决三个常见问题：行程修改后信息互相冲突、AI 跨会话忘记最新版、同行者意见没有明确处理状态。

## 5 分钟开始

1. 下载 Release 中的完整分发包并解压。
2. 将 `skill/travel-os/` 作为 Skill 安装，或把 `redskill/02-单文件投稿-SKILL.md` 交给支持 Markdown Skill 的平台。
3. 打开 `templates/TravelOS-Template.xlsx`，填写“旅行概览”和“当前行程”。
4. 把表格上传给 AI，并说：`读取当前 Active Version，帮我检查并优化这次旅行。所有修改先形成变更提案。`
5. 确认提案后，让 AI 写入新版本；旧版本保留在“版本记录”。

## 核心约定

- “旅行概览”中的 Active Version 是当前唯一有效版本。
- AI 先读取，再提案，再经用户确认写入。
- 已确认预订、签证、健康、费用等事实不得猜测。
- 多人意见记录为待处理、接受、拒绝或需要澄清。
- 任何公开示例都必须使用虚构数据。

## 仓库内容

- `skill/travel-os/`：标准 Skill 目录。
- `redskill/`：单文件 Markdown 投稿材料。
- `templates/`：Excel 旅行档案模板。
- `docs/`：普通用户指南和反馈方式。
- `tests/`：人工回归场景。
- `.github/ISSUE_TEMPLATE/`：公开反馈模板。

## 当前状态

v0.3.1 是试用版。Skill 与 Excel 模板已完成本地结构和文件核验；尚未经过 RedSkill 平台审核或真实客户端安装验证。请通过 GitHub Issues 提交脱敏反馈。

## 隐私

旅行档案可能包含精确日期、住宿、交通和同行者信息。公开 Issue 仅提交最小复现，删除姓名、订单号、联系方式、证件、精确住宿地址和凭据。

## License

MIT。第三方平台名称和商标归各自权利人所有。
