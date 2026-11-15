"""Focused make_product contracts; finite input fixtures, not a cold-build test.

Only load_archive and overlay_files are replaced. The real product transformer,
collision guard, inner checksum writer and root manifest writer are exercised.
Set MAS_CURRENT_BUILD to select a builder outside the usual release/tests tree.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
DEFAULT_BUILDER = Path(__file__).resolve().parents[1] / "current" / "build.py"
BUILDER = Path(os.environ.get("MAS_CURRENT_BUILD", str(DEFAULT_BUILDER))).resolve()
RELEASE = BUILDER.parent.parent
REPOSITORY = RELEASE.parent.parent
spec = importlib.util.spec_from_file_location("license_product_under_test", BUILDER)
current = importlib.util.module_from_spec(spec)
spec.loader.exec_module(current)

BASE_SHA = "5e2f86298c08182eb7f2f3500ff767adc4b2a21e59a64a8c5c6993333f5b4d73"
VERSION = "0.3.0-rc.14"
OVERRIDES = ("core/RIGHTS.md", "source/SOURCES.md")
SKILLS = (
    "beginner-ops-writing",
    "dispatch-accept-verify",
    "evidence-before-done",
    "ops-case-notes",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def reference_tree(files, component):
    """The documented component-tree wire format, independent of current.tree."""
    prefix = component + "/"
    members = {name[len(prefix):]: data for name, data in files.items()
               if name.startswith(prefix)}
    records = b"".join(
        (sha(members[name]) + "  " + name + "\n").encode()
        for name in sorted(members, key=lambda value: value.encode())
    )
    return {"file_count": len(members), "sha256": sha(records)}


class CurrentLicenseProductTest(unittest.TestCase):
    def setUp(self):
        # Reuse the actual frozen prose required by existing exact transforms.
        # This is a small fixture, not a reconstruction of the RC5 release.
        self.base = {}
        for name in ("index.html", "README.md", "README.en.md", "SCOPE.md"):
            raw = (RELEASE / "payload" / (name + ".in")).read_bytes()
            self.base[name] = raw.replace(b"[[MAS:version]]", b"0.2.2-rc.5")
        self.base.update({
            "core/RIGHTS.md": (RELEASE / "payload/core/RIGHTS.md").read_bytes(),
            "source/SOURCES.md": (REPOSITORY / "mas/source/SOURCES.md").read_bytes(),
            "proof/authority/returned/README.md":
                (RELEASE / "payload/proof/authority/returned/README.md").read_bytes(),
            "core/skills-original/LICENSE": (REPOSITORY / "LICENSE").read_bytes(),
            "core/skills-original/NOTICE":
                (RELEASE / "original-notices/NOTICE").read_bytes(),
            "core/team-builder/adapters.js":
                (RELEASE / "payload/core/team-builder/adapters.js").read_bytes(),
            "source/web/core.js":
                (REPOSITORY / "mas/source/web/core.js").read_bytes(),
            "core/fixture-opaque.bin": b"\x00\xffopaque historical fixture\r\n",
            "builder/fixture.html": b"unchanged historical builder fixture\n",
            "resume/fixture.html": b"unchanged historical resume fixture\n",
        })
        for name in SKILLS:
            self.base["core/skills-original/skills/" + name + "/SKILL.md"] = (
                REPOSITORY / "skills" / name / "SKILL.md"
            ).read_bytes()
        self.base["core/checksums.json"] = encoded_json({
            name[len("core/"):]: sha(data)
            for name, data in sorted(self.base.items()) if name.startswith("core/")
        })
        components = ("core", "source", "builder", "resume")
        self.previous = {
            "format": "solo-to-team.release-checksums",
            "version": 1,
            "product_version": "0.2.2-rc.5",
            "component_trees": {
                name: reference_tree(self.base, name) for name in components
            },
            # These are deliberately synthetic archive identities.
            "components": {
                name: sha(("fixture archive " + name).encode()) for name in components
            },
            "files": {name: sha(data) for name, data in self.base.items()},
        }
        self.base["checksums.json"] = encoded_json(self.previous)
        self.overlay = {
            "index.html": b"<html>Current fixture [[PACKAGE_VERSION]]</html>\n",
            "core/RIGHTS.md": (
                b"# Current fixture rights\nMIT applies to this fixture material.\n"
                b"Publication approval is separate.\n"
            ),
            "source/SOURCES.md": (
                b"# Current fixture source scope\nMIT applies to this fixture source.\n"
                b"Host and third-party rights are separate.\n"
            ),
            "LICENSE": (REPOSITORY / "LICENSE").read_bytes(),
            "NOTICE": b"Fixture current notice: retained third-party notices still apply.\n",
        }

    def produce(self, overlay=None):
        supplied = self.overlay if overlay is None else overlay
        with patch.object(current, "load_archive",
                          return_value=(dict(self.base), copy.deepcopy(self.previous))), \
             patch.object(current, "overlay_files",
                          return_value=(dict(supplied), VERSION)):
            return current.make_product(Path("fixture-base-not-read.zip"))

    def test_exact_two_license_overrides_and_root_license_are_emitted(self):
        result = self.produce()
        for name in (*OVERRIDES, "LICENSE", "NOTICE"):
            with self.subTest(path=name):
                self.assertEqual(result[name], self.overlay[name])
        self.assertIn(VERSION.encode(), result["index.html"])

    def test_other_existing_paths_cannot_collide(self):
        # Establish a valid control so rejecting the permitted legal overrides
        # cannot make the negative cases pass for the wrong reason.
        self.produce()
        forbidden = (
            "core/team-builder/adapters.js",
            "source/web/core.js",
            "core/skills-original/skills/evidence-before-done/SKILL.md",
        )
        for name in forbidden:
            with self.subTest(path=name):
                edited = dict(self.overlay)
                edited[name] = b"unapproved replacement"
                with self.assertRaises(ValueError):
                    self.produce(edited)

    def test_missing_either_or_both_expected_license_overrides_is_rejected(self):
        for absent in (OVERRIDES, (OVERRIDES[0],), (OVERRIDES[1],)):
            with self.subTest(missing=absent):
                incomplete = {k: v for k, v in self.overlay.items() if k not in absent}
                with self.assertRaises(ValueError):
                    self.produce(incomplete)

    def test_core_checksum_covers_actual_bytes_and_excludes_itself(self):
        result = self.produce()
        actual = json.loads(result["core/checksums.json"])
        expected = {
            name[len("core/"):]: sha(data)
            for name, data in result.items()
            if name.startswith("core/") and name != "core/checksums.json"
        }
        self.assertEqual(actual, expected)
        self.assertNotIn("checksums.json", actual)
        self.assertEqual(actual["RIGHTS.md"], sha(self.overlay["core/RIGHTS.md"]))
        self.assertNotEqual(result["core/checksums.json"], self.base["core/checksums.json"])

    def test_root_manifest_covers_actual_output_and_current_version(self):
        result = self.produce()
        manifest = json.loads(result["checksums.json"])
        self.assertEqual(manifest["files"], {
            name: sha(data) for name, data in result.items() if name != "checksums.json"
        })
        self.assertEqual(manifest["product_version"], VERSION)
        self.assertEqual(manifest["base_release"],
                         {"version": "0.2.2-rc.5", "sha256": BASE_SHA})

    def test_changed_components_lose_old_archive_identity_only(self):
        result = self.produce()
        manifest = json.loads(result["checksums.json"])
        for name in ("core", "source", "builder", "resume"):
            with self.subTest(component=name):
                self.assertEqual(manifest["component_trees"][name],
                                 reference_tree(result, name))
        self.assertNotIn("core", manifest["components"])
        self.assertNotIn("source", manifest["components"])
        self.assertEqual(manifest["components"], {
            name: self.previous["components"][name] for name in ("builder", "resume")
        })

    def test_original_skills_and_other_historical_payload_bytes_are_preserved(self):
        result = self.produce()
        for name, data in self.base.items():
            if name.startswith(("core/", "source/", "builder/", "resume/")) \
                    and name not in (*OVERRIDES, "core/checksums.json"):
                with self.subTest(path=name):
                    self.assertIn(name, result)
                    self.assertEqual(result[name], data)

    def test_frozen_base_identity_and_historical_inputs_are_not_redefined(self):
        self.assertEqual(current.BASE, BASE_SHA)
        self.assertEqual(current.OLD_VERSION, "0.2.2-rc.5")
        frozen = {
            "mas/release/release.json":
                "7d26b818d06ce925b6cf514aa66821d28cb233232684fcaed2a184cdddd95279",
            "mas/release/expected.json":
                "324b762902dd0c0d7ba50bcad25843412952adc28c4d153d8b25641f33639e84",
            "mas/release/payload/core/RIGHTS.md":
                "91feb8657de39a9e5a20599c950172b4139e914cdc61f7dce53bbc08c86b75fe",
            "mas/source/SOURCES.md":
                "fffa4ae6dc1b4ff8d6d9457307d781762fda8ffdf594772fee29d57da6579752",
            "mas/release/original-notices/NOTICE":
                "2479828705968359259bbe2637fe43f8ed0d46f477e48b6b94498c634e02f5e8",
            "LICENSE":
                "5d63ea4387f51228fe2f5d313203c401fad2121e2fbf60354234b92dd2559001",
        }
        for name, digest in frozen.items():
            with self.subTest(path=name):
                self.assertEqual(sha((REPOSITORY / name).read_bytes()), digest)


if __name__ == "__main__":
    unittest.main()
