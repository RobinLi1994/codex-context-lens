import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("context_lens_package", ROOT / "scripts/package.py")
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def test_zip_preserves_executable_bit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "run-python.sh"
            script.write_text("#!/bin/sh\n")
            script.chmod(0o755)
            manifest = root / "plugin.json"
            manifest.write_text("{}")
            archive = root / "plugin.zip"

            package.write_zip(archive, [(script, "plugin/run-python.sh"),
                                        (manifest, "plugin/plugin.json")])

            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual(bundle.getinfo("plugin/run-python.sh").external_attr >> 16 & 0o777, 0o755)
                self.assertEqual(bundle.getinfo("plugin/plugin.json").external_attr >> 16 & 0o777, 0o644)


if __name__ == "__main__":
    unittest.main()
