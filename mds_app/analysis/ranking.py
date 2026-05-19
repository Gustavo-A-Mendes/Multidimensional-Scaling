from mds_app.data.participant import Participant

# return sorted list of participants, based on strees value:
def rank_participants(participants: list[Participant]) -> list[Participant]:
    ranked = [
        p for p in participants if p.mds_result is not None
    ]
    ranked.sort(key=lambda p: p.mds_result.stress)
    return ranked

# return the top of rank of participants, as much as desired:
def top_n(participants: list[Participant], n: int = 5) -> list[Participant]:
    return rank_participants(participants)[:n]

# return the bottom of rank of participants, as much as desired:
def bottom_n(participants: list[Participant], n: int = 5):
    return participants[-n:]
