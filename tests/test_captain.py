import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "captain"))
import captain as C  # noqa: E402


def transcript(d, replies):
    p = os.path.join(d, "t.jsonl")
    with open(p, "w") as f:
        f.write(json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}) + "\n")
        for r in replies:
            f.write(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": r}]}}) + "\n")
    return p


class Captain(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.home = tempfile.mkdtemp()
        os.environ["HOME"] = self.home
        self.cwd = os.getcwd()
        os.chdir(self.d)

    def tearDown(self):
        os.chdir(self.cwd)

    def run_check(self, replies):
        out = io.StringIO()
        sys.stdin = io.StringIO(json.dumps({"cwd": self.d, "transcript_path": transcript(self.d, replies)}))
        with redirect_stdout(out):
            C.cmd_check(sys.stdin.read())
        return out.getvalue()

    def test_on_is_idempotent_and_keeps_other_rules(self):
        open("CLAUDE.md", "w").write("# My rules\nNo emojis.\n")
        with redirect_stdout(io.StringIO()):
            C.cmd_on(False)
            C.cmd_on(False)
        text = open("CLAUDE.md").read()
        self.assertEqual(text.count(C.START), 1)
        self.assertIn("No emojis.", text)
        s = json.load(open(".claude/settings.json"))
        self.assertEqual(len(s["hooks"]["Stop"]), 1)

    def test_off_removes_only_its_block(self):
        open("CLAUDE.md", "w").write("# My rules\nNo emojis.\n")
        with redirect_stdout(io.StringIO()):
            C.cmd_on(False)
            C.cmd_off(False)
        self.assertEqual(open("CLAUDE.md").read().strip(), "# My rules\nNo emojis.")
        self.assertNotIn("Stop", json.load(open(".claude/settings.json")).get("hooks", {}))

    def test_warns_when_captain_is_missing(self):
        with redirect_stdout(io.StringIO()):
            C.cmd_on(False)
        self.assertEqual(self.run_check(["Aye, Captain. Done."]), "")
        self.assertIn("stopped calling you", self.run_check(["Aye, Captain.", "Here is the file."]))

    def test_silent_when_rule_is_off(self):
        self.assertEqual(self.run_check(["Here is the file."]), "")

    def test_word_match(self):
        self.assertTrue(C.says_name("aye, captain!"))
        self.assertFalse(C.says_name("the captains log"))


if __name__ == "__main__":
    unittest.main()
