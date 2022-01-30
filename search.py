import logging
import random

from query import Query, QueryStateDict
from tree import Result


_TV_SEARCH_QTYPE = "TV-Search"

TOPIC_LEMMAS = ["finna", "finndu", "hryllingsmyndir", "leita"]


def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(("Finndu Love Island",))
    )


# Words for "movie"/"show"/"episode" in
_CONTENT_TYPES_ACCUSATIVE = "|".join(
    (
        "myndina",
        "kvikmyndina",
        "þáttinn",
        "þættina",
        "sjónvarpsþáttinn",
        "sjónvarps þáttinn",
        "sjónvarpsþættina",
        "sjónvarps þættina",
        "þáttaröðina",
        "seríuna",
        "sjónvarpsseríuna",
        "sjónvarps seríuna",
    )
)

_CONTENT_TYPES_DATIVE = "|".join(
    (
        "myndinni",
        "kvikmyndinni",
        "þættinum",
        "þáttunum",
        "sjónvarpsþáttunum",
        "sjónvarps þáttunum",
        "sjónvarpsþættinum",
        "sjónvarps þættinum",
        "þáttaröðinni",
        "seríunni",
        "sjónvarpsseríunni",
        "sjónvarps seríunni",
    )
)

# This module wants to handle parse trees for queries
HANDLE_TREE = True

# The grammar nonterminals this module wants to handle
QUERY_NONTERMINALS = {"QTVSearch"}

# The context-free grammar for the queries recognized by this plug-in module
GRAMMAR = """

Query → QTVSearch
 
QTVSearch → QTVSearchQuery '?'?

QTVSearchQuery →
    QTVSearchKeywordAcc QTVSearchTerm_þf
    | QTVSearchKeywordDat QTVSearchTerm_þgf
    # TODO: "myndum með x (í aðalhutverki)"
    # TODO: Skipta efnisflokkum eftir premium og síminn bíó

QTVSearchKeywordAcc →
    "finna"
    | "finndu"
    | "sýndu" "mér"

QTVSearchKeywordDat →
    "leitaðu" "að"

QTVSearchTerm_þf →
    "hryllingsmyndir"
    | "hasarmyndir"

QTVSearchTerm_þgf →
    "hryllingsmyndum"
    | "hasarmynd"

# QTVSearchTerm →
#     Nl

"""

# efnisflokkar premium efnis vs efnisflokkar siminn bio
# PREMIUM
# jól
# kvikmyndir
# íslenskt bíó
# nýtt efni
# krakkar
# allar seríur
# hámhorf
# íslenskt

# SÍMINN BÍÓ
# jólabíó
# nýjar
# nýkomnar
# krakkabíó
# spenna
# drama
# gaman
# rómantík
# fjölskyldu
# íslenskar
# heimildarmyndir
# indie
# sci-fi
# hrollvekjur
# bíó paradís
# leikarar
# allir flokkar

# response dæmi þeirra flokka sem skarast ekki á
# "sýndu mér hryllingsmyndir"
# "answer": ["hrollvekjur", "BIO"]

# "sýndu mér hámhorf"
# "answer": ["hámhorf", "PREMIUM"]

# íslenskur flokkur er t.d. til á bæði premium og bíó
# "sýndu mér íslenskar myndir á premium"
# "sýndu mér íslenskar myndir á síminn bíó/á leigunni"


def QTVSearchQuery(node, params, result):
    result.qtype = _TV_SEARCH_QTYPE

def QTVSearchTerm(node, params, result):
    result["command"] = ["hryllingsmyndir"]


def sentence(state: QueryStateDict, result: Result) -> None:
    """Called when sentence processing is complete."""
    # if when not specified, default to today
    q: Query = state["query"]
    if "qtype" in result and result["qtype"] == _TV_SEARCH_QTYPE:
        try:
            q.set_qtype(_TV_SEARCH_QTYPE)
            ans = ";".join(["SEARCH"] + result["command"])

            q.set_answer({"answer": ans}, ans)
            return
        except Exception as e:
            logging.warning(
                "Exception generating answer from Timetravel: {0}".format(e)
            )
            q.set_error("E_EXCEPTION: {0}".format(e))
