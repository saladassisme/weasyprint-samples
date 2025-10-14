#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用book样式生成传记PDF
"""

import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def generate_book_style_pdf():
    """使用book样式生成传记PDF"""
    
    print("=" * 60)
    print("使用Book样式生成传记 PDF")
    print("=" * 60)
    
    # 配置文件路径
    JSON_PATH = "biography_data.json"
    TEMPLATE_PATH = "templates/biography_book_style_v3.html"
    OUTPUT_PDF_PATH = "output/顾火良回忆录_Book风格_v3_封底修复=2版.pdf"
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建模板目录
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    
    try:
        # 1. 读取 JSON 数据
        print(f"\n[1/4] 读取 JSON 数据: {JSON_PATH}")
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        print(f"成功读取数据：{book_data['book_info']['title']}")
        
        # 2. 加载并渲染 HTML 模板
        print(f"\n[2/4] 渲染Book风格模板: {TEMPLATE_PATH}")
        template_file = Path(TEMPLATE_PATH)
        template_dir = str(template_file.parent)
        template_name = template_file.name
        
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        
        html_content = template.render(**book_data)
        print(f"HTML 模板渲染成功")
        
        # 保存调试 HTML
        debug_html_path = OUTPUT_PDF_PATH.replace('.pdf', '_debug.html')
        with open(debug_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"调试 HTML 已保存: {debug_html_path}")
        
        # 3. 生成 PDF
        print(f"\n[3/4] 使用 WeasyPrint 生成Book风格 PDF...")
        base_url = str(Path(".").absolute())
        html_obj = HTML(string=html_content, base_url=base_url)
        
        # 使用高质量设置
        html_obj.write_pdf(
            OUTPUT_PDF_PATH,
            optimize_images=True,
            jpeg_quality=95,
            dpi=300,
            presentational_hints=True
        )
        
        print(f"PDF 生成成功!")
        
        # 4. 完成
        print(f"\n[4/4] 任务完成!")
        print(f"PDF 文件路径: {Path(OUTPUT_PDF_PATH).absolute()}")
        if Path(OUTPUT_PDF_PATH).exists():
            print(f"文件大小: {Path(OUTPUT_PDF_PATH).stat().st_size / 1024:.2f} KB")
        
        print("=" * 60)
        print("Book风格传记 PDF 生成成功！")
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
