from typing import List, Dict, Optional

import logging
import cachetools  # type: ignore
import random

from query import Query, QueryStateDict
from queries import query_json_api
from tree import Result

from . import AnswerTuple, LatLonTuple

_SIMINN_QTYPE = "Channel"

TOPIC_LEMMAS = [
    "RÚV",
    "Sjónvarp Símans"
]

def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "RÚV",
                "Sjónvarp Símans",
                "Hringbraut",
                "Síminn Sport",
                "Alþingi",
            )
        )
    )

# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QChannel"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query →
    QChannel

QChannel → QChannelQuery '?'?

QChannelQuery →
    QChannelRUV | QChannelSS 
    | QChannelStod2 | QChannelStod2Fjolskylda | QChannelStod2Bio
    | QChannelHringbraut | QChannelStod2Visir | QChannelRUV2
    | QChannelSiminnSport | QChannelSiminnSport2 | QChannelSiminnSport3 | QChannelSiminnSport4
    | QChannelAlthing | QChannelOmega
    | QChannelStod2Sport | QChannelStod2Sport2 | QChannelStod2Sport3 | QChannelStod2Sport4
    | QChannelStod2eSport | QChannelStod2Golf

QChannelRUV →
    "rúv" | 'ríkisútvarp'/fall | "stöð" "eitt" | "einn"

QChannelSS →
    "sjónvarp" "símans" | "sjónvarp" 'síminn'/fall | "sjónvarp" 'sími:no'/fall | "sjónvarp" "síminn" | "tveir"

QChannelStod2 →
    "stöð" QTwo
    | "studdu" QTwo
    | "studduð" QTwo

QChannelStod2Fjolskylda →
    QChannelStod2 "fjölskylda"

QChannelStod2Bio →
    QChannelStod2 "bíó"

QChannelHringbraut →
    "hringbraut"

QChannelStod2Visir →
    QChannelStod2 "vísir"

QChannelK100 →
    "ká" "hundrað"

QChannelRUV2 →
    QChannelRUV QTwo

QChannelSiminnSport →
    QSiminn QSport QOne?

QChannelSiminnSport2 →
    QSiminn QSport QTwo

QChannelSiminnSport3 →
    QSiminn QSport QThree

QChannelSiminnSport4 →
    QSiminn QSport QFour

QOne →
    'einn'/kyn
QTwo →
    'tveir'/kyn
QThree →
    'þrír'/kyn
QFour →
    'fjórir'/kyn

QSiminn →
    'síminn'/fall | 'sími:no'/fall | "síminn"

QSport →
    "sport"

QChannelAlthing →
    "alþingi"

QChannelOmega →
    "omega" | "ómega" | "Omega"

QChannelStod2Sport →
    QChannelStod2 QSport QOne?
QChannelStod2Sport2 →
    QChannelStod2 QSport QTwo
QChannelStod2Sport3 →
    QChannelStod2 QSport QThree
QChannelStod2Sport4 →
    QChannelStod2 QSport QFour
QChannelStod2eSport →
    QChannelStod2 "e" QSport
QChannelStod2Golf →
    QChannelStod2 "golf"

"""

def QChannelQuery(node, params, result):
    result.qtype = _SIMINN_QTYPE

def QChannelRUV(node, params, result):
    result["command"] = 22759586

def QChannelSS(node, params, result):
    result["command"] = 22759594

def QChannelStod2(node, params, result):
    result["command"] = 22759599

def QChannelStod2Fjolskylda(node, params, result):
    result["command"] = 22759572

def QChannelStod2Bio(node, params, result):
    result["command"] = 22759610

def QChannelHringbraut(node, params, result):
    result["command"] = 40043140

def QChannelStod2Visir(node, params, result):
    result["command"] = 22759598

def QChannelRUV2(node, params, result):
    result["command"] = 46888903

def QChannelSiminnSport(node, params, result):
    result["command"] = 46888998

def QChannelSiminnSport2(node, params, result):
    result["command"] = 46888999

def QChannelSiminnSport3(node, params, result):
    result["command"] = 46890006

def QChannelSiminnSport4(node, params, result):
    result["command"] = 46890007

def QChannelAlthing(node, params, result):
    result["command"] = 22759659

def QChannelOmega(node, params, result):
    result["command"] = 22759667

def QChannelStod2Sport(node, params, result):
    result["command"] = 22759619

def QChannelStod2Sport2(node, params, result):
    result["command"] = 22759656

def QChannelStod2Sport3(node, params, result):
    result["command"] = 22759600

def QChannelStod2Sport4(node, params, result):
    result["command"] = 22759643

def QChannelStod2eSport(node, params, result):
    result["command"] = 46890013

def QChannelStod2Golf(node, params, result):
    result["command"] = 40043123



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
                "Exception generating answer from Channels: {0}".format(e)
            )
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")
    