import logging
import random

from query import Query, QueryStateDict
from tree import Result

# TODO: Channel ID dict?

_TV_CHANNEL_QTYPE = "TV-Channel"

TOPIC_LEMMAS = ["RÚV", "Sjónvarp Símans"]


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
QUERY_NONTERMINALS = {"QTVChannel"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query →
    QTVChannel

QTVChannel → QTVChannelQuery '?'?

QTVChannelQuery →
    QTVChannelRUV | QTVChannelSS
    | QTVChannelStod2 | QTVChannelStod2Fjolskylda | QTVChannelStod2Bio
    | QTVChannelHringbraut | QTVChannelStod2Visir | QTVChannelRUV2
    | QTVChannelSiminnSport | QTVChannelSiminnSport2 | QTVChannelSiminnSport3 | QTVChannelSiminnSport4
    | QTVChannelAlthing | QTVChannelOmega
    | QTVChannelStod2Sport | QTVChannelStod2Sport2 | QTVChannelStod2Sport3 | QTVChannelStod2Sport4
    | QTVChannelStod2eSport | QTVChannelStod2Golf

QTVChannelRUV →
    "rúv" | 'ríkisútvarp'/fall | "stöð" "eitt" | "einn"

QTVChannelSS →
    "sjónvarp" "símans" | "sjónvarp" 'síminn'/fall | "sjónvarp" 'sími:no'/fall | "sjónvarp" "síminn" | "tveir"

QTVChannelStod2 →
    "stöð" QTwo
    | "studdu" QTwo
    | "studduð" QTwo

QTVChannelStod2Fjolskylda →
    QTVChannelStod2 "fjölskylda"

QTVChannelStod2Bio →
    QTVChannelStod2 "bíó"

QTVChannelHringbraut →
    "hringbraut"

QTVChannelStod2Visir →
    QTVChannelStod2 "vísir"

QTVChannelK100 →
    "ká" "hundrað"

QTVChannelRUV2 →
    QTVChannelRUV QTwo

QTVChannelSiminnSport →
    QSiminn QSport QOne?

QTVChannelSiminnSport2 →
    QSiminn QSport QTwo

QTVChannelSiminnSport3 →
    QSiminn QSport QThree

QTVChannelSiminnSport4 →
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

QTVChannelAlthing →
    "alþingi"

QTVChannelOmega →
    "omega" | "ómega" | "Omega"

QTVChannelStod2Sport →
    QTVChannelStod2 QSport QOne?
QTVChannelStod2Sport2 →
    QTVChannelStod2 QSport QTwo
QTVChannelStod2Sport3 →
    QTVChannelStod2 QSport QThree
QTVChannelStod2Sport4 →
    QTVChannelStod2 QSport QFour
QTVChannelStod2eSport →
    QTVChannelStod2 "e" QSport
QTVChannelStod2Golf →
    QTVChannelStod2 "golf"

"""


def QTVChannelQuery(node, params, result):
    result.qtype = _TV_CHANNEL_QTYPE


def QTVChannelRUV(node, params, result):
    result["command"] = 22759586


def QTVChannelSS(node, params, result):
    result["command"] = 22759594


def QTVChannelStod2(node, params, result):
    result["command"] = 22759599


def QTVChannelStod2Fjolskylda(node, params, result):
    result["command"] = 22759572


def QTVChannelStod2Bio(node, params, result):
    result["command"] = 22759610


def QTVChannelHringbraut(node, params, result):
    result["command"] = 40043140


def QTVChannelStod2Visir(node, params, result):
    result["command"] = 22759598


def QTVChannelRUV2(node, params, result):
    result["command"] = 46888903


def QTVChannelSiminnSport(node, params, result):
    result["command"] = 46888998


def QTVChannelSiminnSport2(node, params, result):
    result["command"] = 46888999


def QTVChannelSiminnSport3(node, params, result):
    result["command"] = 46890006


def QTVChannelSiminnSport4(node, params, result):
    result["command"] = 46890007


def QTVChannelAlthing(node, params, result):
    result["command"] = 22759659


def QTVChannelOmega(node, params, result):
    result["command"] = 22759667


def QTVChannelStod2Sport(node, params, result):
    result["command"] = 22759619


def QTVChannelStod2Sport2(node, params, result):
    result["command"] = 22759656


def QTVChannelStod2Sport3(node, params, result):
    result["command"] = 22759600


def QTVChannelStod2Sport4(node, params, result):
    result["command"] = 22759643


def QTVChannelStod2eSport(node, params, result):
    result["command"] = 46890013


def QTVChannelStod2Golf(node, params, result):
    result["command"] = 40043123


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    q: Query = state["query"]
    if "qtype" in result and result["qtype"] == _TV_CHANNEL_QTYPE:
        q.query_is_command()
        try:
            print("))============>", _TV_CHANNEL_QTYPE, "<============((")
            q.set_qtype(_TV_CHANNEL_QTYPE)
            ans = "CHANNEL;" + str(result["command"])
            q.set_answer({"answer": ans}, ans)
            return
        except Exception as e:
            logging.warning("Exception generating answer from Channels: {0}".format(e))
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")
