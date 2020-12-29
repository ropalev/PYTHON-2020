from task_Opalyov_Roman_inverted_index import InvertedIndex, build_inverted_index, load_documents
from textwrap import dedent
import pytest


DATASET_BIG_FPATH = "wikipedia_sample.txt"
DATASET_SMALL_FPATH = 'small_wikipedia_sample'
DATASET_TINY_FPATH = "tiny_wikipedia_sample"
DATASET_TINY_STR = dedent("""\
        123	some words A_word and nothing
        2	some word B_word in this dataset
        5	famous_phrases to be or not to be
        37	all words such as A_word and B_word are here
    """)


def test_load_documents_v2(tmpdir):
    dataset_str = dedent("""\
        123	some words A_word and nothing
        2	some word B_word in this dataset
        5	famous_phrases to be or not to be
        37	all words such as A_word and B_word are here
    """)
    dataset_fio = tmpdir.join("tiny.dataset")
    dataset_fio.write(dataset_str)
    documents = load_documents(dataset_fio)
    etalon_document = [
        "123	some words A_word and nothing\n",
        "2	some word B_word in this dataset\n",
        "5	famous_phrases to be or not to be\n",
        "37	all words such as A_word and B_word are here\n"
    ]
    assert etalon_document == documents, (
        "load_documents incorrectly loaded dataset"
    )



@pytest.fixture()
def tiny_dataset_fio(tmpdir):
    dataset_fio = tmpdir.join("dataset.txt")
    dataset_fio.write(DATASET_TINY_STR)
    return dataset_fio

def test_can_load_documents(tiny_dataset_fio):
    documents = load_documents(tiny_dataset_fio)
    etalon_document = [
        "123	some words A_word and nothing\n",
        "2	some word B_word in this dataset\n",
        "5	famous_phrases to be or not to be\n",
        "37	all words such as A_word and B_word are here\n"
    ]
    assert etalon_document == documents, ("load_documents incorrectly loaded dataset")


@pytest.mark.parametrize(
    "query, etalon_answer",
    [
         pytest.param(["A_word"], "123,37"),
         pytest.param(["B_word"], "2,37"),
         pytest.param(["A_word", "B_word"], "37"),
         pytest.param(["word_does_not_exist"], ""),
         pytest.param([], ""),
    ]
)

def test_query_inverted_index_intersect_result(tiny_dataset_fio, query, etalon_answer):
    documents = load_documents(tiny_dataset_fio)
    tiny_inverted_index = build_inverted_index(documents)
    answer = tiny_inverted_index.query(query)
    assert answer == etalon_answer, \
        ("Expected answer is {}, but you got {}".format(etalon_answer,answer)
         )

# @pytest.mark.skip
def test_can_load_wikipedia_sample():
    documents = load_documents(DATASET_BIG_FPATH)
    assert len(documents) == 4100, ("you incorrectly loaded Wikipedia sample")

@pytest.fixture
def wikipedia_documents():
    documents = load_documents(DATASET_BIG_FPATH)
    return documents


@pytest.fixture
def small_sample_wikipedia_documents():
    documents = load_documents(DATASET_SMALL_FPATH)
    return documents


def test_can_build_and_query_inverted_index(wikipedia_documents):
    wikipedia_inverted_index = build_inverted_index(wikipedia_documents)
    doc_ids = wikipedia_inverted_index.query(["wikipedia"])
    assert isinstance(doc_ids, str), "inverted index query should return str"

@pytest.fixture
def wikipedia_inverted_index(wikipedia_documents):
    wikipedia_inverted_index = build_inverted_index(wikipedia_documents)
    return wikipedia_inverted_index

@pytest.fixture()
def small_wikipedia_inverted_index(small_sample_wikipedia_documents):
    wikipedia_inverted_index = build_inverted_index(small_sample_wikipedia_documents)
    return  wikipedia_inverted_index


def test_can_dump_and_load_inverted_index(tmpdir, wikipedia_inverted_index):
    index_fio = tmpdir.join("index.dump")
    wikipedia_inverted_index.dump(index_fio)
    loaded_inverted_index = InvertedIndex.load(index_fio)
    assert  wikipedia_inverted_index.invert_index == loaded_inverted_index.invert_index, (
        "load should return the same inverted index"
    )