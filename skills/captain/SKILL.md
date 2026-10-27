---
name: captain
description: Turn on the Captain check. Claude calls you "Captain" in every reply, and the moment a reply comes back without it you get a warning that your rules are slipping (context rot) and it is time for a fresh chat. Use when the user says /captain, "captain check", "tell me when Claude stops following my rules", or asks how to spot context rot.
---

# The Captain check

One tiny rule tells you, in every reply, whether Claude is still reading your rules.

## Turn it on

Run this (it is safe to run twice):

```bash
python3 "<this skill's folder>/captain.py" on
```

- `on` adds the rule to `./CLAUDE.md` in the project you are in. Add `--global` to put it in `~/.claude/CLAUDE.md` for every project.
- It also adds the warning hook (a Stop hook) unless the captain-skill plugin is installed, which runs the hook itself.
- If the user wants a different word than "Captain", set `CAPTAIN_NAME` before running it, e.g. `CAPTAIN_NAME=Boss`.

Then tell the user, in one or two short lines:
1. From their next chat, every reply says "Captain".
2. The first reply without it means the rules at the top of the chat have slipped out of focus: type /clear (or open a new chat) and carry on. Claude reads the rules again from the top.

From now on in this chat, follow the rule yourself: call the user "Captain" in every reply.

## Other commands

```bash
python3 "<this skill's folder>/captain.py" status          # is the rule on here, is the hook on?
python3 "<this skill's folder>/captain.py" off [--global]  # take the rule and the hook out
```

## Rules for you

- Never remove or reword other parts of the user's CLAUDE.md. `captain.py` only touches the block between its own markers.
- Never say the check proves Claude followed every rule. It is an early warning: the rule you can see in every reply is the
  first one you notice slipping.
