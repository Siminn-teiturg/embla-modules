import logging
import random

from query import Query, QueryStateDict
from tree import Node, ParamList, Result

_TV_TIMETRAVEL_QTYPE = "TV-Timetravel"
_STARTOVER_CMD = "STARTOVER"


TOPIC_LEMMAS = ["spila", "byrjun", "byrja"]


def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "Spilaðu Kastljós",
                "Spila Kiljuna frá í gær",
                "Spila Tíufréttir frá því í fyrradag",
            )
        )
    )


# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QTVTimeTravel"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query → QTVTimeTravel
 
QTVTimeTravel → QTVTimeTravelQuery '?'?

QTVTimeTravelQuery →
    QTVStartOver
    | QTVTimeTravelKeyword QTVTimeTravelProgram QTVTimeTravelSinceWhen?

QTVStartOver →
    "byrja" "upp" "á" "nýtt"
    | "byrja" "frá" "byrjun"
    | "aftur" "á" "byrjun"

QTVTimeTravelCourtesy →
    "getur" "þú"?
    | "geturðu" 

QTVTimeTravelKeyword →
    "spila"
    | "spilar"
    | "spilaðu"
    | "spilað"
    | "spilaði"

# QTVTimeTravelAtviksord →
#     "í" | "á" | "við" | "þau" | "þú"

QTVTimeTravelProgram →
    Nl

QTVTimeTravelSinceWhen →
    QTVTimeTravelSince? QTVTimeTravelWhen

QTVTimeTravelSince →
    "síðan" 
    | "frá" 
    | "frá" "það" 
    | "frá" "því"

QTVTimeTravelWhen →
    QTVTimeTravelToday
    | QTVTimeTravelYesterday
    | QTVTimeTravelDayBeforeYesterday

QTVTimeTravelToday →
    "í" "dag" | "í_kvöld"

QTVTimeTravelYesterday →
    "í_gær"
    # | "geir"
    # | "hér"

QTVTimeTravelDayBeforeYesterday →
  "í_fyrradag"

"""


def QTVTimeTravelQuery(node, params, result):
    result.qtype = _TV_TIMETRAVEL_QTYPE


def QTVStartOver(node, params, result):
    result["qkey"] = _STARTOVER_CMD


def QTVTimeTravelProgram(node: Node, params: ParamList, result: Result):
    text: str = result._text.lower()
    if text.endswith(" frá því") or text.endswith(" frá því í dag"):
        text = text[: text.rfind(" frá því")]

    result["command"] = [text]


def QTVTimeTravelToday(node, params, result):
    result["when"] = ["today"]


def QTVTimeTravelYesterday(node, params, result):
    result["when"] = ["yesterday"]


def QTVTimeTravelDayBeforeYesterday(node, params, result):
    result["when"] = ["daybeforeyesterday"]


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    # if when not specified, default to today
    if "when" not in result:
        result["when"] = ["today"]

    q: Query = state["query"]
    if "qtype" in result and result["qtype"] == _TV_TIMETRAVEL_QTYPE:
        try:
            q.query_is_command()
            q.set_qtype(_TV_TIMETRAVEL_QTYPE)
            if "qkey" in result and result["qkey"] == _STARTOVER_CMD:
                q.set_answer({"answer": _STARTOVER_CMD}, _STARTOVER_CMD, "")
            else:
                ans = ";".join(["TIMETRAVEL"] + result["command"] + result["when"])
                q.set_answer({"answer": ans}, ans)
            return
        except Exception as e:
            logging.warning("Exception generating answer from TVCP: {0}".format(e))
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")
