"""
Stackoverflow analytics
"""
import argparse
import json
import logging
import logging.config
import sys
from bs4 import BeautifulSoup

APPLICATION_NAME = "stackoverflow analytics debug"
APPLICATION_NAME_S = "stackoverflow analytics warning"
DEBUG_LOG_NAME = 'stackoverflow_analytics.log'
WARNING_LOG_NAME = 'stackoverflow_analytics.warn'
YAML_CONF = "logging.conf.yml"

logger_debug = logging.getLogger(APPLICATION_NAME)
logger_warn = logging.getLogger(APPLICATION_NAME_S)


def xml_reader(path, stop):
    """
    Read XML file
    :arg path, stop"""
    logger_debug.info('xml_reader start with arguments: %s', path)
    xml_list = []
    score_dict_ = {}
    with open(path, 'r') as file:
        for xml_line in file.readlines():
            xml_soup = BeautifulSoup(xml_line, features='lxml-xml')
            dict_ = {}
            try:
                dict_['creation_date'] = int(xml_soup.row['CreationDate'][:4])
                dict_['PostTypeId'] = xml_soup.row['PostTypeId']
                dict_['Score'] = int(xml_soup.row['Score'])
                dict_['Title'] = " ".join(
                    [str.lower(word) for word in xml_soup.row['Title'].split() if word not in stop]
                )
                for i in dict_['Title'].split():
                    score_dict_[i] = score_dict_.get(i, 0) + dict_['Score']
                xml_list.append(dict_)
            except KeyError:
                # pass
                logger_warn.warning("xml line not include nessesery key, xml_line: %s", xml_line)
    return xml_list, score_dict_


def stop_reader(path):
    """
    Read stop-word file
    :arg path
    """
    logger_debug.info('stop_reader start with arguments: %s', path)
    stop_set_ = set()
    with open(path, 'r') as file:
        for line in file.readlines():
            stop_set_.add(line.strip())
    return stop_set_


def query_reader(path):
    """
    Read query file
    :param path:
    :return:
    """
    logger_debug.info('query_reader start with arguments: %s', path)
    query_list_ = []
    with open(path, 'r') as file:
        for line in file.readlines():
            query_list_.append(list(map(int, line.strip().split(','))))
    return query_list_


def statistics(xml, queries, scor):
    """
    Score top words
    """
    logger_debug.info('setup_parser start with arguments')
    res_str = ""
    for query in queries:
        res_dict_ = {}
        question_set = set()
        start, end, top = query
        for xml_line in xml:
            if start <= xml_line['creation_date'] <= end:
                question_set |= set(xml_line['Title'].split())
        score_dict_ = {k: v for k, v in scor.items() if k in question_set}
        score = sorted(score_dict_.items(), key=lambda z: (-z[1], z[0]), reverse=True)
        score.reverse()
        res_dict_['start'] = start
        res_dict_['end'] = end
        res_dict_['top'] = [list(i) for i in score[:top]]
        res_str += json.dumps(res_dict_) + '\n'
        logger_debug.debug("query result from result: %s", json.dumps(res_dict_))
    return res_str


def callback_func(arguments):
    """:
    Функция вызова для создания инфертированого индекса
    """
    stop_set_ = stop_reader(arguments.stop_path)
    xml_list_, score_dict_ = xml_reader(arguments.quest_path, stop_set_)
    query_list_ = query_reader(arguments.query_path)
    return xml_list_, stop_set_, query_list_, score_dict_


def setup_parser(pars):
    """
    Функция для настойки параметров парсера
    :param: pars - Парсер
    :return: None
    """
    logger_debug.info('setup_parser start with arguments: %s', pars)
    pars.add_argument('--questions',
                      action='store',
                      type=str,
                      dest='quest_path',
                      default=None,
                      help='path to questions in xml format',
                      )
    pars.add_argument('--stop-words',
                      action='store',
                      type=str,
                      dest='stop_path',
                      default=None,
                      help='path to stop words',
                      )
    pars.add_argument('--queries',
                      action='store',
                      type=str,
                      dest='query_path',
                      default=None,
                      help='path to queries in csv format',
                      )
    pars.set_defaults(callback=callback_func)


def setup_logging():
    """
    Logger setup
    :return:
    """
    simple_formatter = logging.Formatter(datefmt="%Y-%m-%d %H:%M:%S",
                                         fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
                                         )
    file_handler = logging.FileHandler(
        filename="stackoverflow.log",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(simple_formatter)
    logger_debug.setLevel(logging.DEBUG)
    logger_debug.addHandler(file_handler)
    logger_debug.propagate = False
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    warn_file_handler = logging.FileHandler(
        filename=WARNING_LOG_NAME,
    )
    warn_formatter = logging.Formatter(datefmt="%Y-%m-%d %H:%M:%S",
                                       fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
                                       )
    warn_file_handler.setLevel(logging.WARNING)
    warn_file_handler.setFormatter(warn_formatter)
    logger_warn.setLevel(logging.WARNING)
    logger_warn.addHandler(warn_file_handler)


if __name__ == '__main__':
    setup_logging()
    parser = argparse.ArgumentParser(description='stackoverflow  analytics',
                                     prog='stackoverflow  analytics',
                                     )
    setup_parser(parser)
    args = parser.parse_args()
    xml_lines, stop_set, query_list, score_dict = args.callback(args)
    result = statistics(xml_lines, query_list, score_dict)
    logger_debug.info("end %s", result)
    sys.stdout.write(result)
