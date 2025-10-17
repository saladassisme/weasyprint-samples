# 自定义字体使用指南

## 📁 字体文件放置

将您的字体文件放在 `fonts/` 目录下：

```
weasyprint-samples/
├── fonts/
│   ├── custom-title.ttf     # 标题字体（书法风格）
│   ├── custom-body.ttf      # 正文字体（宋体风格）
│   └── custom-kai.ttf       # 楷体字体
├── templates/
├── output/
└── ...
```

## 🔧 支持的字体格式

- **TTF** (TrueType Font) - 推荐
- **OTF** (OpenType Font) - 推荐
- **WOFF** (Web Open Font Format) - 支持
- **WOFF2** - 支持

## 📝 字体文件命名建议

### 标题字体（书法风格）
- `custom-title.ttf`
- `calligraphy-title.ttf`
- `handwriting-title.ttf`

### 正文字体（宋体风格）
- `custom-body.ttf`
- `songti-body.ttf`
- `serif-body.ttf`

### 楷体字体
- `custom-kai.ttf`
- `kaiti-custom.ttf`
- `classical-kai.ttf`

## 🎨 字体使用位置

### CustomTitle（标题字体）
- 章节标题 (h2)
- 封面标题
- 大标题

### CustomBody（正文字体）
- 文章正文段落 (p)
- 主要内容文本

### CustomKai（楷体字体）
- 目录
- 作者信息
- 封面作者名
- 二维码标签
- 版权信息
- 其他辅助文本

## ⚠️ 注意事项

1. **字体文件大小**：建议单个字体文件不超过 5MB
2. **字体授权**：确保您有使用该字体的合法授权
3. **字体质量**：选择高质量、清晰易读的字体
4. **备用字体**：CSS中已设置备用字体，如果自定义字体加载失败会自动使用系统字体

## 🚀 使用方法

1. 将字体文件放入 `fonts/` 目录
2. 确保文件名与CSS中的 `@font-face` 定义一致
3. 运行 `python generate_book_style.py` 生成PDF
4. 检查生成的PDF是否使用了您的自定义字体

## 🔍 调试技巧

如果字体没有生效：
1. 检查文件路径是否正确
2. 检查字体文件是否损坏
3. 查看生成的 `_debug.html` 文件
4. 确认字体格式是否被WeasyPrint支持
