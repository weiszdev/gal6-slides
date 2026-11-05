"""Galatians 6 live-teaching slide content (DRAFT). KJV (public domain). Same structure as the Gal 5 deck."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
KJV = {int(k): v.replace("\u2019", "'") for k, v in json.load(open(os.path.join(HERE, "kjv-galatians-6.json"))).items()}
assert len(KJV) == 18
TITLE_LINES_WIDE = ["Bear One Another's", "Burdens"]
TITLE_LINES_VERT = ["Bear One", "Another's", "Burdens"]
TRIAD = ["Carry one another.", "Sow to the Spirit.", "Glory in the cross."]
MOVEMENTS = [
    ("01", "CARRY ONE ANOTHER", "vv. 1\u20135", "Restore gently. Bear one another's burdens. Prove your own work.", "Carry One Another", 1, 5),
    ("02", "SOW TO THE SPIRIT", "vv. 6\u201310", "God is not mocked. Sow to the Spirit, do not grow weary, and do good to all.", "Sow to the Spirit", 6, 10),
    ("03", "GLORY IN THE CROSS", "vv. 11\u201318", "Not the flesh, but the cross. A new creature. Grace be with you.", "Glory in the Cross", 11, 18),
]
READ = [(1, 2), (3, 5), (6, 8), (9, 10), (11, 13), (14, 15), (16, 18)]
LISTEN_FOR = [
    "How are we to treat someone caught in a fault, and what does bearing burdens fulfil?",
    "What deceives the man who thinks he is something, and what must every man prove?",
    "What does God not allow, and what do you reap from what you sow?",
    "What is promised to those who do not faint, and who do we do good to?",
    "Why do some want you circumcised, and what do they want to glory in?",
    "What does Paul glory in, and what is the only thing that counts?",
    "What follows those who walk by this rule, and what marks does Paul bear?",
]
VERSES = {
    1:  ("Someone you know has stumbled. Will you restore them gently, or talk about them?", None),
    2:  ("Whose burden can you carry this week? What would the law of Christ look like in your hands?", None),
    3:  ("Where are you thinking yourself to be something, when apart from Christ you are nothing?", None),
    4:  ("What would change if you measured your own work and stopped comparing yourself to someone else?", None),
    5:  ("Verse 2 says carry one another's burdens. Verse 5 says carry your own load. How do the two fit?", "GREEK: HEAVY WEIGHT (V. 2), DAILY PACK (V. 5)"),
    6:  ("Who taught you the word? How can you bless them with something good this month?", None),
    7:  ("Be not deceived. What are you sowing right now that you hope will not grow?", None),
    8:  ("Flesh or Spirit: which field gets most of your time, money and attention?", None),
    9:  ("Tired of doing good and seeing nothing change? What does \u201cin due season\u201d ask of you?", None),
    10: ("Who is right in front of you today? How can you do good to them, and to the household of faith?", None),
    11: ("Paul takes the pen in his own hand. Who needs a personal word from you this week?", None),
    12: ("Who are you trying to impress? What do you avoid because the cross might cost you?", None),
    13: ("Some boast in how many follow their rules. What are you tempted to boast in?", None),
    14: ("God forbid that I should glory, save in the cross. What else do you glory in?", None),
    15: ("Neither circumcision nor uncircumcision, but a new creature. What is new in you?", None),
    16: ("Walk according to this rule: the new creation. What would change in your week if you did?", None),
    17: ("Paul bears the marks of the Lord Jesus. What has following Christ cost you?", None),
    18: ("The grace of our Lord Jesus Christ be with your spirit. What grace do you need today?", None),
}
YOUR_MOVE = [
    "Read Galatians 6 straight through, out loud.",
    "Pick one person and carry one burden for them this week.",
    "Sow to the Spirit every day: pray, read, serve. Do not faint before the harvest.",
]
SAY_IT = "I will carry my brother's burden, sow to the Spirit, and glory only in the cross."
CLOSE_VERSE = 9
