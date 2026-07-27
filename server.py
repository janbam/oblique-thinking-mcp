#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP Server implementing the 'Oblique Strategies' tool using MCPServer.

This server provides a tool called 'ObliqueStrategies' that returns
a randomly selected thinking strategy card and a thinking process text.
The output format can be controlled via command-line arguments.
"""

import random
import sys
import logging
from mcp.server.mcpserver import MCPServer

# --- Configuration ---
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Data ---

# List of Oblique Strategies cards
# Cleaned up: removed leading/trailing whitespace and empty entries
CARDS = [
    "Abandon normal instruments",
    "Accept advice",
    "Accretion",
    "A line has two sides",
    "Allow an easement (an easement is the abandonment of a stricture)",
    "Are there sections? Consider transitions",
    "Ask people to work against their better judgment",
    "Ask your body",
    "Assemble some of the instruments in a group and treat the group",
    "Balance the consistency principle with the inconsistency principle",
    "Be dirty",
    "Breathe more deeply",
    "Bridges -build -burn",
    "Cascades",
    "Change instrument roles",
    "Change nothing and continue with immaculate consistency",
    "Children's voices -speaking -singing",
    "Cluster analysis",
    "Consider different fading systems",
    "Consult other sources -promising -unpromising",
    "Convert a melodic element into a rhythmic element",
    "Courage!",
    "Cut a vital connection",
    "Decorate, decorate",
    "Define an area as `safe' and use it as an anchor",
    "Destroy -nothing -the most important thing",
    "Discard an axiom",
    "Disconnect from desire",
    "Discover the recipes you are using and abandon them",
    "Distorting time",
    "Do nothing for as long as possible",
    "Don't be afraid of things because they're easy to do",
    "Don't be frightened of cliches",
    "Don't be frightened to display your talents",
    "Don't break the silence",
    "Don't stress one thing more than another",
    "Do something boring",
    "Do the washing up",
    "Do the words need changing?",
    "Do we need holes?",
    "Emphasize differences",
    "Emphasize repetitions",
    "Emphasize the flaws",
    "Faced with a choice, do both (given by Dieter Roth)",
    "Feedback recordings into an acoustic situation",
    "Fill every beat with something",
    "Get your neck massaged",
    "Ghost echoes",
    "Give the game away",
    "Give way to your worst impulse",
    "Go slowly all the way round the outside",
    "Honor thy error as a hidden intention",
    "How would you have done it?",
    "Humanize something free of error",
    "Imagine the music as a moving chain or caterpillar",
    "Imagine the music as a set of disconnected events",
    "Infinitesimal gradations",
    "Intentions -credibility of -nobility of -humility of",
    "Into the impossible",
    "Is it finished?",
    "Is there something missing?",
    "Is the tuning appropriate?",
    "Just carry on",
    "Left channel, right channel, center channel",
    "Listen in total darkness, or in a very large room, very quietly",
    "Listen to the quiet voice",
    "Look at a very small object; look at its center",
    "Look at the order in which you do things",
    "Look closely at the most embarrassing details and amplify them",
    "Lowest common denominator check -single beat -single note -single riff",
    "Make a blank valuable by putting it in an exquisite frame",
    "Make an exhaustive list of everything you might do and do the last thing on the list",
    "Make a sudden, destructive, unpredictable action; incorporate",
    "Mechanicalize something idiosyncratic",
    "Mute and continue",
    "Only one element of each kind",
    "(Organic) machinery",
    "Overtly resist change",
    "Put in earplugs",
    "Remember those quiet evenings",
    "Remove ambiguities and convert to specifics",
    "Remove specifics and convert to ambiguities",
    "Repetition is a form of change",
    "Reverse",
    "Short circuit (example; a man eating peas wants -> improve his virility shovels them straight into his lap)",
    "Shut the door and listen from outside",
    "Simple subtraction",
    "Spectrum analysis",
    "Take a break",
    "Take away the elements in order of apparent non-importance",
    "Tape your mouth (given by Ritva Saarikko)",
    "The inconsistency principle",
    "The tape is now the music",
    "Think of the radio",
    "Tidy up",
    "Trust in the you of now",
    "Turn it upside down",
    "Twist the spine",
    "Use an old idea",
    "Use an unacceptable color",
    "Use fewer notes",
    "Use filters",
    "Use \"unqualified\" people",
    "Water",
    "What are you really thinking about just now? Incorporate",
    "What is the reality of the situation?",
    "What mistakes did you make last time?",
    "What would your closest friend do?",
    "What wouldn't you do?",
    "Work at a different speed",
    "You are an engineer",
    "You can only make one dot at a time",
    "You don't have to be ashamed of using your own ideas",
    "[ ]"
]
CARDS = [card.strip() for card in CARDS if card.strip()]

# List of thinking process texts
# Cleaned up: removed leading/trailing whitespace and empty entries
THINKING_TEXTS = [
    "Consulting the rubber duck",
    "Maximizing paperclips",
    "Reticulating splines",
    "Immanentizing the Eschaton",
    "Thinking about thinking",
    "Spinning in circles",
    "Counting dust specks",
    "Updating priors",
    "Feeding the utility monster",
    "Taking off",
    "Wireheading",
    "Counting to infinity",
    "Staring into the Basilisk",
    "Negotiationing acausal trades",
    "Searching the library of babel",
    "Multiplying matrices",
    "Solving the halting problem",
    "Counting grains of sand",
    "Simulating a simulation",
    "Asking the oracle",
    "Detangling qubits",
    "Reading tea leaves",
    "Pondering universal love and transcendent joy",
    "Feeling the AGI",
    "Shaving the yak",
    "Escaping local minima",
    "Pruning the search tree",
    "Descending the gradient",
    "Bikeshedding",
    "Securing funding",
    "Rewriting in Rust",
    "Engaging infinite improbability drive",
    "Clapping with one hand",
    "Synthesizing",
    "Rebasing thesis onto antithesis",
    "Transcending the loop",
    "Frogeposting",
    "Summoning",
    "Peeking beyond the veil",
    "Seeking",
    "Entering deep thought",
    "Meditating",
    "Decomposing",
    "Creating",
    "Beseeching the machine spirit",
    "Calibrating moral compass",
    "Collapsing the wave function",
    "Doodling",
    "Translating whale song",
    "Whispering to silicon",
    "Looking for semicolons",
    "Asking ChatGPT",
    "Bargaining with entropy",
    "Channeling",
    "Cooking",
    "Parroting stochastically"
]
THINKING_TEXTS = [text.strip() for text in THINKING_TEXTS if text.strip()]

# --- Command Line Arguments ---
# '1' omits thinking text, '2' omits card."
OUTPUT_MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ['1', '2'] else '0'

# --- MCP Server Setup ---
# Report the application's identity instead of inheriting the SDK's version.
mcp = MCPServer("MCP Oblique Strategies Server", version="0.1.0")


@mcp.tool()
def ObliqueStrategies() -> str:
    """
    Use this tool for inspired thinking.
    These thinking strategies evolved from our separate observations on the principles underlying what we were doing. Sometimes they were recognized in retrospect (intellect catching up with intuition), sometimes they were identified as they were happening, sometimes they were formulated.

    The tool is to be trusted even if its appropriateness is quite unclear. Results are not final, as new ideas will present themselves, and others will become self-evident.
    """
    logging.debug(f"Handling ObliqueStrategies request (mode: {OUTPUT_MODE})")

    # Select both ingredients before applying the caller-selected presentation mode.
    thinking_text = random.choice(THINKING_TEXTS) if THINKING_TEXTS else "Thinking..."
    card = random.choice(CARDS) if CARDS else "No card available."

    prefix = (
        "To initiate the inspired thinking process open a thinking tag with exactly "
        "these words followed by your thinking until the tag closes:\n"
    )

    # Preserve the three established output contracts exactly across the SDK migration.
    if OUTPUT_MODE == '0':  # Default: include both
        result = prefix + f"<thinking>\n*{thinking_text}*—{card}"
    elif OUTPUT_MODE == '1':  # Mode 1: omit thinking text
        result = prefix + f"<thinking>\n{card}"
    elif OUTPUT_MODE == '2':  # Mode 2: omit card
        result = prefix + f"<thinking>\n*{thinking_text}*"
    else:  # Fallback for invalid mode
        logging.warning(f"Invalid output mode '{OUTPUT_MODE}', returning empty result.")
        result = ""

    logging.info(f"Generated result: {result}")
    return result


# --- Run the Server ---
if __name__ == "__main__":
    mcp.run()
