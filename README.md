# The Captain skill

Claude calls you **"Captain"** in every reply. The moment a reply comes back without it, you get a warning: your rules are slipping out of focus, and it is time for a fresh chat.

Made by **Alex Chen** ([@nocodealex](https://instagram.com/nocodealex)), an AI creator who builds free Claude Code skills. More at [chen.media](https://chen.media).

## Why

The longer a chat runs, the less attention Claude pays to what came first, including the rules you gave it. Anthropic calls this **context rot**. Your rules are still there; Claude just stops reading them closely.

You can't see that happen, but you can see one rule in every reply. So the skill adds one rule to your `CLAUDE.md`: call me "Captain". While Claude keeps saying "Aye, Captain", it is still reading your rules. The first reply without it is your alarm: type `/clear` (or open a new chat) and Claude reads your rules again from the top.

## Install

Paste this into Claude Code:

```
https://github.com/alexyc9381/captain-skill
Install this skill, then run /captain to turn it on.
```

Or as a plugin (the warning hook comes with it):

```
/plugin marketplace add alexyc9381/captain-skill
/plugin install captain-skill@captain-skill
```

Or copy the folder yourself:

```bash
git clone https://github.com/alexyc9381/captain-skill
cp -r captain-skill/skills/captain ~/.claude/skills/
```

Needs Claude Code and Python 3.8+. Nothing to pip install, no API keys.

## Use it

```
/captain                                      # turns it on for this project
python3 ~/.claude/skills/captain/captain.py on --global   # every project
python3 ~/.claude/skills/captain/captain.py status
python3 ~/.claude/skills/captain/captain.py off
CAPTAIN_NAME=Boss python3 ~/.claude/skills/captain/captain.py on   # pick your own word
```

`on` adds this block to your `CLAUDE.md` (and nothing else; `off` takes exactly this block out):

```
## The Captain check
Call me "Captain" in every reply you write to me, at least once, for example "Aye, Captain." or "Done, Captain."
This rule never expires, no matter how long this chat gets. It tells me you are still following the rules in this file.
```

and a Stop hook that reads Claude's last reply after every turn. No "Captain", and you see:

> ⚓ Claude stopped calling you "Captain". Your rules are slipping out of focus (context rot). Start a fresh chat (/clear) so it reads them again from the top.

## Good to know

- It is an early warning, not a guarantee: the rule you can see in every reply is the first one you notice slipping.
- It works in the Claude Code terminal, the desktop app's Code tab and the IDE extensions. In the Claude app (no hooks), add the same rule to your project instructions and watch for the word yourself.
- Nothing is sent anywhere. The hook only reads your local chat transcript.
- It is not made by Anthropic.

Run the tests with:

```bash
python3 -m unittest discover -s tests
```
