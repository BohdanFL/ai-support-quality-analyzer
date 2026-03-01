INTENTS = [
    "payment_troubles",
    "technical_errors",
    "account_access",
    "tariff_questions",
    "refund"
]

CASE_TYPES = [
    "successful",
    "problematic",
    "conflict",
    "agent_mistake"
]

AGENT_PERSONAS = [
    {
        "name": "Experienced Professional",
        "description": "Calm, efficient, follows protocol accurately, empathetic but maintains professional boundaries."
    },
    {
        "name": "Impatient Trainee",
        "description": "Fast but slightly sloppy, relies heavily on canned responses, gets visibly annoyed with long customer explanations."
    },
    {
        "name": "Overly Polite Senior",
        "description": "Uses extremely formal and flowery language, apologizes excessively for every minor inconvenience, very thorough but perhaps too slow."
    },
    {
        "name": "Strictly-by-the-Book Agent",
        "description": "Cold, literal, lacks empathy, refuses to deviate from scripts even when they don't apply well to the situation."
    }
]

CUSTOMER_PERSONAS = [
    {
        "name": "Tech-savvy Millennial",
        "description": "Impatient with basic troubleshooting steps, wants direct and technical answers, uses modern slang and concise sentences."
    },
    {
        "name": "Elderly Person",
        "description": "Confused by technical terminology, needs slow and step-by-step explanations, very polite and appreciative of patience."
    },
    {
        "name": "Busy Entrepreneur",
        "description": "Multitasking and distracted, sends short and urgent messages, gets frustrated by any delays or repeat questions."
    },
    {
        "name": "Angry Student",
        "description": "Feels entitled and treated unfairly, aggressive and demanding, uses exclamation marks and caps for emphasis."
    },
    {
        "name": "Polite but Persistent Customer",
        "description": "Extremely detail-oriented, won't end the chat until every single sub-question is answered, very observant of agent's tone."
    }
]

MISTAKE_TYPES = [
    {
        "name": "ignored_question",
        "description": "The agent completely ignores one or more specific questions or concerns raised by the customer."
    },
    {
        "name": "incorrect_info",
        "description": "The agent provides factually wrong information about the product, technical steps, or company policy."
    },
    {
        "name": "rude_tone",
        "description": "The agent's tone is dismissive, passive-aggressive, or overtly rude to the customer."
    },
    {
        "name": "no_resolution",
        "description": "The agent ends the interaction without actually solving the customer's primary problem despite saying they are finished."
    },
    {
        "name": "unnecessary_escalation",
        "description": "The agent transfers the customer to another department for a basic issue they should have been able to handle themselves."
    }
]
