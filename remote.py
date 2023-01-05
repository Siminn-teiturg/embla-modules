import logging
import random

from queries import Query, QueryStateDict
from tree import Result

from . import AnswerTuple, LatLonTuple

_SIMINN_QTYPE = "Remote"

TOPIC_LEMMAS = [
    "hækka",
    "lækka",
    "þögn",
    "þagna",
    "hljóð",
    "hljóðstyrkur",
]


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
            )
        )
    )


# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QRemote"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query →
    QRemote

QRemote → QRemoteQuery '?'?

QRemoteQuery →
    QMuteQuery | QTVQuery | QVODQuery | QMenuQuery | QDPadQuery | QNumPadQuery | QPlaybackQuery
    | QProgramQuery

QTVQuery →
    "sjónvarp"

QVODQuery →
    "aðalvalmynd"

QMenuQuery →
    "valmynd" | "valnefnd"

QDPadQuery →
    QDPadUp | QDPadDown | QDPadLeft | QDPadRight | QDPadOk | QDPadBack | QDPadInfo | QDPadTeletext

QNumPadQuery →
    QNumPadBackspace | QNumPadSearch

QPlaybackQuery →
    QRewind | QPlay | QFF | QStop | QPause

QProgramQuery →
    QProgramUp | QProgramDown
$score(+720) QProgramQuery

QNumPadBackspace →
    "stroka" | "stroka" "út" | "eyða" | "eyða" "út" | "hreinsa"

QNumPadSearch →
    "leita"

QDPadUp →
    "upp"

QDPadDown →
    "niður"

QDPadLeft →
    "vinstri"

QDPadRight →
    "hægri" | "vigri"

QDPadOk →
    "ok" | "okei" | "ókei" | "engey" | "samþykkt"

QDPadBack →
    "bakka" | "til_baka" | "hætta"
    | "þakka" | "vaka" | "pakka"

QDPadInfo →
    "upplýsingar"

QDPadTeletext →
    "textavarp"

QNumPadTV →
    "sjónvarp"

QMuteQuery →
    "þögn" | "þagna"  | "þagnað" | "þagna" "þú" | "þagnaðu" | "þegið" | "þegiðu"
    | "þegja" | "suss"
    | "teygja" | "beygja" | "treyja" | "freyja" | "feginn"
    | "ragna" | "vegna" | "gagna"| "fagna" | "magna"

QPlay →
    "spila" "áfram" | "halda" "áfram" | "spila" | "áfram"

QRewind → QSpolaVerb QRewindAdv

QFF → QSpolaVerb QFFAdv

QSpolaVerb → "spóla" | "spólaðu"

QRewindAdv → "aftur" | "til_baka" | "aftur" "á" "bak"
QFFAdv → "áfram" | "fram" "á" "við"

QStop →
    "stopp" | "stans" | "stoppa" | "stoppaðu" | "stansaðu"

QPause →
    "pása" | "bíddu" | "pásaðu"
    | "hása" | "kássa"

QProgramUp → QStod QAdvUp | QAdjStodUp QStod | QChange

QProgramDown → QStod QAdvDown | QAdjStodDown QStod

QStod → "stöð" | "rás"

QAdvUp → "upp" | "áfram" | "fram" "á" "við"
QAdjStodUp → "næsta"

QAdvDown → "niður" | "til_baka"
QAdjStodDown → "síðasta" | "seinasta" | "fyrri"

QChange → QChangeVP QStod
QChangeVP → "skiptu" "um" | "skipta" "um"

"""


def QRemoteQuery(node, params, result):
    result.qtype = _SIMINN_QTYPE


def QTVQuery(node, params, result):
    result["command"] = "TV"


def QVODQuery(node, params, result):
    result["command"] = "VOD"


def QMenuQuery(node, params, result):
    result["command"] = "MENU"


def QNumPadBackspace(node, params, result):
    result["command"] = "BACKSPACE"


def QNumPadSearch(node, params, result):
    result["command"] = "SEARCH"


def QDPadUp(node, params, result):
    result["command"] = "UP"


def QDPadDown(node, params, result):
    result["command"] = "DOWN"


def QDPadLeft(node, params, result):
    result["command"] = "LEFT"


def QDPadRight(node, params, result):
    result["command"] = "RIGHT"


def QDPadOk(node, params, result):
    result["command"] = "OK"


def QDPadBack(node, params, result):
    result["command"] = "BACK"


def QDPadInfo(node, params, result):
    result["command"] = "INFO"


def QDPadTeletext(node, params, result):
    result["command"] = "YELLOW"


def QMuteQuery(node, params, result):
    result["command"] = "MUTE"


def QRewind(node, params, result):
    result["command"] = "REWIND"


def QPlay(node, params, result):
    result["command"] = "PLAY"


def QFF(node, params, result):
    result["command"] = "FORWARD"


def QStop(node, params, result):
    result["command"] = "STOP"


def QPause(node, params, result):
    result["command"] = "PAUSE"


def QProgramUp(node, params, result):
    result["command"] = "PROGRAM_UP"


def QProgramDown(node, params, result):
    result["command"] = "PROGRAM_DOWN"


def QChannel(node, params, result):
    # TODO þarf annað qtype hér?
    # TODO þýða yfir á channel_id
    result["command"] = result._text.lower()


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    q: Query = state["query"]
    if "qtype" in result and result["qtype"] == _SIMINN_QTYPE:
        try:
            print("))============>", _SIMINN_QTYPE, "<============((")
            q.set_qtype(_SIMINN_QTYPE)
            q.set_answer("", result["command"], "")
            return
        except Exception as e:
            logging.warning("Exception generating answer from Remote: {0}".format(e))
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")
