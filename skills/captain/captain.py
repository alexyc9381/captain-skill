#!/usr/bin/env python3
"""The Captain check: make Claude call you "Captain" in every reply, and warn you the moment it stops.

    python3 captain.py on [--global]     add the rule to ./CLAUDE.md (or ~/.claude/CLAUDE.md) and the warning hook
    python3 captain.py off [--global]    take both out again
    python3 captain.py status            is the rule on here, and is the hook installed?
    python3 captain.py check             the Stop hook: reads the hook's JSON on stdin, warns when a reply has no "Captain"

Why it works: the rule sits with your other rules at the start of the chat. As a chat gets long, Claude pays less attention
to what came first (Anthropic calls this "context rot"), so the first rule you notice slipping is the one you can see in
every reply. No "Captain" means your rules have dropped out of focus: start a fresh chat.
"""
import json
import os
import re
import sys

START = "<!-- captain-skill:start -->"
END = "<!-- captain-skill:end -->"
NAME = os.environ.get("CAPTAIN_NAME", "Captain")
RULE = f"""{START}
## The Captain check
Call me "{NAME}" in every reply you write to me, at least once, for example "Aye, {NAME}." or "Done, {NAME}."
This rule never expires, no matter how long this chat gets. It tells me you are still following the rules in this file.
{END}
"""
HOOK_CMD = "python3 " + os.path.abspath(__file__) + " check"
WARNING = (f'⚓ Claude stopped calling you "{NAME}". Your rules are slipping out of focus (context rot). '
           "Start a fresh chat (/clear) so it reads them again from the top.")


def claude_md(global_):
    return os.path.expanduser("~/.claude/CLAUDE.md") if global_ else os.path.join(os.getcwd(), "CLAUDE.md")


def settings_path(global_):
    return os.path.expanduser("~/.claude/settings.json") if global_ else os.path.join(os.getcwd(), ".claude", "settings.json")


def strip_rule(text):
    return re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", text, flags=re.S)


def has_rule(text):
    return START in text and END in text


def plugin_installed():
    """The plugin ships the hook itself (hooks/hooks.json); then the settings hook would warn twice."""
    root = os.path.expanduser("~/.claude/plugins")
    for dirpath, dirnames, _ in os.walk(root):
        if "captain-skill" in os.path.basename(dirpath):
            return True
        if dirpath.count(os.sep) - root.count(os.sep) > 4:
            dirnames[:] = []
    return False


def add_hook(path):
    s = json.load(open(path)) if os.path.exists(path) else {}
    stop = s.setdefault("hooks", {}).setdefault("Stop", [])
    if any("captain.py check" in h.get("command", "") for g in stop for h in g.get("hooks", [])):
        return False
    stop.append({"hooks": [{"type": "command", "command": HOOK_CMD}]})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(s, open(path, "w"), indent=2)
    return True


def remove_hook(path):
    if not os.path.exists(path):
        return False
    s = json.load(open(path))
    stop = s.get("hooks", {}).get("Stop", [])
    keep = [g for g in stop if not any("captain.py check" in h.get("command", "") for h in g.get("hooks", []))]
    if len(keep) == len(stop):
        return False
    s["hooks"]["Stop"] = keep
    if not keep:
        del s["hooks"]["Stop"]
    json.dump(s, open(path, "w"), indent=2)
    return True


def cmd_on(global_):
    p = claude_md(global_)
    text = open(p).read() if os.path.exists(p) else ""
    if not has_rule(text):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text + ("\n" if text and not text.endswith("\n") else "") + ("\n" if text else "") + RULE)
        print(f"rule added to {p}")
    else:
        print(f"rule already in {p}")
    if plugin_installed():
        print("warning hook: on (the plugin runs it)")
    elif add_hook(settings_path(global_)):
        print(f"warning hook added to {settings_path(global_)}")
    else:
        print("warning hook: already on")
    print(f'From your next chat, every reply says "{NAME}". The reply that doesn\'t is your signal to start fresh.')


def cmd_off(global_):
    p = claude_md(global_)
    text = open(p).read() if os.path.exists(p) else ""
    if has_rule(text):
        open(p, "w").write(strip_rule(text).rstrip("\n") + "\n" if strip_rule(text).strip() else "")
        print(f"rule removed from {p}")
    if remove_hook(settings_path(global_)):
        print(f"warning hook removed from {settings_path(global_)}")


def rule_active(cwd):
    """The rule is on if any CLAUDE.md Claude reads here has it: ~/.claude, then this folder and every folder above it."""
    paths = [os.path.expanduser("~/.claude/CLAUDE.md")]
    d = os.path.abspath(cwd or os.getcwd())
    while True:
        paths += [os.path.join(d, "CLAUDE.md"), os.path.join(d, ".claude", "CLAUDE.md")]
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    return any(os.path.exists(p) and has_rule(open(p, errors="ignore").read()) for p in paths)


def last_reply(transcript_path):
    """The text of Claude's last reply in a Claude Code transcript (JSON lines), or None."""
    text = None
    try:
        lines = open(transcript_path, errors="ignore").read().splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "user" and not e.get("isMeta") and isinstance(e.get("message", {}).get("content"), str):
            break                                      # the user's last message: nothing after it had text
        if e.get("type") != "assistant":
            continue
        parts = [c.get("text", "") for c in e.get("message", {}).get("content", []) if isinstance(c, dict) and c.get("type") == "text"]
        if any(p.strip() for p in parts):
            text = "\n".join(parts)
            break
    return text


def says_name(text):
    return re.search(r"\b" + re.escape(NAME) + r"\b", text, re.I) is not None


def cmd_check(stdin):
    try:
        data = json.loads(stdin or "{}")
    except ValueError:
        return 0
    if data.get("stop_hook_active") or not rule_active(data.get("cwd")):
        return 0
    text = last_reply(data.get("transcript_path", ""))
    if text and not says_name(text):
        print(json.dumps({"systemMessage": WARNING}))
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    g = "--global" in argv
    if argv[0] == "on":
        cmd_on(g)
    elif argv[0] == "off":
        cmd_off(g)
    elif argv[0] == "status":
        print("rule:", "on" if rule_active(os.getcwd()) else "off")
        print("hook:", "plugin" if plugin_installed() else
              ("on" if any(os.path.exists(settings_path(x)) and "captain.py check" in open(settings_path(x)).read()
                           for x in (False, True)) else "off"))
    elif argv[0] == "check":
        return cmd_check(sys.stdin.read())
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
