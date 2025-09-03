# Changelog Generator

这是一个基于 git tag 和 git diff 的变更日志生成工具。

This is a changelog generator tool based on git tags and git diff.

## 功能特点 / Features

- 🏷️ 自动获取所有 git tags / Automatically retrieves all git tags
- 📊 使用 git diff 生成变更统计 / Uses git diff to generate change statistics  
- 📝 生成格式化的 Markdown 变更日志 / Generates formatted Markdown changelog
- 🔄 显示未发布的变更 / Shows unreleased changes since last tag
- 📁 列出修改的文件 / Lists modified files
- 💻 显示提交信息 / Shows commit messages
- 📈 统计添加/删除的行数 / Counts added/deleted lines

## 使用方法 / Usage

```bash
# 输出到终端 / Output to terminal
python3 changelog_generator.py

# 保存到文件 / Save to file  
python3 changelog_generator.py CHANGELOG.md

# 查看帮助 / Show help
python3 changelog_generator.py --help

# 查看前20行 / View first 20 lines
python3 changelog_generator.py | head -20
```

## 输出格式 / Output Format

生成的变更日志包含以下信息：
The generated changelog includes:

- **[Unreleased]** - 自上次标签以来的未发布变更 / Unreleased changes since last tag
- **[v1.x.x]** - 每个版本标签的变更 / Changes for each version tag
- **Changes Summary** - 变更统计（文件数、行数）/ Change statistics (files, lines)
- **Commits** - 提交信息列表 / List of commit messages  
- **Modified Files** - 修改的文件列表 / List of modified files
- **Detailed Changes** - 详细的文件变更统计 / Detailed file change statistics

## 示例输出 / Example Output

```markdown
# Changelog

## [Unreleased]

**Changes Summary:**
- 2 files changed
- 45 lines added
- 12 lines deleted

**Commits:**
- abc1234 Add new feature
- def5678 Fix bug in search

**Modified Files:**
- `everything.py`
- `README.md`

## [v1.3.5] - 2025-09-03

**Changes Summary:**
- 10 files changed

**Commits:**
- 6ba8ee1 Bump version to 1.3.5 in documentation and application files

**Modified Files:**
- `.github/workflows/Standalone.yaml`
- `.gitignore`
- `LICENSE.md`
- ...
```

## 依赖要求 / Requirements

- Python 3.6+
- Git repository
- Git 命令行工具 / Git command line tools

## 注意事项 / Notes

1. 必须在 git 仓库中运行 / Must be run in a git repository
2. 需要至少一个 git tag / Requires at least one git tag for meaningful output
3. 浅克隆仓库可能显示有限的历史信息 / Shallow repositories may show limited history
4. 生成的 CHANGELOG.md 文件会被自动排除 / Generated CHANGELOG.md is automatically excluded in .gitignore