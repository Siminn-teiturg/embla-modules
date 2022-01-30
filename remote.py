from typing import List, Mapping

import logging
import random

from query import Query, QueryStateDict
from tree import Node, ParamList, Result

# TODO: Add topic lemmas
# TODO: "Ýttu (y sinnum) á x takkann (y sinnum)"
# TODO: Implement rewind/forward by X seconds (Need backend support)
# TODO: Spólaðu áfram/afturábak um mínútu (left/right keys) also "á tvöföldum hraða"


_TV_REMOTE_QTYPE = "TV-Remote"

TOPIC_LEMMAS = [
    "rás",
    "sjónvarp",
    "valmynd",
    "upp",
    "niður",
    "hægri",
    "vinstri",
    "textavarp",
]


def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "Aðalvalmynd",
                "Textavarp",
                "Kveikja á textavarpi",
                "Spólaðu áfram",
            )
        )
    )


# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QTVRemote"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query → QTVRemote

QTVRemote → QTVRemoteQuery '?'?

# Each button or group of buttons on the remote
QTVRemoteQuery →
    QTVRemoteMute
    # | QTVRemotePower # TODO: Is this possible?
    | QTVRemoteNumPad
    | QTVRemoteTV
    | QTVRemoteVOD
    | QTVRemoteMenu
    | QTVRemoteDPad # TODO: Repeat x times
    | QTVRemotePlayback
    # | Misc buttons (color buttons, so on)

QTVRemoteMute →
    "þögn"
    | "þagna" "þú"?
    | "þagnaðu"
    | "þagnað"
    # | "ragna" | "vegna" | "gagna" | "fagna" | "magna"

# Number buttons

QTVRemoteNumPad →
    QTVRemoteNumPadBackspace  # TODO: Repeatable (x letters)
    | QTVRemoteNumPadSearch

QTVRemoteNumPadBackspace →
    "stroka" "út"?
    | "strokaðu" "út"?

QTVRemoteNumPadSearch →
    "leita"
    | "leitaðu"
    | "leit"
    | "leitartakkinn"
    | QTVRemoteFarðuÍ "leitina"

# TV/VOD/Menu buttons

QTVRemoteTV →
    QTVRemoteFarðuÍ? "sjónvarp"
    | QTVRemoteFarðuÍ? "sjónvarpið"
    | "sjónvarpstakki"
    | "sjónvarpstakkinn"

QTVRemoteVOD →
    QTVRemoteFarðuÍ? "aðalvalmynd"
    | "aðalvalmyndin"
    | QTVRemoteFarðuÍ "aðalvalmyndina"
    | QTVRemoteFarðuÍ? "aðal" "valmynd"
    | "aðal" "valmyndin"
    | QTVRemoteFarðuÍ "aðal" "valmyndina"

QTVRemoteMenu →
    QTVRemoteFarðuÍ? "valmynd"
    | "valmyndin"
    | QTVRemoteFarðuÍ "valmyndina"
    | "valnefnd"

# Directional buttons (DPad)

QTVRemoteDPad →
    "farðu"? QTVRemoteXTimes? QTVRemoteDirections
    | QTVRemoteDPadOk
    | QTVRemoteDPadBack
    | QTVRemoteDPadInfo
    | QTVRemoteDPadTeletext

QTVRemoteDirections →
    QTVRemoteDPadUp
    | QTVRemoteDPadDown
    | QTVRemoteDPadLeft
    | QTVRemoteDPadRight

QTVRemoteDPadUp →
    "upp"

QTVRemoteDPadDown →
    "niður"

QTVRemoteDPadLeft →
    "til"? "vinstri"

QTVRemoteDPadRight →
    "til"? "hægri"
    # | "vigri"

QTVRemoteXTimes →
    QTVRemoteNumber "sinnum"?

QTVRemoteDPadOk →
    "ok"
    | "okei"
    | "ókei"
    # | "engey"

QTVRemoteDPadBack →
    "bakka"
    | "farðu"? QTVRemoteBackwards
    | "bakkaðu"
    # | "þakka"
    # | "pakka"
    # | "vaka"

