"""
module
"""
import argparse


class InvertedIndex:
    """
    class
    """
    service_bits = "6shh"
    format_strings = []

    def __init__(self, invert_index=None):
        self.invert_index = invert_index or {}

    def query(self, words: list):
        """Return the list of relevant documents for the given query"""
        if not words:
            return None
        ids_set = set(self.invert_index.get(words[0], []))
        if len(words) == 1:
            return ",".join([str(i) for i in ids_set])
        for word in words[1:]:
            ids_set &= set(self.invert_index.get(word, []))
        return ",".join([str(i) for i in ids_set])

    def dump(self, filepath: str):
        print("DUMP")
        print(len(self.invert_index))
        i = 0
        with open(filepath, "wb") as file:
            for word, id in self.invert_index.items():
                format_string = "{}s".format(len(word.encode("utf-8"))) + "H" * len(id)
                InvertedIndex.format_strings.append(format_string)
                line_to_write = [word.encode("utf-8")] + [i for i in id]
                # len_line = len(word.encode("utf-8")) + \
                #            sum([len(str(i)) for i in id]) + \
                #            len([i for i in id])
                file.write(struct.pack(InvertedIndex.service_bits + format_string,
                                "\t\0\t\t\0\t".encode("utf-8"),
                                len(word.encode("utf-8")),
                                len(id),
                                *line_to_write))
                i += 1
                print(i)

    @classmethod
    def load(cls, filepath: str):
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


def load_documents(filepath: str):
    documents = []
    with open(filepath, "r") as file:
        for line in file.readlines():
            documents.append(line)
    return documents


def build_inverted_index(documents):
    article_dict = {}
    i = 0
    # print(len(documents))
    for doc in documents:
        tokens = dict.fromkeys(doc.split("\t", 1)[1].split())
        id = int(doc.split("\t", 1)[0])
        for token in tokens:
            article_dict[token] = article_dict.get(token, []) + [id]
        i += 1
        print(i)
        # if i == 10:
        #     break
    return InvertedIndex(article_dict)


def main():
    # documents = load_documents("wikipedia_sample")
    # inverted_index = build_inverted_index(documents)
    # inverted_index.dump("inverted.index")
    inverted_index = InvertedIndex.load("inverted.index")
    print(inverted_index.invert_index)

def setup_parser(parser):
    """
    setup_parser
    :return:
    """
    parser.add_argument('bq')
    parser.add_argument('--dataset', action='store', type=str, dest="dataset_path", default=None)
    parser.add_argument('--output', action='store', type=str, dest="output_path", default=None)
    parser.add_argument('--index', action="store", type=str, dest="index_path", default=None)
    parser.add_argument('--query-file-utf8', nargs='?', type=argparse.FileType('r', encoding="utf-8"),  dest="utf")
    parser.add_argument('--query-file-cp1251', nargs='?', type=argparse.FileType('r', encoding="cp1251"), dest="cp")
    parser.add_argument('--query', nargs='?', action="append", type=argparse.FileType('r', encoding="utf-8"), dest="query")

if __name__ == "__main__":
    import struct
    import sys

    parser = argparse.ArgumentParser(description='inverted index parser')
    setup_parser(parser)
    args = parser.parse_args()
    if args.bq == "build":
        documents = load_documents(args.dataset_path)
        inverted_index = build_inverted_index(documents)
        inverted_index.dump(args.output_path)
    if args.bq == "query":
        if not (args.utf or args.cp or args.query):
            exit()
        if args.utf and args.cp:
            sys.exit("Chose utf-8 or cp1251")
        files = args.utf or args.cp or args.query
        if args.query:
            for file in files:
                queries = list(map(lambda x: x.split(), file.readlines()))
                inverted_index = InvertedIndex.load(args.index_path)
                for q in queries:
                    print(inverted_index.query(q))
        else:
            queries = list(map(lambda x: x.split(), files.readlines()))
            inverted_index = InvertedIndex.load(args.index_path)
            for q in queries:
                print(inverted_index.query(q))
