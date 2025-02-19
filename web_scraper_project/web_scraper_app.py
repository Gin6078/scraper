import streamlit as st
import requests
from bs4 import BeautifulSoup
import base64
from urllib.parse import urlparse
import time

def is_valid_url(url):
    """验证URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def scrape_webpage(url):
    try:
        # 验证URL
        if not is_valid_url(url):
            raise ValueError("无效的URL格式")

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 添加超时设置
        response = requests.get(url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code != 200:
            raise requests.RequestException(f"请求失败，状态码: {response.status_code}")
            
        response.encoding = response.apparent_encoding
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            raise ValueError(f"不支持的内容类型: {content_type}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
            
        text = soup.get_text()
        
        # 文本清理
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text.strip():
            raise ValueError("未找到有效的文本内容")
        
        return text
        
    except requests.Timeout:
        return "错误：请求超时，请检查网络连接或稍后重试"
    except requests.ConnectionError:
        return "错误：无法连接到服务器，请检查网络连接"
    except ValueError as e:
        return f"错误：{str(e)}"
    except requests.RequestException as e:
        return f"请求错误：{str(e)}"
    except Exception as e:
        return f"未知错误：{str(e)}"

def get_download_link(text, filename="webpage_content.txt"):
    """生成下载链接"""
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">点击下载文本文件</a>'

# Streamlit界面
st.title('网页文本内容爬取工具')

# 输入URL
url = st.text_input('请输入网页链接：')

if st.button('开始爬取'):
    if url:
        try:
            with st.spinner('正在爬取内容...'):
                # 添加进度条
                progress_bar = st.progress(0)
                progress_bar.progress(25)
                time.sleep(0.5)
                
                content = scrape_webpage(url)
                progress_bar.progress(75)
                time.sleep(0.5)
                
                if content.startswith("错误") or content.startswith("未知错误"):
                    st.error(content)
                else:
                    progress_bar.progress(100)
                    st.success('爬取完成！')
                    
                    # 显示预览
                    st.subheader('内容预览：')
                    preview_text = content[:1000] + ('...' if len(content) > 1000 else '')
                    st.text_area('', preview_text, height=200)
                    
                    # 提供下载链接
                    if len(content) > 0:
                        st.markdown(get_download_link(content), unsafe_allow_html=True)
                        st.info(f'文本总长度：{len(content)} 字符')
        except Exception as e:
            st.error(f"处理过程中发生错误：{str(e)}")
    else:
        st.error('请输入有效的网页链接！')

# 添加使用说明
st.markdown("""
### 使用说明：
1. 在输入框中粘贴要爬取的网页链接
2. 点击"开始爬取"按钮
3. 等待爬取完成
4. 可以预览内容并下载文本文件
""")