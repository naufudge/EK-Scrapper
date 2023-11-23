from bs4 import BeautifulSoup
import httpx

# Modified for full automation

def is_news_mihaaru(soup: BeautifulSoup) -> bool:
    categories_parent = soup.find('div', class_="container flex px-4 mx-auto mt-10 mb-3 text-faseyha text-21px text-warm-grey-two xl:px-0")
    # categories = [category['href'] for category in categories_parent.find_all('a')]
    categories = [category['href'].lower() for category in categories_parent.find_all('a')]

    for each in categories:
        if "news" in each:
            return True
    else:
        return False

def is_news_sun(soup: BeautifulSoup) -> bool:
    tags = [each['href'].split('/')[-1].lower() for each in soup.find('div', class_="component-article-tag").find_all('a')]

    if 'news' in tags and not 'filaavalheh' in tags:
        return True
    else:
        return False

class NewsScrapping:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def Sun(self, url):
        results = {'url': url}
        try:
            page = await self.client.get(url)
        except httpx.UnsupportedProtocol as e:
            return f"{url} is not a URL"

        if page.status_code < 400:
            soup = BeautifulSoup(page.content, 'html.parser')
            if not is_news_sun(soup):
                return None
            
            article_title = soup.find('div', class_='component-article-title')
            results['title'] = article_title.find('h1').text

            # Finds author name
            article_author = soup.find('div', class_='author')
            if (article_author.find('span', class_='name') != None):
                results['author'] = article_author.find('span', class_='name').text
            else:
                results['author'] = ""

            # Finds article picture link
            if (soup.find('div', class_="component-article-featured") != None):
                article_pic = soup.find('div', class_='component-article-featured')
                try:
                    results['pic'] = article_pic.find('img')['src'] # Picutre link as a string
                except (AttributeError, TypeError) as error:
                    results['pic'] = "" # No picture
            elif (soup.find('div', class_="inline_image") != None) or (soup.find('div', class_="player") != None):
                article_pic = soup.find('div', class_="inline_image")
                try:
                    results['pic'] = article_pic.find('img')['src']
                except AttributeError:
                    results['pic'] = "" # No picture

            #Finds all the main body writing of the article
            article_main = soup.find('div', class_='component-article-content clearfix')
            results['paras'] = article_main.find_all('p')
            return results
        else:
            return None

    async def Mihaaru(self, url):
        results = {'url': url}
        try:
            page = await self.client.get(url)
        except httpx.UnsupportedProtocol as e:
            return f"{url} is not a URL"
        if page.status_code < 400:
            soup = BeautifulSoup(page.content, 'html.parser')
            if not is_news_mihaaru(soup):
                return None
            
            # Find the Title
            results['title'] = soup.find('h1').text

            # Find the Author and time
            article_author = soup.find('div', class_="text-center px-4 sm:flex items-center justify-center space-x-2")
            if (article_author != None):
                try:
                    results['author'] = article_author.find('a').text.strip()
                except AttributeError:
                    results['author'] = article_author.text.strip()
            else:
                results['author'] = ""

            # Find Article Picture Link

            article_pic = soup.find('div', class_="w-full lg:max-w-40rem xl:max-w-3xl")
            try:
                results['pic'] = article_pic.find('img')['src']
            except TypeError:
                results['pic'] = ""

            # Find all the main body wiriting of the article
            article_main = soup.find('div', class_="flex-1 lg:pr-4 lg:border-r lg:border-pale-grey mt-8 w-full")
            # results['paras'] = article_main.find_all('p')
            paras = article_main.find_all('p')
            for para in paras:
                try:
                    if "text-lg" in para['class'] or "text-xs" in para['class']:
                        paras.remove(para)
                except KeyError:
                    pass
            results['paras'] = paras
            return results
        else:
            return None

    async def President(self, url):
        results = {'url': url}
        try:
            page = await self.client.get(url)
        except httpx.UnsupportedProtocol as e:
            return f"{url} is not a URL"
        if page.status_code < 400:
            soup = BeautifulSoup(page.content, 'html.parser')
            #Find the Title
            article_title = soup.find('div', class_='col-sm-9')
            results['title'] = article_title.find('h1').text

            #Find the Author name and time
            results['author'] = ""
            # time = soup.find('div', class_="small-text").text

            #Find Article Picture Link and it's caption
            try:
                results['pic'] = article_title.find('img')['src']
            except TypeError:
                results['pic'] = ""
            #Finds all the main body writing of the article
            article_main = soup.find('div', class_='article-body')
            results['paras'] = article_main.find_all('p')
        return results

    async def Avas(self, url):
        results = {'url': url}
        try:
            page = await self.client.get(url)
        except httpx.UnsupportedProtocol as e:
            return f"{url} is not a URL"
        if page.status_code < 400:
            soup = BeautifulSoup(page.content, 'html.parser')
            # Find the Title
            results['title'] = soup.find('h1').text

            # Find the Author and time
            article_author_div = soup.find('div', class_="font-waheed text-grey ml-3 pl-3 text-lg border-l border-grey border-dotted")
            if (article_author_div != None):
                article_author = article_author_div.find('a')
                results['author'] = article_author.text
            else:
                results['author'] = ""

            # Find Article Picture Link
            article_pic = soup.find('figure', class_="leading-zero rtl relative")
            results['pic'] = article_pic.find('img')['src']

            # Find all the main body wiriting of the article
            article_main = soup.find('div', class_="post_content ml-0 md:ml-10")
            results['paras'] = article_main.find_all('p')
        return results
