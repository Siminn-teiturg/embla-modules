from typing import List, Dict, Optional
from islenska import Bin
from reynir import Greynir

import logging
import cachetools  # type: ignore
import random

from query import Query, QueryStateDict
from queries import query_json_api
from tree import Result
from reynir import NounPhrase

from . import AnswerTuple, LatLonTuple

_TIMETRAVEL_QTYPE = "Timetravel"
_STARTOVER_QTYPE = "Startover"

TOPIC_LEMMAS = [
    "spila"
]

def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "Spila Gísla Martein í kvöld",
                "Spila Kiljuna frá í gær",
                "Spila Tíufréttir frá því í fyrradag",
            )
        )
    )

# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QTimeTravel", "QStartOver"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query →
    QTimeTravel | QStartOver
 
QTimeTravel → QTimeTravelQuery '?'?

QStartOver → QStartOverQuery '?'?

QTimeTravelQuery →
    QTimeTravelKeyword QTimeTravelProgram QTimeTravelWhen?

QStartOverQuery →
    "byrja" "upp" "á" "nýtt"
    | "byrja" "byrjun"

QTimeTravelCourtesy →
    "getur" 
    | "getur" "þú" 
    | "geturðu" 

QTimeTravelKeyword →
    "spila" | "spilar" | "spilaðu" | "spilað"  | "spilaði"

QTimeTravelAtviksord →
    "í" | "á" | "við" | "þau" | "þú"

QTimeTravelProgram →
    Nl

QTimeTravelSince →
    "síðan" 
    | "frá" 
    | "frá" "það" 
    | "frá" "því"

QTimeTravelWhen →
    QTimeTravelToday | QTimeTravelYesterday | QTimeTravelDayBeforeYesterday

QTimeTravelToday →
    "í" "dag"

QTimeTravelYesterday →
    "í_gær" | "geir" | "hér"

QTimeTravelDayBeforeYesterday →
  "í_fyrradag"

"""

def QTimeTravelQuery(node, params, result):
    result.qtype = _TIMETRAVEL_QTYPE

def QStartOverQuery(node, params, result):
    result.qtype = _STARTOVER_QTYPE

def QTimeTravelProgram(node, params, result):
    nl = NounPhrase(result._nominative)
    try:
        result["program-angr"] = "{nl:ángr}".format(nl=nl)
        result["program-nf"] = "{nl:nf}".format(nl=nl)
    except:
        result["program-angr"] = str(nl)
        result["program-nf"] = ""

    print("Nl:", nl)


def QTimeTravelToday(node, params, result):
    result["when"] = "today"


def QTimeTravelYesterday(node, params, result):
    result["when"] = "yesterday"


def QTimeTravelDayBeforeYesterday(node, params, result):
    result["when"] = "daybeforeyesterday"


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    # if when not specified, default to today
    """
    try:
        result["when"]
    except:
        result["when"] = "today"
    """
    if "when" not in result:
        result["when"] = "today"

    q: Query = state["query"]
    if (
        "qtype" in result
        and result["qtype"] == _TIMETRAVEL_QTYPE
    ):
        try:
            print("))============>", _TIMETRAVEL_QTYPE, "<============((")
            q.set_qtype(_TIMETRAVEL_QTYPE)
            q.set_answer("", [result["when"], result["program-angr"], result["program-nf"]], "")
            return
        except Exception as e:
            logging.warning(
                "Exception generating answer from Timetravel: {0}".format(e)
            )
            q.set_error("E_EXCEPTION: {0}".format(e))
    elif (
        "qtype" in result
        and result["qtype"] == _STARTOVER_QTYPE
    ):
        try:
            print("))============>", _STARTOVER_QTYPE, "<============((")
            q.set_qtype(_STARTOVER_QTYPE)
            q.set_answer("", "startover", "")
            return
        except Exception as e:
            logging.warning(
                "Exception generating answer from TVCP: {0}".format(e)
            )
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")