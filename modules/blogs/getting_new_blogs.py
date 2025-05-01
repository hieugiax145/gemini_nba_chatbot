import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--headless=new')  # Chạy không hiển thị GUI
options.add_argument('--disable-dev-shm-usage')  # Tránh lỗi bộ nhớ
options.add_argument('--incognito')  # Mở ở chế độ ẩn danh
options.add_argument('--disable-notifications')  # Tắt thông báo từ trình duyệt
options.add_argument('--disable-extensions')  # Tắt tất cả extensions

driver = webdriver.Chrome(options=options)


class GettingNewBlogs:
    def __init__(self):
        self.links = []
        self.blogs = []

    def get_new_blogs(self):
        self.get_link_blogs()
        for link in self.links:
            self.get_article(link)

        return self.blogs

    def get_link_blogs(self):
        link_page = "https://www.nba.com/warriors/category/news-blogs"
        driver.get(link_page)
        time.sleep(1)

        layout_columns = driver.find_element(By.CLASS_NAME, 'LayoutColumns_left__sQqWc')
        link_blogs = layout_columns.find_elements(By.TAG_NAME, 'a')
        for blog in link_blogs:
            link = blog.get_attribute('href')
            self.links.append(link)

    def get_article(self, link_page):
        driver.get(link_page)
        time.sleep(1)

        articles = driver.find_elements(By.TAG_NAME, 'article')
        for article in articles:
            self.get_info_blog(article=article)

    def get_info_blog(self, article):
        img_cover = article.find_element(By.TAG_NAME, 'img').get_attribute('src')
        title = article.find_element(By.TAG_NAME, 'h1').text
        subtitle = article.find_element(By.TAG_NAME, 'h2').text
        author_divs = article.find_elements(By.CSS_SELECTOR, 'div[data-testid^="author-"]')
        author = author_divs[0].find_element(By.TAG_NAME, 'a').text if author_divs else "Unknown"
        time_box = article.find_element(By.CLASS_NAME, 'articleDateTime')
        date_posted = time_box.find_element(By.CLASS_NAME, 'font-bold').text
        time_posted = time_box.find_element(By.CLASS_NAME, 'ml-2').text
        tags = [tag.text for tag in article.find_element(By.CLASS_NAME, 'tags').find_elements(By.TAG_NAME, 'a')]
        blog = {
            'img_cover': img_cover,
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'post_time': f"{date_posted} {time_posted}",
            'content': self.get_content_blog(article.get_attribute("outerHTML")),
            'tags': tags
        }

        self.blogs.append(blog)

    def get_content_blog(self, article):
        soup = BeautifulSoup(article, 'html.parser')

        # Tìm phần tử chứa thông tin bài viết (sau phần ngày đăng bài)
        article_content = soup.find('div', class_='ArticleContent_articleContent__3_8sq')

        # Lấy tất cả các đoạn văn bản (p) và bảng (table)
        text_elements = article_content.find_all(['p', 'table'])

        # Tạo phần HTML chỉ chứa nội dung bài viết
        html_output = '<div>'

        # Duyệt qua các phần tử và xử lý chúng
        for element in text_elements:
            if element.name == 'table':
                # Nếu phần tử là bảng, thêm nó vào HTML với lớp 'article-table'
                html_output += '<table class="article-table">'
                html_output += element.prettify()  # Thêm nội dung bảng
                html_output += '</table>'
            else:
                # Nếu phần tử là đoạn văn, thêm nó vào HTML với lớp 'article-text'
                html_output += f'<p class="article-text">{element.get_text()}</p>'

        # Đóng HTML
        html_output += '</div>'

        return html_output

