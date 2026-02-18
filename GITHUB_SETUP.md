# 🚀 GitHub仓库创建指南

## 步骤1：在GitHub上创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `castmind`
   - **Description**: `播客智能流系统 - 自动化播客处理、AI深度分析、知识库集成`
   - **Visibility**: `Public` (或 `Private` 如果你希望私有)
   - **Initialize this repository with**: 不要勾选任何选项（我们已经有本地仓库）

3. 点击 "Create repository"

## 步骤2：连接本地仓库到GitHub

```bash
# 进入项目目录
cd ~/Project/castmind-new

# 添加远程仓库（替换 YOUR_USERNAME 为你的GitHub用户名）
git remote add origin https://github.com/YearsAlso/castmind.git

# 推送到GitHub
git push -u origin main
```

## 步骤3：设置GitHub Actions（可选但推荐）

### 创建CI工作流
在 `.github/workflows/ci.yml` 创建：

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: |
        python -m pytest tests/ -v
```

## 步骤4：设置分支保护规则

1. 进入仓库 Settings → Branches
2. 点击 "Add branch protection rule"
3. 配置规则：
   - Branch name pattern: `main`
   - Require a pull request before merging: ✓
   - Require approvals: 1
   - Require status checks to pass: ✓
   - Require branches to be up to date before merging: ✓

## 步骤5：设置README徽章（可选）

在README.md中添加：

```markdown
![GitHub](https://img.shields.io/github/license/YearsAlso/castmind)
![GitHub last commit](https://img.shields.io/github/last-commit/YearsAlso/castmind)
![GitHub issues](https://img.shields.io/github/issues/YearsAlso/castmind)
![GitHub stars](https://img.shields.io/github/stars/YearsAlso/castmind)
```

## 步骤6：创建开发分支

```bash
# 创建develop分支
git checkout -b develop
git push -u origin develop

# 设置develop分支保护
# 在GitHub仓库设置中为develop分支添加保护规则
```

## 步骤7：设置Git Flow工作流（推荐）

### 安装Git Flow
```bash
# macOS
brew install git-flow

# Ubuntu/Debian
sudo apt-get install git-flow

# 初始化Git Flow
git flow init -d
```

### 常用工作流
```bash
# 开始新功能
git flow feature start feature-name

# 完成功能
git flow feature finish feature-name

# 开始发布
git flow release start v1.0.0

# 完成发布
git flow release finish v1.0.0
```

## 步骤8：设置GitHub Pages（文档网站）

1. 进入仓库 Settings → Pages
2. 配置：
   - Source: `GitHub Actions`
   - 选择主题或自定义

3. 创建 `docs/index.md` 作为文档首页

## 步骤9：设置项目标签和里程碑

### 创建标签
```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 在GitHub上创建里程碑
1. 进入 Issues → Milestones
2. 点击 "New milestone"
3. 创建里程碑如 "v1.0.0"、"v2.0.0"

## 步骤10：设置代码所有者（CODEOWNERS）

创建 `.github/CODEOWNERS`：
```
# 默认代码所有者
* @YearsAlso

# 特定目录所有者
/src/core/ @YearsAlso
/docs/ @YearsAlso
```

## 步骤11：设置安全扫描

启用GitHub的安全功能：
1. Settings → Security & analysis
2. 启用：
   - Dependency graph
   - Dependabot alerts
   - Dependabot security updates
   - Code scanning

## 步骤12：设置讨论区（可选）

1. Settings → General → Features
2. 启用 "Discussions"

## 步骤13：设置项目看板

1. 点击顶部 "Projects" 标签
2. 点击 "New project"
3. 选择模板或创建自定义看板

## 步骤14：推送现有代码

如果你还没有推送代码：

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "feat: initial commit - CastMind播客智能流系统"

# 推送到GitHub
git push -u origin main
```

## 步骤15：验证设置

检查以下项目是否设置正确：

- [ ] 仓库可以访问：https://github.com/YearsAlso/castmind
- [ ] README.md正确显示
- [ ] 许可证文件存在
- [ ] .gitignore配置正确
- [ ] 分支保护规则生效
- [ ] CI工作流运行正常

## 故障排除

### 问题：推送被拒绝
```bash
# 强制推送（谨慎使用）
git push -f origin main

# 或先拉取更新
git pull origin main --rebase
```

### 问题：GitHub Actions失败
- 检查 `.github/workflows/ci.yml` 语法
- 查看Actions日志
- 确保Python版本兼容

### 问题：权限不足
- 确保你有仓库的写入权限
- 检查SSH密钥或访问令牌

## 下一步

1. **完善文档**：更新README，添加使用指南
2. **添加测试**：创建单元测试和集成测试
3. **设置CI/CD**：配置自动化部署
4. **添加贡献指南**：创建CONTRIBUTING.md
5. **发布版本**：创建第一个正式版本

## 有用的链接

- [GitHub Docs](https://docs.github.com/)
- [Git Flow工作流](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [开源项目最佳实践](https://opensource.guide/)