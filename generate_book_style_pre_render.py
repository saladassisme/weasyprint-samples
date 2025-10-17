#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用预渲染分页计算方案生成传记PDF - 终极方案
通过两次渲染获取准确的目录页码
"""

import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import pdfplumber
import qrcode

def generate_qr_code(url, filename):
    """生成二维码图片"""
    if not url or not url.strip():
        return None
    
    try:
        # 创建二维码实例
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # 添加数据
        qr.add_data(url)
        qr.make(fit=True)
        
        # 创建图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存图片
        img.save(filename)
        print(f"  二维码生成成功: {filename}")
        return filename
        
    except Exception as e:
        print(f"  二维码生成失败: {e}")
        return None

def generate_chapter_qr_codes(chapters):
    """为所有章节生成二维码"""
    print("\n[1.5/3] 生成章节二维码...")
    
    # 创建二维码目录
    qr_dir = Path("qr_codes")
    qr_dir.mkdir(exist_ok=True)
    
    for chapter in chapters:
        if 'qr_link' in chapter and chapter['qr_link']:
            qr_filename = qr_dir / f"chapter_{chapter['id']}_qr.png"
            generated_qr = generate_qr_code(chapter['qr_link'], str(qr_filename))
            
            if generated_qr:
                # 更新章节数据，添加生成的二维码路径
                chapter['qr_code'] = str(qr_filename)
            else:
                # 如果生成失败，使用默认二维码
                chapter['qr_code'] = "qrcode.jpg"
        else:
            # 如果没有链接，使用默认二维码
            chapter['qr_code'] = "qrcode.jpg"
    
    print("章节二维码生成完成")


def create_pre_render_template():
    """创建预渲染模板（无目录，带页码标记）"""
    template_content = '''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="author" content="{{ book_info.author }}">
    <title>{{ book_info.title }}</title>
    <style>
        /* 自定义字体定义 */
        @font-face {
            font-family: 'CustomTitle';
            src: url('fonts/custom-title.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        
        @font-face {
            font-family: 'CustomKai';
            src: url('fonts/custom-kai.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        
        /* 自定义页面尺寸和样式 */
        @page {
            margin: 2cm 2cm 2cm 2cm;
            size: 140mm 210mm;
        }

        @page :left {
            @bottom-left {
                content: counter(page);
                position: absolute;
                z-index: -1;
                font-size: 10pt;
            }
            @bottom-right {
                content: string(heading);
                position: absolute;
                z-index: -1;
                font-size: 10pt;
            }
        }

        @page :right {
            @bottom-left {
                content: string(heading);
                position: absolute;
                z-index: -1;
                font-size: 10pt;
            }
            @bottom-right {
                content: counter(page);
                position: absolute;
                z-index: -1;
                font-size: 10pt;
            }
        }

        @page full {
            @bottom-right { content: none; }
            @bottom-left { content: none; }
            background: url('file:///C:/Users/xutin/Desktop/小工具/weasyprint-samples/cover_bg.jpg') no-repeat center center;
            background-size: cover;
            margin: 0;
            size: 140mm 210mm;
        }

        @page clean {
            @bottom-right { content: none; }
            @bottom-left { content: none; }
            size: 140mm 210mm;
        }

        @page back-cover {
            @bottom-right { content: none; }
            @bottom-left { content: none; }
            background: url('file:///C:/Users/xutin/Desktop/小工具/weasyprint-samples/封底.jpg') no-repeat center center;
            background-size: cover;
            margin: 0;
            size: 140mm 210mm;
        }

        @page chapter-image :left {
            @bottom-left { 
                content: counter(page);
                font-size: 10pt;
                color: black;
                text-shadow: none;
            }
            @bottom-right { 
                content: string(heading);
                font-size: 10pt;
                color: black;
                text-shadow: none;
            }
            margin: 2cm 2cm 2cm 2cm;
            size: 140mm 210mm;
        }

        @page chapter-image :right {
            @bottom-right { 
                content: counter(page);
                font-size: 10pt;
                color: black;
                text-shadow: none;
            }
            @bottom-left { 
                content: string(heading);
                font-size: 10pt;
                color: black;
                text-shadow: none;
            }
            margin: 2cm 2cm 2cm 2cm;
            size: 140mm 210mm;
        }

        @page chapter-content :left {
            @bottom-left { 
                content: counter(page);
                font-size: 10pt;
            }
            @bottom-right { 
                content: string(heading);
                font-size: 10pt;
            }
            margin: 2cm 2cm 2cm 2cm;
            size: 140mm 210mm;
        }

        @page chapter-content :right {
            @bottom-right { 
                content: counter(page);
                font-size: 10pt;
            }
            @bottom-left { 
                content: string(heading);
                font-size: 10pt;
            }
            margin: 2cm 2cm 2cm 2cm;
            size: 140mm 210mm;
        }

        /* 基础样式 */
        html {
            counter-reset: h2-counter;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
            font-size: 12pt;
        }
        
        body {
            margin: 0;
            color: #333;
        }
        
        /* 段落样式 */
        p {
            line-height: 1.8;
            text-align: justify;
            text-indent: 2em;
            margin: 1em 0;
            font-size: 14pt;
            font-family: "SimSun", "宋体", "NSimSun", serif;
        }
        
        /* 标题样式 */
        h1 {
            position: absolute;
            visibility: hidden;
        }
        
        h2 {
            color: #333;
            counter-increment: h2-counter;
            display: flex;
            flex-direction: column;
            font-family: 'CustomTitle', "STKaiti", "KaiTi", "楷体", "华文行楷", "STXingkai", serif;
            font-size: 2.2em;
            height: auto;
            justify-content: flex-start;
            margin: 0;
            padding-top: 0.3cm;
            padding-bottom: 0.1cm;
            string-set: heading content();
            text-align: center;
            text-shadow: none;
        }
        
        h2::before {
            content: "第" counter(h2-counter) "篇 ";
            display: inline;
            font-size: 0.8em;
            color: #666;
            margin-right: 0.3em;
        }
        
        h3 {
            font-size: 1.8em;
            text-align: center;
            margin: 1.5em 0;
            color: #333;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
        }
        
        /* 章节样式 */
        section {
            break-after: right;
        }
        
        .chapter {
            break-after: right;
            position: relative;
            padding-top: 0cm;
        }
        
        /* 封面样式 */
        .cover-page {
            page: full;
            color: #2c2c2c;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
            padding: 2cm 2cm 3cm 2cm;
            margin: 0;
            height: 100%;
        }
        
        .cover-title {
            font-size: 2.8em;
            font-weight: bold;
            margin-bottom: 8cm;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 2;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
            letter-spacing: 0.15em;
            color: #1a1a1a;
            margin-top: 2.5cm;
        }
        
        .cover-author {
            font-size: 1.4em;
            position: relative;
            z-index: 2;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
            letter-spacing: 0.1em;
            color: #2c2c2c;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
            margin-bottom: 2cm;
        }
        
        /* 封底样式 */
        .back-cover {
            page: back-cover;
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: #666;
        }
        
        .back-cover-content {
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
            font-size: 1.2em;
            opacity: 0.7;
        }
        
        /* 空白页样式 */
        .blank-page {
            page: clean;
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            break-before: right;
            page-break-before: right;
        }
        
        /* 章节左右分页布局 */
        .chapter-image-page {
            page: chapter-image;
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            break-before: left;
            page-break-before: left;
        }
        
        .chapter-image {
            width: 10cm;
            height: auto;
            object-fit: contain;
            display: block;
        }
        
        .chapter-image-page img {
            max-width: 100%;
            max-height: 100%;
            object-fit: cover;
        }
        
        .chapter-content-page {
            page: chapter-content;
            padding: 0cm;
            break-before: right;
            page-break-before: right;
        }
        
        .chapter-qr {
            text-align: center;
            margin: 0 0 0.5cm 0;
        }
        
        .chapter-qr img {
            max-width: 2cm;
            max-height: 2cm;
            border-radius: 4px;
        }
        
        .chapter-qr-label {
            font-size: 9pt;
            color: #666;
            margin-top: 0.2cm;
            font-family: "Microsoft YaHei", sans-serif;
        }
        
        /* 作者信息页 */
        .author-info {
            page: clean;
            text-align: center;
        }
        
        .author-info h3 {
            font-size: 1.8em;
            margin-bottom: 1.5em;
            color: #333;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
        }
        
        .author-info p {
            font-size: 13pt;
            line-height: 1.6;
            text-indent: 0;
            margin: 1em 0;
            color: #555;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
        }
        
        /* 目录样式 */
        .contents {
            page: clean;
            counter-reset: page 1;
        }
        
        .contents h3 {
            font-size: 2em;
            text-align: center;
            margin-bottom: 1.5em;
            color: #333;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
        }
        
        .contents ul {
            list-style: none;
            padding: 0;
        }
        
        .contents li {
            margin: 1.2em 0;
            font-size: 13pt;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
        }
        
        .contents a {
            color: #333;
            text-decoration: none;
            display: block;
            padding: 0.3em 0;
            font-family: 'CustomKai', "KaiTi", "楷体", "STKaiti", serif;
        }
        
        /* 页码标记样式 */
        .page-marker {
            color: red;
            font-weight: bold;
            font-size: 12pt;
            margin-left: 1em;
        }
        
        /* 图片样式 */
        img {
            display: block;
            margin: 1.5em auto;
            max-width: 80%;
        }
        
        aside {
            display: flex;
            justify-content: center;
        }
        
        aside figure {
            flex: none;
            margin: 0;
            padding: 1em;
            text-align: center;
        }
        
        aside img {
            border: 0.4mm solid white;
            border-radius: 50%;
            margin: 0 auto;
            max-width: 14mm;
        }
    </style>
</head>
<body>
    <h1>{{ book_info.title }}</h1>
    
    <!-- 封面页 -->
    <section class="cover-page">
        <div class="cover-title">{{ book_info.title }}</div>
        <div class="cover-author">作者 {{ book_info.author }}</div>
    </section>
    
    <!-- 作者信息页 -->
    <section class="author-info">
        <h3>关于作者</h3>
        <p>{{ book_info.author }}，生于1948年5月，松江华阳桥长楼村人。</p>
        <p>一生从事教育工作，从民办教师到食堂管理，见证了时代变迁。</p>
        <p>虽历经坎坷，但始终保持乐观坚韧的人生态度。</p>
        <p>本书记录了他从童年到暮年的人生历程，展现了一个普通人的不凡人生。</p>
    </section>
    
    <!-- 目录页（预渲染版本，带页码标记） -->
    <section class="contents">
        <h3>目录<span class="page-marker">[页码: TOC]</span></h3>
        <ul>
            {% for chapter in chapters %}
            <li><a href="#chapter-{{ chapter.id }}-title">第{{ chapter.id }}篇 {{ chapter.title }}</a></li>
            {% endfor %}
        </ul>
    </section>
    
    <!-- 各章节内容 -->
    {% for chapter in chapters %}
    <!-- 章节图片页（偶数页，翻开后的左页） -->
    <section class="chapter-image-page">
        <img src="back_cover.jpg" alt="章节配图" class="chapter-image">
    </section>
    
    <!-- 章节内容页（奇数页，翻开后的右页） -->
    <section id="chapter-{{ chapter.id }}" class="chapter chapter-{{ chapter.id }} chapter-content-page">
        <h2 id="chapter-{{ chapter.id }}-title">{{ chapter.title }}<span class="page-marker">[页码: {{ chapter.id }}]</span></h2>
        
        <!-- 二维码区域 -->
        <div class="chapter-qr">
            {% if chapter.qr_code %}
            <img src="{{ chapter.qr_code }}" alt="{{ chapter.title }}二维码">
            {% else %}
            <img src="qrcode.jpg" alt="{{ chapter.title }}二维码">
            {% endif %}
            <div class="chapter-qr-label">扫码听故事</div>
        </div>
        
        {% for paragraph in chapter.content %}
        <p>{{ paragraph }}</p>
        {% endfor %}
        
        {% if chapter.images %}
        {% for image in chapter.images %}
        <aside>
            <figure>
                <img src="{{ image.url }}" alt="{{ image.alt }}">
                <figcaption>{{ image.caption }}</figcaption>
            </figure>
        </aside>
        {% endfor %}
        {% endif %}
    </section>
    {% endfor %}
    
    <!-- 封底页 -->
    <section class="back-cover">
        <div class="back-cover-content">
            <p></p>
        </div>
    </section>
</body>
</html>'''
    
    return template_content

def extract_page_numbers_from_pdf(pdf_path):
    """从PDF中提取页码信息"""
    print(f"\n[3/5] 解析PDF提取页码信息: {pdf_path}")
    
    chapter_pages = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    # 查找页码标记 [页码: X]
                    matches = re.findall(r'\[页码: (\d+)\]', text)
                    for chapter_id in matches:
                        chapter_id = int(chapter_id)
                        if chapter_id not in chapter_pages:
                            chapter_pages[chapter_id] = page_num
                            print(f"  第{chapter_id}篇 -> 页码 {page_num}")
    
    except Exception as e:
        print(f"  警告：解析PDF时出错: {e}")
        # 使用估算值作为备选
        for i in range(1, 7):  # 假设有6章
            chapter_pages[i] = 3 + (i - 1) * 2 + 1
    
    return chapter_pages

def generate_book_style_pdf_pre_render():
    """使用预渲染分页计算方案生成传记PDF"""
    
    print("=" * 60)
    print("使用预渲染分页计算方案生成传记 PDF (终极方案)")
    print("=" * 60)
    
    # 配置文件路径
    JSON_PATH = "biography_data.json"
    TEMPLATE_PATH = "templates/biography_book_style_v3.html"
    PRE_RENDER_PDF_PATH = "output/顾火良回忆录_预渲染版.pdf"
    OUTPUT_PDF_PATH = "output/顾火良回忆录_Book风格_v3_预渲染终极版.pdf"
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建模板目录
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    
    try:
        # 1. 读取 JSON 数据
        print(f"\n[1/5] 读取 JSON 数据: {JSON_PATH}")
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        print(f"成功读取数据：{book_data['book_info']['title']}")
        
        generate_chapter_qr_codes(book_data['chapters'])
        # 显示目录信息
        print("\n目录信息：")
        for chapter in book_data['chapters']:
            print(f"  第{chapter['id']}篇 {chapter['title']}")
        
        # 2. 第一次渲染（预渲染，无目录，带页码标记）
        print(f"\n[2/5] 第一次渲染（预渲染，带页码标记）...")
        
        # 创建预渲染模板
        pre_render_template = create_pre_render_template()
        
        # 使用Jinja2渲染预渲染模板
        env = Environment(loader=FileSystemLoader('.'))
        template = env.from_string(pre_render_template)
        html_content_pre = template.render(**book_data)
        
        # 生成预渲染PDF
        base_url = str(Path(".").absolute())
        html_obj_pre = HTML(string=html_content_pre, base_url=base_url)
        
        html_obj_pre.write_pdf(
            PRE_RENDER_PDF_PATH,
            optimize_images=True,
            jpeg_quality=95,
            dpi=300,
            presentational_hints=True
        )
        print(f"预渲染PDF生成成功: {PRE_RENDER_PDF_PATH}")
        
        # 3. 解析预渲染PDF，提取页码信息
        chapter_pages = extract_page_numbers_from_pdf(PRE_RENDER_PDF_PATH)
        
        # 4. 更新章节数据中的页码
        print(f"\n[4/5] 更新章节页码数据...")
        for i, chapter in enumerate(book_data['chapters'], 1):
            if i in chapter_pages:
                chapter['page'] = chapter_pages[i]
                print(f"  更新：第{chapter['id']}篇 -> 页码 {chapter['page']}")
        
        # 5. 第二次渲染（最终版本，包含准确页码的目录）
        print(f"\n[5/5] 第二次渲染（最终版本，包含准确目录）...")
        
        # 加载最终模板
        template_file = Path(TEMPLATE_PATH)
        template_dir = str(template_file.parent)
        template_name = template_file.name
        
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        
        # 渲染最终HTML
        html_content_final = template.render(**book_data)
        
        # 保存调试 HTML
        debug_html_path = OUTPUT_PDF_PATH.replace('.pdf', '_debug.html')
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content_final)
        print(f"调试 HTML 已保存: {debug_html_path}")
        
        # 生成最终PDF
        html_obj_final = HTML(string=html_content_final, base_url=base_url)
        
        html_obj_final.write_pdf(
            OUTPUT_PDF_PATH,
            optimize_images=True,
            jpeg_quality=95,
            dpi=300,
            presentational_hints=True
        )
        
        print(f"最终PDF生成成功!")
        
        print(f"\n任务完成!")
        print(f"预渲染PDF路径: {Path(PRE_RENDER_PDF_PATH).absolute()}")
        print(f"最终PDF路径: {Path(OUTPUT_PDF_PATH).absolute()}")
        if Path(OUTPUT_PDF_PATH).exists():
            print(f"文件大小: {Path(OUTPUT_PDF_PATH).stat().st_size / 1024:.2f} KB")
        
        print("=" * 60)
        print("预渲染分页计算方案 PDF 生成成功！(终极方案)")
        print(f"请打开查看: {Path(OUTPUT_PDF_PATH).absolute()}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = generate_book_style_pdf_pre_render()
    
    if success:
        print("\n结束处理")
        
    else:
        print("\n生成失败，请检查错误信息")

if __name__ == "__main__":
    main()