QTVRemoteDPadInfo →
    "upplýsingar"
    | "upplýsingatakki"

QTVRemoteDPadTeletext →
    QTVRemoteFarðuÍ? "textavarp"
    | QTVRemoteFarðuÍ? "textavarpið"
    | "kveikja" "á" "textavarpi"
    | "kveiktu" "á" "textavarpi"
    | "textavarpstakki"

QTVRemotePlayback →
    QTVRemotePause
    | QTVRemotePlay
    | QTVRemoteStop
    | QTVRemoteRewind
    | QTVRemoteFF

QTVRemoteChannels →
    QTVRemoteChannelNext
    | QTVRemoteChannelPrevious

# For fast-forwarding/rewinding a specific time interval
# QTVRemoteXTime →
#     QTVRemoteXMinutes | QTVRemoteXSeconds
# QTVRemoteXMinutes →
# QTVRemoteXSeconds →

QTVRemoteFF →
    "spóla" "áfram"
    | "spólaðu" "áfram"

QTVRemoteRewind →
    "spóla" QTVRemoteBackwards
    | "spólaðu" QTVRemoteBackwards
    # 'farðu x sek til baka'

QTVRemoteFarðuÍ →
    "farðu" "í"

# (Both 'aftur á bak' and 'afturábak' are recognized by Greynir)
QTVRemoteBackwards →
    "aftur"? "til_baka"
    | "aftur" QTVRemoteÁBak?
    | "afturábak"

QTVRemoteÁBak →
    "á" "bak"

QTVRemoteProgramAccusative →
    "myndina"
    | "bíómyndina"
    | "kvikmyndina"
    | "þáttinn"

QTVRemoteSpilun →
    "spilun"
    | "að" "spila"

# 'Haltu áfram með myndina', 'Spilaðu áfram', 'Halda áfram spilun'
QTVRemotePlay →
    "spila" "áfram"? "mynd"?
    | "spilaðu" "áfram"? QTVRemoteProgramAccusative?
    | "halda" "áfram"
    | "haltu" "áfram" QTVRemoteSpilun?
    | "haltu" "áfram" "með" QTVRemoteProgramAccusative

QTVRemoteStop →
    "stopp"
    | "stoppa" "þú"? QTVRemoteSpilun?
    | "stoppaðu" QTVRemoteSpilun?
    | "stans"
    | "stansaðu"
    | "hættu" QTVRemoteSpilun

QTVRemotePause →
    "pása" "spilun"?
    | "pásaðu" QTVRemoteSpilun?
    | "bíddu"
    | "settu" QTVRemoteProgramAccusative? "á" "pásu"
    # | "hása" | "kássa"

QTVRemoteChannelNext →
    QTVRemoteChannel "upp"
    | QTVRemoteChannel "áfram"
    | "næsta" QTVRemoteChannel
    # 'skiptu/farðu yfir á næstu rás'?

QTVRemoteChannelPrevious →
    QTVRemoteChannel "niður"
    | QTVRemoteChannel "til_baka"
    | "fyrri" QTVRemoteChannel
    # 'skiptu/farðu yfir á rásina á undan'?

QTVRemoteChannel →
    "sjónvarps"? "rás"
    | "sjónvarps"? "stöð"
    | "sjónvarpsstöð"
    | "sjónvarpsrás"

QTVRemoteChannelChange →
    "skipta"
    | "skiptu"
    | "setja"
    | "settu"
    | "fletta"
    | "flettu"
    | "farðu"

# Misc buttons

# ---

# Note: not the numpad on the remote, just numbers
QTVRemoteNumber →
    QTVRemoteNumTens "og" QTVRemoteNum1To9
    | tala
    | töl
    | to
    | "tvisvar"
    | "þrisvar"

QTVRemoteNum0 → "núll"

QTVRemoteNum1To9 →
    'einn:to'
    | 'tveir:to'
    | 'þrír:to'
    | 'fjórir:to'
    | "fimm"
    | "sex"
    | "sjö"
    | "átta"
    | "níu"

