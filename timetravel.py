from typing import Optional, Match

import re
import random

from queries import Query
from reynir import NounPhrase


_TIMETRAVEL_QTYPE = "Timetravel"
_STARTOVER_QTYPE = "Startover"


def help_text(lemma: str) -> str:
    """Help text to return when query.py is unable to parse a query but
    one of the above lemmas is found in it"""
    return "Ég get svarað ef þú spyrð til dæmis: {0}?".format(
        random.choice(
            (
                "Spilaðu Gísla Martein í kvöld",
                "Gætirðu spilað Kiljuna frá í gær",
                "Spilaðu Tíufréttir frá því í fyrradag",
            )
        )
    )


_STARTOVER_RE = (
    r"^byrja(ðu)?( þáttinn| myndina)?( aftur)? upp á nýtt$",
    r"^byrja(ðu)?( þáttinn| myndina)?(( aftur)? frá)? byrjun(inni)?$",
)

# Ways of saying 'from ...'
_SINCE_RE = r"(frá( (því|það))?|síðan)"
# Ways of saying 'today'
_TODAY_RE = rf"(?P<today>{_SINCE_RE}? í (dag|kvöld|morgun))"
# Ways of saying 'yesterday'
_YESTERDAY_RE = rf"(?P<yesterday>{_SINCE_RE}? í gær(kvöldi?|morgun)?)"
# Ways of saying 'day before yesterday'
_DAYBEFOREYESTERDAY_RE = rf"(?P<daybeforeyesterday>{_SINCE_RE}? í fyrradag)"
# Ways of specifying date
_WHEN_RE = r"( ?({}) ?)".format(
    "|".join(
        (
            _TODAY_RE,
            _YESTERDAY_RE,
            _DAYBEFOREYESTERDAY_RE,
        )
    )
)
# Common courtesies
_CAN_YOU_RE = r"( ?({}) ?)".format(
    "|".join(
        (
            r"geturðu",
            r"getur þú",
            r"gætirðu",
            r"værirðu til í að",
        )
    )
)
# Ways of saying 'play'
_PLAY_RE = r"( ?({}) ?)".format(
    "|".join(
        (
            r"spilaðu?",
            r"spilaði",
            r"spilar(ðu)?",
            r"spila",
            r"spilað? fyrir mig",
        )
    )
)

_TIMETRAVEL_RE = rf"^{_CAN_YOU_RE}?{_PLAY_RE}(?P<program>.+?){_WHEN_RE}?$"


def handle_plain_text(q: Query) -> bool:
    """Handles a plain text query."""

    ql: str = q.query_lower
    if any(re.search(r, ql) for r in _STARTOVER_RE):
        q.set_qtype(_STARTOVER_QTYPE)
        q.set_answer({"answer": "startover"}, "startover")
        return True
    m: Optional[Match[str]] = re.search(_TIMETRAVEL_RE, ql)
    if m:
        gd = m.groupdict()
        program_raw: str = gd["program"]
        when: Optional[str] = (
            "daybeforeyesterday" if gd.get("daybeforeyesterday") else None
        )
        if not when:
            when = "yesterday" if gd.get("yesterday") else None
        if not when:
            when = "today"
        program_indef: str = NounPhrase(program_raw).indefinite or program_raw

        q.set_qtype(_TIMETRAVEL_QTYPE)
        q.set_answer({"answer": "timetravel"}, [when, program_raw, program_indef])
        return True
    return False
