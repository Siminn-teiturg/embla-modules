from typing import List, Mapping, cast

import logging
import json
import random

from query import Query, QueryStateDict
from tree import Node, OptionalNode, ParamList, Result, TerminalNode


_TV_VOLUME_QTYPE = "TV-Volume"

TOPIC_LEMMAS = [
    "hækka",
    "hækkaðu",
    "lækka",
    "lækkaðu",
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
                "Þögn",
                "Hljóð fimmtíu prósent",
            )
        )
    )


# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QTVVolume"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query → QTVVolume

QTVVolume → QTVVolumeQuery '?'?

QTVVolumeQuery →
    QTVVolumeRelative
    | QTVVolumeAbsolute

# "hækkaðu um tuttugu prósent", "lækkaðu um fimmtíu og einn"
QTVVolumeRelative →
    QTVVolumeIncrease QTVVolumeHljóð? QTVVolumeUmAmount?
    | QTVVolumeDecrease QTVVolumeHljóð? QTVVolumeUmAmount?

QTVVolumeUmAmount → "um"? QTVVolumeAmount

# "stilltu hljóðið í fimmtíu prósent", "settu hljóðið í tuttugu"
QTVVolumeAbsolute →
    QTVVolumeSet? QTVVolumeHljóð "í"? QTVVolumeAmount
    | "hækkaðu" "í" QTVVolumeAmount
    | "lækkaðu" "í" QTVVolumeAmount

QTVVolumeIncrease →
    "hækka" "þú"?
    | "hækkaðu"
    | "hækkað"
    # | "fækka"

QTVVolumeDecrease →
    "lækka" "þú"?
    | "lækkaðu"
    | "lækkað"
    | "lægra"
    | "lægri"
    | "minnka" "þú"?
    | "minnkaðu"

QTVVolumeSet →
    "stilltu"
    | "stilla"
    | "setja"
    | "settu"


QTVVolumeHljóð →
    "hljóð"
    | "hljóðið"
    | "hljóðstyrk"
    | "hljóðstyrkinn"

QTVVolumeAmount →
    QTVVolumePercent
    | QTVVolumeNumber "prósent"?

QTVVolumePercent →
    Prósenta
    | QTVVolumeNumTens "og" Prósenta


QTVVolumeNumber →
    QTVVolumeNum0
    | QTVVolumeNum1To9
    | QTVVolumeNum10To19
    | QTVVolumeNumTens
    | QTVVolumeNumTens "og" QTVVolumeNum1To9
    | QTVVolumeNum100

QTVVolumeNum0 → "núll"

QTVVolumeNum1To9 →
    'einn:to'
    | 'tveir:to'
    | 'þrír:to'
    | 'fjórir:to'
    | "fimm"
    | "sex"
    | "sjö"
    | "átta"
    | "níu"

QTVVolumeNum10To19 →
    "tíu"
    | "ellefu"
    | "tólf"
    | "þrettán"
    | "fjórtán"
    | "fimmtán"
    | "sextán"
    | "sautján"
    | "átján"
    | "nítján"

QTVVolumeNumTens →
    "tuttugu"
    | "þrjátíu"
    | "fjörutíu"
    | "fjörtíu"
    | "fimmtíu"
    | "sextíu"
    | "sjötíu"
    | "áttatíu"
    | "níutíu"

QTVVolumeNum100 →
    "eitt"? "hundrað"

"""

_NUMBER_WORDS: Mapping[str, float] = {
    "núll": 0,
    "einn": 1,
    "einu": 1,
    "eitt": 1,
    "tveir": 2,
    "tveim": 2,
    "tvö": 2,
    "þrír": 3,
    "þrem": 3,
    "þrjú": 3,
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


def QTVVolumeQuery(node: Node, params: ParamList, result: Result) -> None:
    result.qtype = _TV_VOLUME_QTYPE


def Prósenta(node: Node, params: ParamList, result: Result) -> None:
    tnode: OptionalNode = node.first_child(lambda x: x.has_t_base("prósenta"))
    if tnode:
        tnode = cast(TerminalNode, tnode)
        # Extract number value from percentage terminal node
        result["numbers"] = [json.loads(tnode.aux)[0]]


def QTVVolumeNum0(node: Node, params: ParamList, result: Result) -> None:
    result["numbers"] = [0]


def QTVVolumeNum1To9(node: Node, params: ParamList, result: Result) -> None:
    r = _NUMBER_WORDS.get(result._root)
    if r:
        result["numbers"] = [r]


def QTVVolumeNum10To19(node: Node, params: ParamList, result: Result) -> None:
    r = _NUMBER_WORDS.get(result._root)
    if r:
        result["numbers"] = [r]


def QTVVolumeNumTens(node: Node, params: ParamList, result: Result) -> None:
    r = _NUMBER_WORDS.get(result._root)
    if r:
        result["numbers"] = [r]


def QTVVolumeNum100(node: Node, params: ParamList, result: Result) -> None:
    result["numbers"] = [100]


def QTVVolumeIncrease(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["VOLUME_REL"]


def QTVVolumeDecrease(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["VOLUME_REL"]
    result["negative"] = True


def QTVVolumeAbsolute(node: Node, params: ParamList, result: Result) -> None:
    result["command"] = ["VOLUME_ABS"]


def _parse_numbers(result: Result) -> int:
    """
    Parse numbers in query/command and
    combine into a single number.
    """
    nums: List[int] = result.get("numbers", [])

    if len(nums) == 0:
        # By default the volume increment is just 1
        return 1

    if len(nums) == 1:
        final_num = nums[0]
    elif len(nums) >= 2:
        n1, n2 = nums

        if 19 < n1 < 100 and n1 % 10 == 0 and 0 < n2 < 10:
            # Normal, e.g. "fimmtíu og eitt prósent"
            final_num = n1 + n2
        else:
            # Weird queries, e.g. "tuttugu og þrjátíu prósent"
            # Just ignore first number and take second one
            final_num = n2
    else:
        return 1

    # Keep number in range 0-100
    if final_num < 0:
        final_num = 0
    elif final_num > 100:
        final_num = 100

    if "negative" in result and result["negative"]:
        # Lowering the volume
        final_num = -final_num

    return int(final_num)


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    q: Query = state["query"]
    if "qtype" in result and result["qtype"] == _TV_VOLUME_QTYPE:
        try:
            q.query_is_command()
            q.set_qtype(_TV_VOLUME_QTYPE)

            cmd_list: List[str] = result["command"]
            cmd_list.append(str(_parse_numbers(result)))

            # Return the command as a string delimited by semicolons
            # Format: (VOLUME_REL|VOLUME_ABS);<value>
            ans = ";".join(cmd_list)
            q.set_answer({"answer": ans}, ans)
            return
        except Exception as e:
            logging.warning("Exception generating answer from Volume: {0}".format(e))
            q.set_error("E_EXCEPTION: {0}".format(e))
    else:
        q.set_error("E_QUERY_NOT_UNDERSTOOD")