QTVRemoteNumTens →
    "tuttugu"
    | "þrjátíu"
    | "fjörutíu"
    | "fjörtíu"
    | "fimmtíu"
    | "sextíu"
    | "sjötíu"
    | "áttatíu"
    | "níutíu"

"""

_NUMBER_WORDS: Mapping[str, float] = {
    "núll": 0,
    "einn": 1,
    "einu": 1,
    "eitt": 1,
    "tveir": 2,
    "tveim": 2,
    "tvö": 2,
    "tvisvar": 2,
    "þrír": 3,
    "þrem": 3,
    "þrjú": 3,
    "þrisvar": 3,
    "þremur": 3,
    "fjórir": 4,
    "fjórum": 4,
    "fjögur": 4,
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
    "fjörtíu": 40,
    "fimmtíu": 50,
    "sextíu": 60,
    "sjötíu": 70,
    "áttatíu": 80,
    "níutíu": 90,
    "hundrað": 100,
    "hundruð": 100,
}


def QTVRemote(node: Node, params: ParamList, result: Result) -> None:
    result.qtype = _TV_REMOTE_QTYPE


def QTVRemoteMute(node: Node, params: ParamList, result: Result) -> None:
    # Not in volume.py, as mute button has special functionality
    # (restores to former volume when toggled off, which would
    # otherwise have to be implemented in a stateless manner)
    result["command"] = ["MUTE"]


def QTVRemoteTV(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["TV"]


def QTVRemoteVOD(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["VOD"]


def QTVRemoteMenu(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["MENU"]


def QTVRemoteNumPadBackspace(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["BACKSPACE"]


def QTVRemoteNumPadSearch(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["SEARCH"]


def QTVRemoteDirections(node: Node, params: ParamList, result: Result) -> None:
    result["repeatable"] = True


def QTVRemoteDPadUp(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["UP"]


def QTVRemoteDPadDown(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["DOWN"]


def QTVRemoteDPadLeft(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["LEFT"]


def QTVRemoteDPadRight(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["RIGHT"]


def QTVRemoteDPadOk(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["OK"]


def QTVRemoteDPadBack(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["BACK"]


def QTVRemoteDPadInfo(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["INFO"]


def QTVRemoteDPadTeletext(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["YELLOW"]


def QTVRemoteRewind(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["REWIND"]


def QTVRemotePlay(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["PLAY"]


def QTVRemoteFF(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["FORWARD"]


def QTVRemoteStop(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["STOP"]


def QTVRemotePause(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["PAUSE"]


def QTVRemoteProgramUp(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["PROGRAM_UP"]


def QTVRemoteProgramDown(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["PROGRAM_DOWN"]


def QTVRemoteNumber(node: Node, params: ParamList, result: Result) -> None:
    # Try to parse numbers such as: "50", "fimmtíu" and "fimmtíu og fjórir"
    nums: List[str] = result._root.split()
    s = 0
    for word in nums:
        if word.isdecimal():
            s += int(word)
        else:
            s += _NUMBER_WORDS.get(word, 0)

    if s > 0:
        result["numbers"] = [s]


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    q: Query = state["query"]
    if "qtype" in result and result["qtype"] == _TV_REMOTE_QTYPE:
        try:
            q.query_is_command()
            q.set_qtype(_TV_REMOTE_QTYPE)

            if result.get("repeatable", False) and "numbers" in result:
                # Keypress multipliers
                result["command"].append("MUL")
                result["command"] += result["numbers"]

            if result.get("timespan", False) and "numbers" in result:
                # Keypress multipliers
                result["command"].append("SECONDS")
                result["command"] += result["numbers"]

            # Return the command as a string delimited by semicolons
            # Format: REMOTE;<key pressed>;<additional args>
            # Additional args can be multipliers (press a key multiple times) (MUL;x)
            # or a time span (given in seconds) for fast-forwarding or rewinding (SECONDS;x)

            ans: str = ";".join(["REMOTE"] + result["command"])
            q.set_answer({"answer": ans}, ans)
            return
        except Exception as e:
            logging.warning("Exception generating answer from Remote: {0}".format(e))
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")
