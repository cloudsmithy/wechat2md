import requests
from bs4 import BeautifulSoup
import html2text
import re
import os
from flask import Flask, render_template, request, send_file
import io  # 用于在内存中创建文件对象

app = Flask(__name__)



# 将之前的提取逻辑放入一个独立的函数
def extract_wechat_article_to_markdown(url):
    """
    从微信公众号文章 URL 提取 Markdown 内容，包括标题。
    尝试多种方法获取文章标题。

    Args:
        url (str): 微信公众号文章的 URL。

    Returns:
        str: 转换后的 Markdown 内容（包含标题），如果失败则返回 None。
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)  # 增加超时时间
        response.raise_for_status()  # 检查 HTTP 请求是否成功
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # --- 1. 提取文章主标题 ---
        article_title = ""
        # 方法 A: 尝试从 <meta property="og:title"> 获取 (最推荐，用于社交分享的标准化标题)
        og_title_tag = soup.find('meta', property='og:title')
        if og_title_tag and 'content' in og_title_tag.attrs:
            article_title = og_title_tag['content'].strip()

        if not article_title:  # 如果 'og:title' 没有找到，尝试其他方法
            # 方法 B: 尝试从 <h2 id="activity-name"> 获取 (微信公众号常见的标题位置)
            title_tag_h2 = soup.find('h2', id='activity-name')
            if title_tag_h2:
                article_title = title_tag_h2.get_text(strip=True)

        if not article_title:  # 如果以上都没找到，尝试从 <title> 标签获取
            # 方法 C: 从 <title> 标签获取 (备用，格式可能不统一)
            title_tag_page = soup.find('title')
            if title_tag_page:
                full_title = title_tag_page.get_text(strip=True)
                # 尝试切割，移除公众号名称部分 (通常是 "文章标题 - 公众号名称")
                if ' - ' in full_title:
                    article_title = full_title.split(' - ')[0].strip()
                else:
                    article_title = full_title

        # --- 2. 提取文章内容 ---
        article_content_div = soup.find('div', id='js_content')
        if not article_content_div:
            print(f"DEBUG: URL {url} - 未找到文章内容区域（ID 为 'js_content' 的 div）。")
            return "错误：无法找到文章内容区域。可能是文章结构改变或已被删除。"

        # 处理图片 data-src 及清理冗余属性
        for img in article_content_div.find_all('img'):
            if 'data-src' in img.attrs:
                img['src'] = img['data-src']
            for attr in ['data-type', 'data-w', 'data-ratio', 'style']:
                if attr in img.attrs:
                    del img[attr]

        # 移除无关紧要的 script 和 style 标签
        for s in article_content_div(['script', 'style', 'noscript']):
            s.extract()

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        h.single_line_break = True
        h.pad_alt_text = True
        h.ignore_emphasis = False  # 保留粗体/斜体
        h.ul_item_mark = '  '  # 尝试将无序列表符号替换为两个空格
        h.list_indent = '    '  # 列表缩进
        h.ignore_tables = False  # 保留表格

        markdown_content = h.handle(str(article_content_div))

        # 清理多余的空行和空白
        markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
        markdown_content = markdown_content.strip()

        # --- 3. 将标题和内容组合成最终的 Markdown ---
        final_markdown = ""
        if article_title:
            final_markdown += f"# {article_title}\n\n"

        final_markdown += markdown_content

        return final_markdown

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: 网络请求错误: {e}")
        return f"网络请求错误: {e}. 请检查 URL 或网络连接。"
    except Exception as e:
        print(f"DEBUG: 发生错误: {e}")
        return f"处理错误: {e}"


@app.route('/', methods=['GET', 'POST'])
def index():
    markdown_output = None
    error_message = None
    original_url = ""

    if request.method == 'POST':
        original_url = request.form['wechat_url'].strip()
        if original_url:
            markdown_output = extract_wechat_article_to_markdown(original_url)
            if markdown_output and "错误：" in markdown_output:  # 检查是否是 extract 函數返回的错误信息
                error_message = markdown_output
                markdown_output = None  # 清空 markdown_output
        else:
            error_message = "请输入微信公众号文章 URL。"

    return render_template('index.html',
                           markdown_output=markdown_output,
                           error_message=error_message,
                           original_url=original_url)


@app.route('/download', methods=['POST'])
def download_markdown():
    markdown_content = request.form['markdown_content']
    # 从隐藏字段获取标题，并进行清理，用于文件名，避免特殊字符
    # 尝试从 markdown_content 的第一行解析标题，如果不存在，则使用默认标题
    title_from_md = ""
    if markdown_content.startswith('# '):
        title_from_md = markdown_content.split('\n')[0][2:].strip()

    clean_title = re.sub(r'[\\/:*?"<>|]', '', title_from_md).strip()
    if not clean_title:
        clean_title = "微信文章"  # 默认文件名

    # 使用 io.BytesIO 在内存中创建文件，而不是实际写入磁盘
    buffer = io.BytesIO()
    buffer.write(markdown_content.encode('utf-8'))
    buffer.seek(0)  # 将指针移回文件开头

    return send_file(
        buffer,
        mimetype='text/markdown',
        as_attachment=True,
        download_name=f'{clean_title}.md'
    )


if __name__ == '__main__':
    # Flask 默认运行在 5000 端口
    # debug=True: 开启调试模式，代码修改后会自动重启，并提供详细错误信息
    # host='0.0.0.0': 允许从外部访问此服务（如果您部署到服务器上，需要设置此项）
    app.run(debug=True, host='0.0.0.0', port=5001)
