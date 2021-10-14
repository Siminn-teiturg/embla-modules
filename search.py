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

_SIMINN_QTYPE = "Search"

TOPIC_LEMMAS = [
    "finna"
]

def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "Finna Love Island",
            )
        )
    )

# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QSearch"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query →
    QSearch
 
QSearch → QSearchQuery '?'?

QSearchQuery →
    QSearchKeyword QSearchTerm

QSearchKeyword →
    "finna"

QSearchTerm →
    Nl

"""


def QSearchQuery(node, params, result):
    result.qtype = _SIMINN_QTYPE

def QSearchTerm(node, params, result):
    nl = NounPhrase(result._nominative)
    try:
        result["leit-angr"] = "{nl:ángr}".format(nl=nl)
        result["leit-nf"] = "{nl:nf}".format(nl=nl)
    except:
        result["leit-angr"] = str(nl)
        result["leit-nf"] = ""

    print("Nl:", nl)


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    # if when not specified, default to today
    q: Query = state["query"]
    if (
        "qtype" in result
        and result["qtype"] == _SIMINN_QTYPE
    ):
        try:
            print("))============>", _SIMINN_QTYPE, "<============((")
            q.set_qtype(_SIMINN_QTYPE)
            q.set_answer("", [result["leit-angr"], result["leit-nf"]], "")
            return
        except Exception as e:
            logging.warning(
                "Exception generating answer from Timetravel: {0}".format(e)
            )
            q.set_error("E_EXCEPTION: {0}".format(e))