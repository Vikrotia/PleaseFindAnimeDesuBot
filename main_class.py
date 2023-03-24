import requests
import urllib.parse
from bs4 import BeautifulSoup
import re

class AnimeFinder(object):
    def __init__(self):
        self.response = ''
        self.list_of_numb = []
        self.list_of_episode = []
        self.list_of_similarity = []
        self.info = []
        self.aboutanime = ''
        self.more = []
        self.more_str =''

    def FindAnimeByURL(self):
        res = 0
        self.response = self.response = requests.get("https://api.trace.moe/search?url={}".format(urllib.parse.quote_plus(
            self.fileURL))).json()
        if self.response['error'] != '':
            return res+1
        for i in self.response['result']:
            self.list_of_numb.append(i['anilist'])
            if i['episode'] == None:
                self.list_of_episode.append('Movie')
            else:
                self.list_of_episode.append(i['episode'])
            self.list_of_similarity.append(i['similarity'])
        return res

    def FindAnimeByScreen(self):
        res = 0
        self.response = requests.post("https://api.trace.moe/search", data=open(self.path , "rb"),
            headers={"Content-Type": "image/jpeg"}).json()
        if self.response['error'] != '':
            return res+1
        for i in self.response['result']:
            self.list_of_numb.append(i['anilist'])
            if i['episode'] == None:
                self.list_of_episode.append('Movie')
            else:
                self.list_of_episode.append(i['episode'])
            self.list_of_similarity.append(i['similarity'])
        return res

    def BringURL(self, fileURL):
        self.fileURL = fileURL

    def BringScreen(self, path):
        self.path = path

    def Check(self):
        for elem in self.list_of_numb:
            if self.ParsingAnilist(elem) == 1:
                return 0
            else:
                self.info = []
        print("Больше нет совпадений :(")

    def ParsingAnilist(self, elem):
        url = "https://anilist.co/anime/" + str(elem)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        dataset_class = []
        for i in soup.find_all(class_='data-set'):
            dataset_class.append(i.get_text())
        count_ep = 0
        en = 0
        for i in dataset_class:
            if 'Episodes' in i:
                self.info.append(i.replace('Episodes', '').strip())
            if 'Genres' in i:
                i = i.replace('Genres', '').strip()
                self.info.append(self.edit(i))
            if 'English' in i:
                self.info.append(i.replace('English', '').strip())
                en = 1
            if 'Season' in i:
                if not count_ep:
                    self.info.append(i.replace('Season', '').replace('\n', '').strip())
                    count_ep += 1
        for i in dataset_class:
            if en == 0 and 'Romaji' in i:
                self.info.append(i.replace('Romaji', '').strip())
        self.info.append(soup.find('img', class_='cover').get('src'))
        return 1

    def edit(self, elem):
        s = 0
        m = 0
        if 'Slice of Life' in elem:
            s = 1
            if 'Mahou Shoujo' in elem:
                m = 1
        elem = elem.replace('Slice of Life', '')
        elem = elem.replace('Mahou Shoujo', '')
        elem = re.sub(r'([A-Z])', r' \1', elem).strip()
        elem = elem.replace(' ', ', ')
        if s and m:
            if elem != '':
                elem = elem + ', '
            elem = elem + 'Slice of Life, Mahou Shoujo'
        elif s:
            if elem != '':
                elem = elem + ', '
            elem = elem + 'Slice of Life'
        elif m:
            if elem != '':
                elem = elem + ', '
            elem = elem + 'Mahou Shoujo'
        return elem

    def ProcessingURL(self, linkscreen):
        res = 0
        self.BringURL(linkscreen)
        if self.FindAnimeByURL() == 0:
            self.ParsingAnilist(self.list_of_numb[0])
            self.aboutanime = f"""Title: {self.info[3]}\nGenres: {self.info[2]}\nSeason: {self.info[1]}\nEpisodes: {self.info[0]}
Screenshot Episode: {self.list_of_episode[0]}\nSimilarity:  + {round(self.list_of_similarity[0], 2)}"""
        else:
            res = 1
        return res

    def ProcessingScreen(self, path):
        res = 0
        self.BringScreen(path)
        if self.FindAnimeByScreen() == 0:
            self.ParsingAnilist(self.list_of_numb[0])
            self.aboutanime = f"""Title: {self.info[3]}\nGenres: {self.info[2]}\nSeason: {self.info[1]}\nEpisodes: {self.info[0]}
Screenshot Episode: {self.list_of_episode[0]}\nSimilarity:  + {round(self.list_of_similarity[0], 2)}"""
        else:
            res = 1
        return res

    def MoreInforation(self):
        for i in self.list_of_numb:
            url = "https://anilist.co/anime/" + str(i)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            dataset_class = []
            for j in soup.find_all(class_='data-set'):
                dataset_class.append(j.get_text())
            count_ep = 0
            en = 0
            for title in dataset_class:
                if 'English' in title:
                    self.more.append(title.replace('English', '').strip())
                    en = 1
            for title in dataset_class:
                if en == 0 and 'Romaji' in title:
                    self.more.append(title.replace('Romaji', '').strip())
        self.more_str = f"""This screenshot may belong to anime such as:\n{self.more[1]} - {round(self.list_of_similarity[1],2)}
{self.more[2]} - {round(self.list_of_similarity[2],2)}\n{self.more[3]} - {round(self.list_of_similarity[3],2)}\n"""
        return self.more_str




