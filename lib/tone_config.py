"""
Softening Phrase Library for WondrLink

Provides pre-written empathetic phrases that can be injected into
prompts based on the emotional context of the query. Referenced by
assemble_prompt() in llm_utils.py.
"""

SOFTENING_PHRASES = {
    "before_clinical_data": [
        "One approach your team might consider is",
        "Some patients have found it helpful to",
        "Based on what you're describing, it may be worth exploring",
        "There are a few options we can look at together",
    ],
    "before_disclaimer": [
        "Because your safety is the priority,",
        "I want to make sure you get the best relief possible, which is why",
        "To make sure this is the right fit for you,",
        "Your wellbeing matters most here, so",
    ],
    "pain_comfort_openers": [
        "I'm so sorry you're hurting right now. Let's look at how we can address this together.",
        "That level of pain is really tough to deal with. You shouldn't have to just push through it.",
        "Pain like that deserves immediate attention. Let's figure out the best next step.",
    ],
    "distress_comfort_openers": [
        "I hear you, and what you're feeling right now is completely valid.",
        "This is an incredibly hard moment, and it makes sense that you're struggling.",
        "You don't have to navigate this alone. Let's take this one step at a time.",
    ],
    "physician_friction_bridges": [
        "I've been feeling a bit disconnected from our treatment plan lately. Can we spend five minutes today making sure I understand the next steps?",
        "I have some concerns I'd like to discuss. Could we set aside a few minutes to go over them together?",
        "I want to make sure we're on the same page about my care. Can we review my treatment plan?",
    ],
}
