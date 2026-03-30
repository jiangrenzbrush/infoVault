# 信息管家

一个给 Windows 本地使用的小程序，用来集中记录平时重要的信息，避免反复翻聊天记录。

适合记录的内容：
- 学习网站账号、密码、备注
- 软件授权和注册码
- 家庭事务或重要提醒
- 各类平台登录信息
- 从 Word 文档导入的账号密码整理结果

## 主要功能

- 本地保存，不上传到云端
- 按日期、分类、重要级别筛选
- 关键词搜索
- 编辑已有记录时，可选择“覆盖当前记录”或“保存为新记录”
- 左侧记录列表支持颜色标记和分类自动配色
- 支持导出通用文本备份，再导入恢复
- 支持从 `DOCX` 文档中导入账号密码并自动分类
- 一键复制账号和密码
- 支持直接打开记录里的网站
- 敏感字段使用当前 Windows 账户进行本地加密保存

## 项目文件

- `main.py`：程序入口
- `infovault_app.py`：界面逻辑
- `infovault_storage.py`：本地数据库和加密存储
- `infovault_docx_import.py`：DOCX 导入和自动分类
- `infovault_i18n.py`：中英文界面文本
- `启动信息管家.bat`：本地启动脚本
- `信息管家.spec`：PyInstaller 打包配置

## 本地运行

```powershell
cd C:\Users\yitia\Documents\InfoVault
python main.py
```

## 打包 EXE

```powershell
cd C:\Users\yitia\Documents\InfoVault
python -m PyInstaller --noconfirm --clean --onefile --windowed --name 信息管家 main.py
```

打包后的文件默认在：

```text
C:\Users\yitia\Documents\InfoVault\dist\信息管家.exe
```

## 数据位置

默认数据库位置：

```text
C:\Users\yitia\Documents\InfoVault\data\vault.db
```

## 发布到 GitHub 的建议

- GitHub 仓库里建议只放源码，不要提交 `data/` 里的个人数据。
- `dist/` 和 `build/` 建议不进仓库，成品 `exe` 可以单独发到 GitHub Releases。
- 如果你要公开仓库，导出的备份文件和数据库都不要上传。

## 这次已经整理好的发布内容

- GitHub 源码包：适合上传到仓库
- Windows 成品包：适合上传到 Releases

## 后续还可以继续加的功能

- 导入预览
- 主密码锁
- 到期提醒
- 附件上传
- 桌面快捷方式自动创建
