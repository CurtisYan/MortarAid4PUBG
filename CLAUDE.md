# CLAUDE.md

本文件定义 AI 在本仓库协作时必须遵守的提交前流程。

## 提交前强制要求

1. 在提交代码前，必须先更新 CHANGELOG.md。
2. CHANGELOG 必须新增一条“当日第 N 次更新（更新 #XXX）”记录。
3. 记录至少包含以下小节：
   - 新增（可选）
   - 修复（可选）
   - 优化（可选）
   - 影响文件（必填）
4. 同一天可能有多次提交，必须递增“第 N 次更新”和“更新 #XXX”。
5. 若本次提交无功能变化，也要写明“文档/重构/维护”类型变化。

## 提交信息建议

- 推荐使用简洁前缀：feat / fix / refactor / docs / chore
- 示例：
  - feat: add reset hotkey flow
  - fix: handle reset during point capture
  - docs: update changelog and usage notes

## AI 工作约束

- 不得跳过 CHANGELOG 更新直接提交。
- 不得覆盖或删除历史更新记录。
- 仅在确认变更内容后写入记录，避免虚构内容。
