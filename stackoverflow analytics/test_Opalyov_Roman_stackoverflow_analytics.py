# from task_Opalyov_Roman_inverted_index import InvertedIndex, build_inverted_index, load_documents
from textwrap import dedent
import pytest
import argparse
QUERY_FILE_PATH = 'query.csv'
STOP_FILE_PATH = 'stop_words_en.txt'
XML_FILE_PATH = 'stackoverflow_posts_sample.xml'
from task_opalyov_roman_stackoverflow_analytics import callback_func,  query_reader, stop_reader,xml_reader

def test_query_reader():
    queries = query_reader(QUERY_FILE_PATH)
    assert len(queries) == 4, ("Expected len is {}".format(4))

def test_stop_reader():
    stop_set = stop_reader(STOP_FILE_PATH)
    assert len(stop_set) == 319,("Expected len is {}".format(4))

def test_xml_reader():
    stop_set = stop_reader(STOP_FILE_PATH)
    xml_list, score_dict = xml_reader(XML_FILE_PATH, stop_set)
    assert len(xml_list) == 325, ("Expected len is {}".format(4))
    assert len(score_dict) == 1160, ("Expected len is {}".format(4))

