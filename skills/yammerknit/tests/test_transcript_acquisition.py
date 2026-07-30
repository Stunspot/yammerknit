from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "yammerknit_tool.py"
SPEC = importlib.util.spec_from_file_location("yammerknit_tool_transcript", MODULE_PATH)
assert SPEC and SPEC.loader
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class TranscriptBoundaryTests(unittest.TestCase):
    def test_command_is_subtitle_only_and_credential_free(self) -> None:
        command = tool.yt_dlp_command(
            "yt-dlp",
            "https://www.youtube.com/watch?v=test123",
            Path("stage"),
            "en",
        )
        required = {
            "--ignore-config",
            "--no-plugin-dirs",
            "--no-remote-components",
            "--no-playlist",
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--no-overwrites",
            "--no-cookies",
            "--no-cookies-from-browser",
        }
        self.assertTrue(required.issubset(command))
        forbidden = {
            "--extract-audio",
            "--audio-format",
            "--cookies",
            "--cookies-from-browser",
            "--username",
            "--password",
        }
        self.assertTrue(forbidden.isdisjoint(command))

    def test_non_youtube_url_is_rejected(self) -> None:
        with self.assertRaises(tool.YammerknitError):
            tool.validate_youtube_url("https://example.com/watch?v=test123")

    def test_fake_backend_creates_governed_source_record(self) -> None:
        observed_command: list[str] = []

        def fake_run(command: list[str], **_: object) -> SimpleNamespace:
            observed_command.extend(command)
            output_template = Path(command[command.index("--output") + 1])
            subtitle = Path(str(output_template).replace("%(id)s", "test123").replace("%(ext)s", "en.vtt"))
            subtitle.parent.mkdir(parents=True, exist_ok=True)
            subtitle.write_text(
                "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nA semantic mesh 🕸️.\n",
                encoding="utf-8",
            )
            return SimpleNamespace(
                returncode=0,
                stdout=(
                    "YAMMERKNIT_META\ttest123\tTest Channel\t20260729\t"
                    "A Semantic Mesh\thttps://www.youtube.com/watch?v=test123\n"
                ),
                stderr="",
            )

        with tempfile.TemporaryDirectory() as temp:
            with patch.object(tool.shutil, "which", return_value="yt-dlp"), patch.object(
                tool.subprocess, "run", side_effect=fake_run
            ):
                result = tool.acquire_youtube(
                    url="https://www.youtube.com/watch?v=test123",
                    rights_basis=None,
                    workspace=Path(temp),
                    languages="en",
                    backend="yt-dlp",
                )

            source_dir = Path(result["source_directory"])
            manifest = json.loads(
                (source_dir / "source-manifest.json").read_text(encoding="utf-8")
            )
            self.assertTrue((source_dir / manifest["files"]["original"]).is_file())
            self.assertIsNone(manifest["rights_basis"])
            self.assertEqual(manifest["acquisition"]["backend"], "yt-dlp")
            normalized = (source_dir / "source.txt").read_text(encoding="utf-8")
            self.assertEqual(normalized, "[00:00:01.000] A semantic mesh 🕸️.\n")
            self.assertIn("--skip-download", observed_command)
            self.assertNotIn("--cookies-from-browser", observed_command)


if __name__ == "__main__":
    unittest.main()
