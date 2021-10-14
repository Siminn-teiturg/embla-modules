from typing import List, Dict, Optional, Mapping

import logging
import cachetools  # type: ignore
import random
import math
import re

from query import Query, QueryStateDict
from queries import query_json_api
from tree import Result
from reynir import NounPhrase

from . import AnswerTuple, LatLonTuple

_SIMINN_QTYPE = "Volume"

TOPIC_LEMMAS = [
    "hækka",
    "lækka",
    "þögn",
    "þagna",
    "hljóð",
    "hljóðstyrkur",
]

_NUMBER_WORDS: Mapping[str, float] = {
    "núll": 0,
    "einn": 1,
    "einu": 1,
    "tveir": 2,
    "tveim": 2,
    "þrír": 3,
    "þrem": 3,
    "þremur": 3,
    "fjórir": 4,
    "fjórum": 4,
    "fimm": 5,
    "sex": 6,
    "sjö": 7,
    "átta": 8,
    "níu": 9,
    "tíu": 10,
    "ellefu": 11,
    "tólf": 12,
    "þrettán": 13,
    "fjórtán": 14,
    "fimmtán": 15,
    "sextán": 16,
    "sautján": 17,
    "átján": 18,
    "nítján": 19,
    "tuttugu": 20,
    "þrjátíu": 30,
    "fjörutíu": 40,
    "fimmtíu": 50,
    "sextíu": 60,
    "sjötíu": 70,
    "áttatíu": 80,
    "níutíu": 90,
    "hundrað": 100,
    "hundruð": 100,
}

def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "Hækka hljóðið",
                "Lækka hljóðstyrkinn",
                "Hækka",
                "Þagna",
                "Þögn!",
                "hljóð fimmtíu prósent"
            )
        )
    )

# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QVolume"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query →
    QVolume
 
QVolume → QVolumeQuery '?'?

QVolumeQuery →
    QVolumeUpQuery QVolumeVolume?
    | QVolumeDownQuery QVolumeVolume?
    | QVolumeVolume QVolumePercent

QVolumeUpQuery →
    "hækka" | "hækka" "þú" | "hækkaðu" | "hækkað" 
    | "fækka"

QVolumeDownQuery →
    "lækka" | "lækkað" | "lækka" "þú" | "lækkaðu" 

QVolumeVolume →
    "hljóð" | "hljóðið" | "hljóðstyrk" | "hljóðstyrkinn"

QVolumePercent → Prósenta

"""

def QVolumePercent(node, params, result):
    result._canonical = result._text
    n = result._text.split()
    print(result._canonical)
    print("N:", n, type(n))
    # skoda rett control flow
    # hvad gaeti fokkad thessu upp?
    if n[0].isdecimal():
        print(n[0], "is decimal")
        result["command"] = int(n[0])           # 8
    elif n[0] in _NUMBER_WORDS:
        print(n[0], "is not decimal")
        result["command"] = _NUMBER_WORDS[n[0]] # átta
    else:
        print("tjah, hvað er í gangi hér?")

def QVolumeQuery(node, params, result):
    result.qtype = _SIMINN_QTYPE


def QVolumeUpQuery(node, params, result):
    result["command"] = "VOLUME_UP"


def QVolumeDownQuery(node, params, result):
    result["command"] = "VOLUME_DOWN"


def QVolumeMuteQuery(node, params, result):
    result["command"] = "MUTE"


def parse_num(num_str: str) -> float:
    # Parse Icelandic number string to float or int
    num = None
    try:
        # Pi
        if num_str == "pí":
            num = math.pi
        # Handle numbers w. Icelandic decimal places ("17,2")
        elif re.search(r"^\d+,\d+$", num_str):
            num = float(num_str.replace(",", "."))
        # Handle digits ("17")
        else:
            num = float(num_str)
    except ValueError:
        # Handle number words ("sautján")
        if num_str in _NUMBER_WORDS:
            num = _NUMBER_WORDS[num_str]
        # Ordinal number strings ("17.")
        elif re.search(r"^\d+\.$", num_str):
            num = int(num_str[:-1])
        else:
            num = 0
    except Exception as e:
        logging.warning("Unexpected exception: {0}".format(e))
        raise
    return num

def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    q: Query = state["query"]
    if (
        "qtype" in result
        and result["qtype"] == _SIMINN_QTYPE
    ):
        try:
            print("))============>", _SIMINN_QTYPE, "<============((")
            q.set_qtype(_SIMINN_QTYPE)
            q.set_answer("", result["command"], "")
            return
        except Exception as e:
            logging.warning(
                "Exception generating answer from Volume: {0}".format(e)
            )
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")