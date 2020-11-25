"""
Класс Inverted index и консолььное приложение
"""
import argparse
import struct
import sys
from io import TextIOWrapper


class EncodedFileType(argparse.FileType):
    """
    Небольшой костыль для рабты с кодировкой cp-1251
    """
    def __call__(self, string):
        if string == '-':
            if 'r' in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            elif 'w' in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)
        try:
            return open(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as err:
            message = "can't open '%s': %s"
            raise argparse.ArgumentTypeError(message % (string, err))


class InvertedIndex:
    """
    Инвертированый индекс
    """
    service_bits = "6shh"
    format_strings = []

    def __init__(self, invert_index=None):
        self.invert_index = invert_index or {}

    def query(self, words: list):
        """Return the list of relevant documents for the given query"""
        if not words:
            return []
        ids_set = set(self.invert_index.get(words[0], []))
        if len(words) == 1:
            return list([str(i) for i in ids_set])
        for word in words[1:]:
            ids_set &= set(self.invert_index.get(word, []))
        return list([str(i) for i in ids_set])


    def dump(self, filepath: str):
        """
        Функция сохраняет обратный индекс в виде битовой последовательности
        :param filepath: имя фаила
        :return: None
        """
        with open(filepath, "wb") as file:
            for word, idx in self.invert_index.items():
                format_string = "{}s".format(len(word.encode("utf-8"))) + "H" * len(idx)
                line_to_write = [word.encode("utf-8")] + idx
                file.write(struct.pack(InvertedIndex.service_bits + format_string,
                                "\t\0\t\t\0\t".encode("utf-8"),
                                len(word.encode("utf-8")),
                                len(idx),
                                *line_to_write))


    @classmethod
    def load(cls, filepath: str):
        """
        Функция считывает обратный индекс из фаила
        :param filepath имя фаила с обратным индеском
        :return InvertedIndex
        """
        article_dict = {}
        with open(filepath, "rb") as file:
            lines = file.read()
        for i in lines.split(b'\t\x00\t\t\x00\t'):
            if i == b'':
                continue
            struct_info = struct.unpack("hh", i[:4])
            len_word, num_ids = struct_info[0], struct_info[1]
            tup = struct.unpack("{}s".format(len_word) + "H" * num_ids, i[4:])
            key = tup[0].decode("utf-8")
            article_dict[key] = article_dict.get(key, []) + list(tup[1:])
        return InvertedIndex(article_dict)


def load_documents(filepath: str) -> list:
    """
    Функция считывает данные из фаилы и сохраняет в введе списка
    :param filepath
    :return list
    """
    documents_list = []
    with open(filepath, "r") as file:
        for line in file.readlines():
            documents_list.append(line)
    return documents_list


def build_inverted_index(documents_list: list) -> InvertedIndex:
    """
    Функция создает обхект класса  Inverted index
    :param documents_list - список документов
    :return InvertedIndex
    """
    article_dict = {}
    for doc in documents_list:
        tokens = dict.fromkeys(doc.split("\t", 1)[1].split())
        idx = int(doc.split("\t", 1)[0])
        for token in tokens:
            article_dict[token] = article_dict.get(token, []) + [idx]
    return InvertedIndex(article_dict)


def callback_build(arguments):
    """:
    Функция вызова для создания инфертированого индекса
    """
    documents = load_documents(arguments.dataset_path)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(arguments.output_path)


def callback_query(arguments):
    """
    функция вызова для запроса
    """
    inverted_index = InvertedIndex.load(args.index_path)
    queries = args.query or list(map(lambda x: x.split(), arguments.query_file.readlines()))
    for query in queries:
        print(inverted_index.query(query))


def setup_parser(pars):
    """
    Функция для настойки параметров парсера
    :param: pars - Парсер
    :return: None
    """
    subparser = pars.add_subparsers(help="chose command")

    build_parser = subparser.add_parser("build",
                                        help="build inverted index",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    build_parser.add_argument('--dataset',
                              action='store',
                              type=str,
                              dest="dataset_path",
                              default=None,
                              help="use with 'build', dataset path",
                              )

    build_parser.add_argument('--output',
                              action='store',
                              type=str,
                              dest="output_path",
                              default=None,
                              help="use with 'build', inverted index path",
                              )

    build_parser.set_defaults(callback=callback_build)

    query_parser = subparser.add_parser("query",
                                        help="query inverted index",
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                        )

    query_parser.add_argument('--index',
                              action="store",
                              type=str,
                              dest="index_path",
                              default=None,
                              help="use with 'query', inverted index path",
                              )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument('--query-file-utf8',
                                  type=EncodedFileType('r', encoding="utf-8"),
                                  dest="query_file",
                                  help="use with 'query', query's path",
                                  default=TextIOWrapper(sys.stdin, encoding="utf-8"),
                                  )
    query_file_group.add_argument('--query-file-cp1251',
                                  type=EncodedFileType('r', encoding="cp1251"),
                                  dest="query_file",
                                  help="use with 'query', query's path",
                                  default=TextIOWrapper(sys.stdin, encoding="cp1251"),
                                  )
    query_file_group.add_argument('--query',
                                  nargs='+',
                                  action="append",
                                  dest="query",
                                  help="use with 'query', query itself",
                                  )

    query_parser.set_defaults(callback=callback_query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='inverted index parser',
                                     prog='inverted-index',
                                     )
    setup_parser(parser)
    args = parser.parse_args()
    args.callback(args)
