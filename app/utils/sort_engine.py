from app import db
from app.articles.models import Article
from sqlalchemy import select
from flask_login import current_user

import re


class Search:

    STOP_WORDS = [
        "a",
        "about",
        "above",
        "after",
        "again",
        "against",
        "ain",
        "all",
        "am",
        "an",
        "and",
        "any",
        "are",
        "aren",
        "aren't",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "couldn",
        "couldn't",
        "d",
        "did",
        "didn",
        "didn't",
        "do",
        "does",
        "doesn",
        "doesn't",
        "doing",
        "don",
        "don't",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "hadn",
        "hadn't",
        "has",
        "hasn",
        "hasn't",
        "have",
        "haven",
        "haven't",
        "having",
        "he",
        "he'd",
        "he'll",
        "her",
        "here",
        "hers",
        "herself",
        "he's",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "i'd",
        "if",
        "i'll",
        "i'm",
        "in",
        "into",
        "is",
        "isn",
        "isn't",
        "it",
        "it'd",
        "it'll",
        "it's",
        "its",
        "itself",
        "i've",
        "just",
        "ll",
        "m",
        "ma",
        "me",
        "mightn",
        "mightn't",
        "more",
        "most",
        "mustn",
        "mustn't",
        "my",
        "myself",
        "needn",
        "needn't",
        "no",
        "nor",
        "not",
        "now",
        "o",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "re",
        "s",
        "same",
        "shan",
        "shan't",
        "she",
        "she'd",
        "she'll",
        "she's",
        "should",
        "shouldn",
        "shouldn't",
        "should've",
        "so",
        "some",
        "such",
        "t",
        "than",
        "that",
        "that'll",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "these",
        "they",
        "they'd",
        "they'll",
        "they're",
        "they've",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "ve",
        "very",
        "was",
        "wasn",
        "wasn't",
        "we",
        "we'd",
        "we'll",
        "we're",
        "were",
        "weren",
        "weren't",
        "we've",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "will",
        "with",
        "won",
        "won't",
        "wouldn",
        "wouldn't",
        "y",
        "you",
        "you'd",
        "you'll",
        "your",
        "you're",
        "yours",
        "yourself",
        "yourselves",
        "you've",
    ]

    def __init__(self, query: str, article_id: int|None = None):
        self.query = query.strip()
        self.articles = self.fetch_articles()
        self.kw = self.extract_key_words()
        self.article_id = article_id

    def fetch_articles(self) -> list[Article]:
        ret = []
        for article in db.session.scalars(select(Article)).all():
            if article.author.id == current_user.id:
                ret.append(article)
        return ret

    def get_word_frequncy(self):
        freq = {}
        for word in self.words:
            if word not in freq:
                freq[word] = 1
            else:
                freq[word] += 1
        return freq

    def extract_key_words(self):
        self.query_post_punc = re.sub(
            pattern=r"[^a-zA-Z\s]", repl=" ", string=self.query
        )
        self.words = self.query_post_punc.split()
        word_frequency = self.get_word_frequncy()
        self.key_words = {word: word_frequency[word] for word in filter(lambda x: x not in self.STOP_WORDS, word_frequency)}
        # Sort by frequency, descending
        self.sorted_key_words = list(sorted(self.key_words.keys(), key=lambda key_word: self.key_words[key_word], reverse=True))

        if len(self.sorted_key_words) >= 20:
            return self.sorted_key_words[0:20]
        
        return self.sorted_key_words
    
    def get_matches(self) -> list[tuple[int, int]]:
        self.article =  db.session.scalar(select(Article).where(Article.id==int(self.article_id)))
        
        pattern = '('
        for word in self.kw:
            pattern += f'{word}'
            if word != self.kw[-1]:
                pattern += '|'
        pattern += ')'

        matches = list(re.finditer(pattern, self.article.body))

        print(matches)

        pos = [match.span() for match in matches]

        print(pos)

        return pos

        
    def get_results(self) -> tuple[int]:
        
        def is_relavent(article: Article) -> int:
            include_key_word_count = 0
            for k in self.kw:
                if (
                    k.lower() in article.title.lower()
                    or k.lower() in article.description.lower()
                    or k.lower() in article.body.lower()
                    or k.lower() in article.author.first_name.lower()
                    or k.lower() in article.author.last_name.lower()
                ):
                    include_key_word_count += 1
            return include_key_word_count
                    

        relavent_articles = {}
        for article in self.articles:
            matched_kw_count = is_relavent(article)
            if matched_kw_count > 0:
                relavent_articles[article.id] = matched_kw_count
        
        return tuple(sorted(relavent_articles.keys(), key=lambda article_id: relavent_articles[article_id], reverse=True))
        

