"""
Test argparse functionality for springs-of-mud-ui.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

sys.modules["ui.MudClientUI"] = type(sys)("ui.MudClientUI")
sys.modules["ui.MudClientUI"].MudClientUI = lambda *args, **kwargs: None

import importlib.util

spec = importlib.util.spec_from_file_location(
    "main",
    Path(__file__).parent.parent / "src" / "springs-of-mud-ui.py",
)
main_module = importlib.util.module_from_spec(spec)


class TestArgparseSpringsOfMudUI(unittest.TestCase):
    def setUp(self):
        spec.loader.exec_module(main_module)

    def test_parse_arguments_missing_required(self):
        sys.argv = ["springs-of-mud-ui"]
        with self.assertRaises(SystemExit):
            main_module.parse_arguments()
        print("[PASS] test_parse_arguments_missing_required")

    def test_parse_arguments_install_dir_short(self):
        sys.argv = ["springs-of-mud-ui", "-i", "/tmp/test"]
        args = main_module.parse_arguments()

        self.assertEqual(args.install_dir, "/tmp/test")
        self.assertIs(args.verbose, False)
        print("[PASS] test_parse_arguments_install_dir_short")

    def test_parse_arguments_install_dir_long(self):
        sys.argv = ["springs-of-mud-ui", "--install-dir", "/home/user/mud"]
        args = main_module.parse_arguments()

        self.assertEqual(args.install_dir, "/home/user/mud")
        self.assertIs(args.verbose, False)
        print("[PASS] test_parse_arguments_install_dir_long")

    def test_parse_arguments_verbose(self):
        sys.argv = ["springs-of-mud-ui", "-i", "/tmp/test", "-v"]
        args = main_module.parse_arguments()

        self.assertEqual(args.install_dir, "/tmp/test")
        self.assertIs(args.verbose, True)
        print("[PASS] test_parse_arguments_verbose")

    def test_parse_arguments_combined(self):
        sys.argv = ["springs-of-mud-ui", "-i", "/opt/mud", "--verbose"]
        args = main_module.parse_arguments()

        self.assertEqual(args.install_dir, "/opt/mud")
        self.assertIs(args.verbose, True)
        print("[PASS] test_parse_arguments_combined")

    def test_setup_install_dir_new(self):
        test_dir = Path("C:/tmp/test_mud_install_new")
        if test_dir.exists():
            if (test_dir / "resources").exists():
                (test_dir / "resources").rmdir()
            test_dir.rmdir()

        result = main_module.setup_install_dir(str(test_dir), verbose=False)

        self.assertEqual(result, test_dir.resolve())
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())
        self.assertTrue((result / "resources").exists())
        self.assertTrue((result / "resources").is_dir())

        (test_dir / "resources").rmdir()
        test_dir.rmdir()
        print("[PASS] test_setup_install_dir_new")

    def test_setup_install_dir_existing(self):
        test_dir = Path("C:/tmp/test_mud_install_existing")
        test_dir.mkdir(exist_ok=True)

        result = main_module.setup_install_dir(str(test_dir), verbose=False)

        self.assertEqual(result, test_dir.resolve())
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())
        self.assertTrue((result / "resources").exists())

        (test_dir / "resources").rmdir()
        test_dir.rmdir()
        print("[PASS] test_setup_install_dir_existing")

    def test_setup_install_dir_relative(self):
        result = main_module.setup_install_dir(".", verbose=False)

        self.assertTrue(result.is_absolute())
        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())
        self.assertTrue((result / "resources").exists())
        print("[PASS] test_setup_install_dir_relative")


if __name__ == "__main__":
    unittest.main()
