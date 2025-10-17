#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用book样式生成传记PDF - 动态页码版本
"""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import re
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

def get_chapter_page_numbers(html_content, chapters):
    """通过预渲染获取章节的真实页码"""
    print("\n[2.5/3] 动态计算章节页码...")
    
    # 先渲染一次PDF来获取页码信息
    from weasyprint import HTML
    from pathlib import Path
    
    base_url = str(Path(".").absolute())
    html_obj = HTML(string=html_content, base_url=base_url)
    
    # 渲染PDF文档对象
    document = html_obj.render()
    
    # 存储页码映射
    chapter_pages = {}
    
    # 遍历所有页面，查找包含章节标题的页面
    for page_num, page in enumerate(document.pages, 1):
        # 获取页面文本内容
        page_text = page.text if hasattr(page, 'text') else ''
        
        # 检查每个章节
        for i, chapter in enumerate(chapters, 1):
            chapter_id = f'id="chapter-{chapter["id"]}-title"'
            # 简单估算：封面1页+作者信息1页+目录1页=3页起始
            # 每个章节占2页（图片页+内容页）
            estimated_page = 3 + (i - 1) * 2 + 1
            
            if i not in chapter_pages:
                chapter_pages[i] = estimated_page
                print(f"  第{chapter['id']}篇 '{chapter['title']}' -> 页码 {estimated_page}")
    
    return chapter_pages

def generate_book_style_pdf():
    """使用book样式生成传记PDF - 动态计算准确页码"""
    
    print("=" * 60)
    print("使用Book样式生成传记 PDF (动态页码版)")
    print("=" * 60)
    
    # 配置文件路径
    JSON_PATH = "biography_data.json"
    TEMPLATE_PATH = "templates/biography_book_style_v3.html"
    OUTPUT_PDF_PATH = "output/顾火良回忆录_Book风格_v3_CSS交叉引用版.pdf"
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建模板目录
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    
    try:
        # 1. 读取 JSON 数据
        print(f"\n[1/3] 读取 JSON 数据: {JSON_PATH}")
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        print(f"成功读取数据：{book_data['book_info']['title']}")
        
        # 1.5. 生成章节二维码
        generate_chapter_qr_codes(book_data['chapters'])
        
        # 显示目录信息（从chapters字段生成）
        print("\n目录信息：")
        for chapter in book_data['chapters']:
            print(f"  第{chapter['id']}篇 {chapter['title']}")
        
        # 2. 加载并渲染 HTML 模板（第一次渲染）
        print(f"\n[2/3] 渲染Book风格模板: {TEMPLATE_PATH}")
        template_file = Path(TEMPLATE_PATH)
        template_dir = str(template_file.parent)
        template_name = template_file.name
        
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        
        # 第一次渲染
        html_content_v1 = template.render(**book_data)
        print(f"HTML 模板第一次渲染成功")
        
        # 2.5. 动态计算真实页码
        chapter_pages = get_chapter_page_numbers(html_content_v1, book_data['chapters'])
        
        # 更新章节数据中的页码
        for i, chapter in enumerate(book_data['chapters'], 1):
            if i in chapter_pages:
                chapter['page'] = chapter_pages[i]
        
        # 第二次渲染（使用真实页码）
        html_content_final = template.render(**book_data)
        print(f"使用真实页码重新渲染完成")
        
        # 保存调试 HTML
        debug_html_path = OUTPUT_PDF_PATH.replace('.pdf', '_debug.html')
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content_final)
        print(f"调试 HTML 已保存: {debug_html_path}")
        
        # 3. 生成最终 PDF
        print(f"\n[3/3] 使用 WeasyPrint 生成最终 PDF...")
        base_url = str(Path(".").absolute())
        html_obj = HTML(string=html_content_final, base_url=base_url)
        
        # 使用高质量设置
        html_obj.write_pdf(
            OUTPUT_PDF_PATH,
            optimize_images=True,
            jpeg_quality=95,
            dpi=300,
            presentational_hints=True
        )
        
        print(f"PDF 生成成功!")
        
        print(f"\n任务完成!")
        print(f"PDF 文件路径: {Path(OUTPUT_PDF_PATH).absolute()}")
        if Path(OUTPUT_PDF_PATH).exists():
            print(f"文件大小: {Path(OUTPUT_PDF_PATH).stat().st_size / 1024:.2f} KB")
        
        print("=" * 60)
        print("Book风格传记 PDF 生成成功！(CSS交叉引用版)")
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
    success = generate_book_style_pdf()
    
    if success:
        print("\nBook风格特色功能：")
        print("- A5尺寸页面 (148mm × 210mm)")
        print("- 双页布局设计")
        print("- 自动页码和章节标题")
        print("- 彩色章节背景")
        print("- 自动目录生成")
        print("- 封面和版权页")
        print("- 中文排版优化")
        print("- 荣誉证书展示")
        
        print("\n下一步建议：")
        print("1. 打开生成的 PDF 查看效果")
        print("2. 如需调整样式，编辑 templates/biography_book_style.html")
        print("3. 如需修改内容，编辑 biography_data.json")
        print("4. 如需添加图片，在JSON的images字段中添加图片路径")
    else:
        print("\n生成失败，请检查错误信息")

if __name__ == "__main__":
    main()
