# 当前字体配置

## 📁 字体文件位置
请将您的字体文件放在以下位置：

```
weasyprint-samples/
├── fonts/
│   ├── custom-title.ttf     # ✅ 您的标题字体
│   └── custom-kai.ttf       # ✅ 您的楷体字体
```

## 🎨 字体使用配置

### 1. 标题字体 (CustomTitle)
- **文件**: `fonts/custom-title.ttf`
- **用途**: 章节标题、封面标题
- **备用字体**: STKaiti, KaiTi, 楷体, 华文行楷, STXingkai

### 2. 正文字体 (系统宋体)
- **字体**: SimSun, 宋体, NSimSun
- **用途**: 文章正文段落
- **说明**: 使用系统自带的宋体，无需自定义字体文件

### 3. 楷体字体 (CustomKai)
- **文件**: `fonts/custom-kai.ttf`
- **用途**: 目录、作者信息、其他辅助文本
- **备用字体**: KaiTi, 楷体, STKaiti

## ✅ 配置完成

当前配置已经优化：
- ✅ 标题使用您的自定义字体 `custom-title.ttf`
- ✅ 正文使用系统宋体（清晰易读）
- ✅ 其他文本使用您的自定义楷体 `custom-kai.ttf`

## 🚀 生成PDF

运行以下命令生成PDF：
```bash
python generate_book_style.py
```

输出文件：`output/顾火良回忆录_Book风格_v3_自定义字体版.pdf`
