import unittest
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

sys.modules.setdefault(
    "pyxel",
    SimpleNamespace(
        init=lambda *args, **kwargs: None,
        mouse=lambda *args, **kwargs: None,
        btn=lambda *args, **kwargs: False,
        btnp=lambda *args, **kwargs: False,
        cls=lambda *args, **kwargs: None,
        run=lambda *args, **kwargs: None,
        quit=lambda *args, **kwargs: None,
        rect=lambda *args, **kwargs: None,
        rectb=lambda *args, **kwargs: None,
        text=lambda *args, **kwargs: None,
        blt=lambda *args, **kwargs: None,
        clip=lambda *args, **kwargs: None,
        mouse_x=0,
        mouse_y=0,
        mouse_wheel=0,
        frame_count=0,
        MOUSE_BUTTON_LEFT=0,
    ),
)

from ui.layout import Layout

spec = importlib.util.spec_from_file_location(
    "mud_client_ui_module",
    Path(__file__).parent.parent / "src" / "ui" / "MudClientUI.py",
)
mud_client_ui_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mud_client_ui_module)
MudClientUI = mud_client_ui_module.MudClientUI


class FakeApp:
    def __init__(self):
        self.components = []

    def clear_components(self) -> None:
        self.components.clear()

    def add(self, component) -> None:
        self.components.append(component)


class TestMudClientUIToggle(unittest.TestCase):
    def _build_ui(self) -> MudClientUI:
        ui = MudClientUI.__new__(MudClientUI)
        ui.layout = Layout(game_w=256, ui_w=400, h=400, game_h=400, gutter=1)
        ui._configured_game_w = 256
        ui._configured_ui_w = 400
        ui._configured_gutter = 1
        ui._show_graphics = True
        ui.menu_bar = SimpleNamespace(width=ui.layout.w)
        ui.app = FakeApp()
        ui.gate = SimpleNamespace()
        ui.message_dialog = SimpleNamespace()
        ui.connection_settings = SimpleNamespace()
        ui.display_settings = SimpleNamespace()
        ui._toggle_graphics_menu_item = SimpleNamespace(label="Hide Graphics")
        ui.handle_command = lambda cmd: None
        ui.logged = []
        ui.log = ui.logged.append
        return ui

    def test_refresh_render_mode_layout_expands_text_pane_without_graphics(self):
        ui = self._build_ui()

        ui._show_graphics = False
        ui._refresh_render_mode_layout()

        self.assertEqual(ui.layout.game_w, 0)
        self.assertEqual(ui.layout.ui_w, 657)
        self.assertEqual(ui.layout.gutter, 0)
        self.assertEqual(ui.menu_bar.width, 657)

        ui._show_graphics = True
        ui._refresh_render_mode_layout()

        self.assertEqual(ui.layout.game_w, 256)
        self.assertEqual(ui.layout.ui_w, 400)
        self.assertEqual(ui.layout.gutter, 1)
        self.assertEqual(ui.menu_bar.width, 657)

    def test_toggle_graphics_remounts_components_and_updates_menu_label(self):
        ui = self._build_ui()

        ui._mount_components()
        initial_types = [type(component).__name__ for component in ui.app.components]
        self.assertIn("GameWorld", initial_types)
        self.assertIn("Divider", initial_types)

        ui.toggle_graphics()

        toggled_types = [type(component).__name__ for component in ui.app.components]
        self.assertNotIn("GameWorld", toggled_types)
        self.assertNotIn("Divider", toggled_types)
        self.assertEqual(ui._toggle_graphics_menu_item.label, "Show Graphics")
        self.assertEqual(ui.logged[-1], "Graphics disabled. Telnet client is now the only rendered pane.")

        ui.toggle_graphics()

        restored_types = [type(component).__name__ for component in ui.app.components]
        self.assertIn("GameWorld", restored_types)
        self.assertIn("Divider", restored_types)
        self.assertEqual(ui._toggle_graphics_menu_item.label, "Hide Graphics")
        self.assertEqual(ui.logged[-1], "Graphics enabled. Game board restored.")


if __name__ == "__main__":
    unittest.main()
