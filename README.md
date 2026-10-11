# Travel OS

Travel OS is an AI Agent Skill for planning, executing and maintaining a trip as a versioned source of truth.

它解决三个常见问题：行程修改后信息互相冲突、AI 跨会话忘记最新版、同行者意见没有明确处理状态。

## 5 分钟开始

1. 下载 Release 中的完整分发包并解压。
2. 将 `skill/travel-os/` 安装为 Agent Skill。
3. 打开 `templates/TravelOS-Template.xlsx`，先填写 `Travel Overview`、`Preferences`、`Bookings` 和 `Members`。
4. 上传表格并说：`恢复当前旅行状态，告诉我 Active Version、硬约束、已确认预订和下一步。不要直接改档案。`
5. 新旅行先生成 Draft；修改现有旅行时先审查变更提案，确认后再生成新版本。

## 核心约定

- `Travel Overview` 中的 Active Version 是当前唯一有效版本。
- 每次会话先执行恢复协议：读取、校验、总结，再回答。
- AI 先读取，再提案，再经用户确认写入；写入失败时不得更新 Active Version。
- 已确认预订、签证、健康、费用等事实不得猜测。
- 多人意见记录为待处理、接受、拒绝或需要澄清。
- 执行中的临时变化与正式行程版本分开记录；只有影响后续计划时才创建新版本。
- 任何公开示例都必须使用虚构数据。

## 仓库内容

- `skill/travel-os/`：标准 Skill 目录。
- `templates/`：Excel 旅行档案模板。
- `docs/`：普通用户指南和反馈方式。
- `tests/`：人工回归场景。
- `.github/ISSUE_TEMPLATE/`：公开反馈模板。

## 当前状态

当前版本是 GitHub Early Access。自动检查会验证 Skill 结构、Excel 表结构、Active Version、行程和版本记录的一致性；AI 行为仍需按回归场景进行客户端验证。

产品设计覆盖和明确延期项见 [`docs/design-coverage.md`](docs/design-coverage.md)。

## 隐私

旅行档案可能包含精确日期、住宿、交通和同行者信息。公开 Issue 仅提交最小复现，删除姓名、订单号、联系方式、证件、精确住宿地址和凭据。

## License

MIT。第三方平台名称和商标归各自权利人所有。
