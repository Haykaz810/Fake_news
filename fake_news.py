import urllib.request
from bs4 import BeautifulSoup
from googlesearch import search
import telebot

TOKEN = '1771672528:AAEz4dMaIoPzu4ghzkzoiwuIr7iykoSOcxk'
bot = telebot.TeleBot(token=TOKEN)
API_Key = "87395221864d4fa7a9319a0afc33b986"


class Text:
    """url address is processed here"""
    def __init__(self, url):
        self.url = url
        self.html = urllib.request.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.html, features="html.parser")
        self.list = []

    """take all the text information from the HTML code"""
    def html_text(self):
        for script in self.soup(["script", "style"]):
            script.extract()

        text = self.soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text

    """take all links from the HTML code"""
    def take_links(self):
        for line in self.soup.find_all('a'):
            self.list.append(line.get('href'))

        link = []
        for i in range(len(self.list)):
            if self.list[i][:4] == "http":
                link.append(self.list[i])
        self.list.clear()
        return link


class Analysis(Text):
    """the text information is analyzed here"""
    def __init__(self, url):
        super().__init__(url)

    """search for information here"""
    def search(self):
        list = []
        for j in search(self.html_text(),
                        'com', 'en'):
            if j != self.url:
                list.append(j)
                if len(list) == 4:
                    break
        return list

    """here text information is compared"""
    def comparison(self):
        list = []
        for i in range(len(self.search())):
            html = urllib.request.urlopen(self.search()[i]).read()
            soup = BeautifulSoup(html, features="html.parser")
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            one_bigrams = set(self.html_text())
            all_bigrams = set(text)
            overlap = len(one_bigrams & all_bigrams)
            formula = (overlap * 2.0 / (len(one_bigrams) + len(all_bigrams)))
            list.append(formula)
        if sum(list) > 3.6:
            return "this is link is not fake"
        else:
            return "this is link is fake"


if __name__ == '__main__':
    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if message.text[:4] == "http":
            a = Analysis(message.text)
            a.search()
            a.comparison()
            if a.comparison() == "this is link is not fake":
                bot.send_message(message.chat.id, "This is link is not fake")
            else:
                bot.send_message(message.chat.id, "This is link fake")
        else:
            bot.send_message(message.chat.id, "This is not link")


    bot.polling(none_stop=True, interval=0)