from __future__ import annotations

import json
import random
import time
from typing import Any

import requests

from domain.PlayerCharacter import PlayerCharacter


class CharacterCreation:
    ENDPOINTS = {
        "classes": "/classes",
        "races": "/races",
        "skills": "/skills",
        "spells": "/spells",
        "rooms": "/rooms",
        "items": "/items",
        "game": "/game",
    }
    ALIGNMENT_MAP = {"g": 750, "good": 750, "n": 0, "neutral": 0, "e": -750, "evil": -750}
    SEX_MAP = {"m": "male", "male": "male", "f": "female", "female": "female"}
    ROM_WEAPONS = {"axe", "dagger", "flail", "mace", "polearm", "spear", "sword", "whip", "staff"}
    TEMPLE_VNUM = 3001
    CLASS_MAP = {"mage": 0, "cleric": 1, "thief": 2, "warrior": 3}

    def __init__(self, api_base_url: str, account_id: str) -> None:
        self.api_base_url = api_base_url
        self.account_id = account_id
        self.state: dict | None = None
        raw_game_data = self._fetch_json(self.ENDPOINTS["game"])
        self.game_data = raw_game_data[0] if isinstance(raw_game_data, list) and raw_game_data else raw_game_data
        self.skills = self._fetch_json(self.ENDPOINTS["skills"]) or []
        self.spells = self._fetch_json(self.ENDPOINTS["spells"]) or []
        self.classes = self._fetch_json(self.ENDPOINTS["classes"]) or []
        self.races = self._fetch_json(self.ENDPOINTS["races"]) or []
        self.rooms = self._fetch_json(self.ENDPOINTS["rooms"]) or []
        self.items = self._fetch_json(self.ENDPOINTS["items"]) or []
        self.pc_races = self.game_data.get("pcRaces", self.game_data.get("pc_races", {})) if isinstance(self.game_data, dict) else {}
        self.groups = self.game_data.get("groups", {}) if isinstance(self.game_data, dict) else {}
        self.weapons = self.game_data.get("weapons", {}) if isinstance(self.game_data, dict) else {}
        self.item_lookup = {
            str(item.get("vnum", "")).strip(): item
            for item in self.items
            if isinstance(item, dict) and str(item.get("vnum", "")).strip()
        }
        self.skill_lookup = {
            str(skill.get("name", "")).strip().lower(): skill
            for skill in self.skills
            if isinstance(skill, dict) and isinstance(skill.get("name"), str)
        }
        self.spell_lookup = {
            str(spell.get("name", "")).strip().lower(): spell
            for spell in self.spells
            if isinstance(spell, dict) and isinstance(spell.get("name"), str)
        }
        self.class_lookup = {
            str(character_class.get("name", "")).strip().lower(): character_class
            for character_class in self.classes
            if isinstance(character_class, dict) and isinstance(character_class.get("name"), str)
        }
        self.race_lookup = {
            str(race.get("name", "")).strip().lower(): race
            for race in self.races
            if isinstance(race, dict) and isinstance(race.get("name"), str)
        }
        self.available_choices: list[dict] = []

    def _fetch_json(self, endpoint: str) -> dict:
        url = f"{self.api_base_url}/api/v1{endpoint}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch JSON from {url}: {response.status_code}")
        return response.json()

    @property
    def active(self) -> bool:
        return self.state is not None

    def help_lines(self) -> list[str]:
        return [
            "create-char start",
            "create-char show",
            "create-char submit",
            "create-char cancel",
            "After 'start', just type answers like ROM nanny prompts.",
        ]

    def start(self) -> list[str]:
        self.state = {
            "state": "get_name",
            "name": None,
            "race": None,
            "sex": None,
            "characterClass": None,
            "alignment": None,
            "customize": None,
            "weapon": None,
            "selectedGroups": [],
            "selectedSkills": [],
            "selectedSpells": [],
            "lockedGroups": [],
            "raceSkills": [],
            "standaloneSkills": [],
            "racePoints": 0,
            "raceBasePoints": 0,
            "raceSkillPoints": 0,
            "points": 0,
            "pointsChosen": 0,
            "expPerLevel": 1000,
            "trainBonus": 0,
            "raceStats": {},
            "raceMaxStats": {},
        }
        return ["New character.", "Name: "]

    def cancel(self) -> list[str]:
        self.state = None
        return ["Character creation canceled."]

    def show_lines(self) -> list[str]:
        if not self.state:
            return ["No active character creation. Run: create-char start"]
        lines = [json.dumps(self.state, indent=2)]
        payload = self.build_payload_dict()
        if payload is not None:
            lines.append(json.dumps(payload, indent=2))
        return lines

    def prompt_current_state(self) -> list[str]:
        if not self.state:
            return []
        phase = self.state.get("state")
        prompts = {
            "get_name": ["Name: "],
            "confirm_name": [f"Did I get that right, {self.state.get('name', '')} (Y/N)? "],
            "get_race": ["What is your race (help for more information)? "],
            "get_sex": ["What is your sex (M/F)? "],
            "get_class": ["What is your class? "],
            "get_alignment": ["Which alignment (G/N/E)? "],
            "default_choice": ["Customize (Y/N)? "],
            "gen_groups": ["Choices are: list, learned, premise, add, drop, info, help, and done."],
            "complete": ["Type 'create-char submit' to send."],
        }
        if phase == "pick_weapon":
            return self._weapon_choice_prompt_lines()
        return prompts.get(phase, [])

    def handle_input(self, raw: str) -> list[str]:
        if not self.state:
            return []

        text = raw.strip()
        low = text.lower()

        phase = self.state.get("state")
        if low in ("cancel", "quit", "abort"):
            return self.cancel()
        if low == "help" and phase != "gen_groups":
            return self.help_lines() + self.prompt_current_state()
        if low == "show":
            return self.show_lines() + self.prompt_current_state()

        if phase == "get_name":
            if not text:
                return ["Name: "]
            self.state["name"] = text
            self.state["state"] = "confirm_name"
            return [f"Did I get that right, {text} (Y/N)? "]

        if phase == "confirm_name":
            if low in ("y", "yes"):
                self.state["state"] = "get_race"
                return self._option_lines("races") + ["What is your race (help for more information)? "]
            if low in ("n", "no"):
                self.state["name"] = None
                self.state["state"] = "get_name"
                return ["Ok, what IS it, then? "]
            return ["Please type Yes or No? "]

        if phase == "get_race":
            race = self._resolve_option("races", text)
            if race is None:
                return ["That is not a valid race."] + self._option_lines("races") + ["What is your race (help for more information)? "]
            self.state["race"] = race
            self.state["raceBasePoints"] = self._race_points(race)
            self.state["raceSkillPoints"] = 0
            self.state["racePoints"] = self.state["raceBasePoints"]
            self.state["points"] = self.state["raceBasePoints"]
            self.state["pointsChosen"] = self.state["points"]
            self.state["raceSkills"] = self._race_skills(race)
            self.state["raceStats"] = self._race_stats(race)
            self.state["raceMaxStats"] = self._race_max_stats(race)
            self._sync_selected_skills()
            self.state["state"] = "get_sex"
            return ["What is your sex (M/F)? "]

        if phase == "get_sex":
            sex = self.SEX_MAP.get(low)
            if sex is None:
                return ["That's not a sex.", "What IS your sex? "]
            self.state["sex"] = sex
            self.state["state"] = "get_class"
            return self._option_lines("classes") + ["What is your class? "]

        if phase == "get_class":
            character_class = self._resolve_option("classes", text)
            if character_class is None:
                return ["That's not a class.", "What IS your class? "]
            self.state["characterClass"] = character_class
            self.state["raceSkillPoints"] = self._class_points(character_class, self._race_data(self.state["race"]))
            self.state["racePoints"] = self.state["raceBasePoints"] + self.state["raceSkillPoints"]
            self.state["points"] = self.state["racePoints"]
            self.state["pointsChosen"] = self.state["racePoints"]
            self._sync_selected_skills()
            self._refresh_exp(character_class)
            self.state["state"] = "get_alignment"
            return ["You may be good, neutral, or evil.", "Which alignment (G/N/E)? "]

        if phase == "get_alignment":
            alignment = self.ALIGNMENT_MAP.get(low)
            if alignment is None:
                return ["That's not a valid alignment.", "Which alignment (G/N/E)? "]
            self.state["alignment"] = alignment
            self.state["selectedGroups"] = self._default_base_groups()
            self.state["lockedGroups"] = list(self.state["selectedGroups"])
            self._sync_selected_skills()
            self._refresh_exp()
            self.state["state"] = "default_choice"
            return [
                "Do you wish to customize this character?",
                "Customization takes time, but allows a wider range of skills and abilities.",
                "Customize (Y/N)? ",
            ]

        if phase == "default_choice":
            if low in ("y", "yes"):
                self.state["customize"] = True
                self.state["pointsChosen"] = self.state["points"]
                self._refresh_exp()
                self.state["state"] = "gen_groups"
                return [
                    "Character customization mode.",
                    "Choices are: list, learned, premise, add, drop, info, help, and done.",
                ] + self._creation_points_lines()
            if low in ("n", "no"):
                self.state["customize"] = False
                self._apply_default_group()
                self._sync_selected_skills()
                self._refresh_exp()
                self.state["state"] = "pick_weapon"
                return self._weapon_choice_prompt_lines()
            return ["Please answer (Y/N)? "]

        if phase == "gen_groups":
            if low == "help":
                return ["Choices are: list, learned, premise, add, drop, info, help, and done."]
            if low == "list":
                return self._list_group_cost_lines() + self._creation_points_lines()
            if low == "learned":
                return self._selected_groups_lines() + self._creation_points_lines()
            if low == "premise":
                return ["Premise: customize to tune creation points and experience-per-level tradeoffs."]
            if low.startswith("info"):
                parts = text.split(maxsplit=1)
                if len(parts) < 2:
                    return ["Info on which group or skill?"]
                return self._info_lines(parts[1].strip())
            if low == "done":
                if self.state["points"] == self.state["racePoints"]:
                    return ["You didn't pick anything."]
                min_points = 40 + self.state["racePoints"]
                if self.state["points"] <= min_points:
                    return [f"You must take at least {min_points} points of skills and groups"]
                self._sync_selected_skills()
                self._refresh_exp()
                self.state["state"] = "pick_weapon"
                return self._creation_points_lines() + self._weapon_choice_prompt_lines()

            parts = text.split(maxsplit=1)
            if len(parts) == 2 and parts[0].lower() == "add":
                return self._add_choice(parts[1].strip())
            if len(parts) == 2 and parts[0].lower() == "drop":
                return self._drop_choice(parts[1].strip())
            if low == "add":
                return ["You must provide a skill name."]
            if low == "drop":
                return ["You must provide a skill to drop."]
            return ["Choices are: list, learned, premise, add, drop, info, help, and done."]

        if phase == "pick_weapon":
            weapon = self._resolve_option("weapons", text)
            if weapon is None or weapon.lower() not in set(s.lower() for s in self.state.get("selectedSkills", [])):
                return ["That's not a valid selection. Choices are:"] + self._weapon_choice_prompt_lines()
            self.state["weapon"] = weapon
            self.state["state"] = "complete"
            payload = self.build_payload_dict()
            if payload is None:
                return ["Unable to build payload."]
            return ["Character creation payload:", json.dumps(payload, indent=2), "Type 'create-char submit' to send."]

        if phase == "complete":
            return ["Creation complete. Type 'create-char submit' or 'create-char cancel'."]

        return []

    def build_player_character(self) -> PlayerCharacter | None:
        if not self.state or self.state.get("state") != "complete":
            return None

        room = self._resolve_temple_room()
        if room is None:
            raise ValueError("Failed to resolve temple room for character creation")
        room_id = room.get("id")
        area_id = room.get("areaId")
        character_class = self.state["characterClass"]
        character_race = self.state["race"]
        class_meta = self._class_meta(character_class)
        race_data = self._race_data(character_race)
        race_stats = self._class_stats(character_class, race_data)
        race_max_stats = self._class_max_stats(character_class, race_data)
        strength = min(int(race_stats.get("str", 13)), int(race_max_stats.get("str", 99)))
        intelligence = min(int(race_stats.get("int", 13)), int(race_max_stats.get("int", 99)))
        wisdom = min(int(race_stats.get("wis", 13)), int(race_max_stats.get("wis", 99)))
        dexterity = min(int(race_stats.get("dex", 13)), int(race_max_stats.get("dex", 99)))
        constitution = min(int(race_stats.get("con", 13)), int(race_max_stats.get("con", 99)))

        character_attributes = {
            "strength": strength,
            "intelligence": intelligence,
            "wisdom": wisdom,
            "dexterity": dexterity,
            "constitution": constitution,
            "alignment": self.state["alignment"],
            "max_weight": 10000000,
            "max_items": 10000000,
            "position": 8,
            "wimpy": 0,
            "trains": 3 + int(self.state.get("trainBonus", 0)),
            "practices": 5,
            "points": int(self.state.get("points", 0)),
            "experience": 0,
            "accumulated_experience": 0,
            "experience_per_level": int(self.state.get("expPerLevel", 1000)),
        }
        character_class = {
            "name": self._presented_class_name(class_meta, self.state["characterClass"]),
            "attr_prime": 0,
            "weapon": 0,
            "guild": 0,
            "skill_adept": int(class_meta.get("skillAdept", class_meta.get("skill_adept", 75))),
            "thac000": int(class_meta.get("thac000", 20)),
            "thac032": int(class_meta.get("thac032", 0)),
            "hp_min": int(class_meta.get("hpMin", class_meta.get("hp_min", 8))),
            "hp_max": int(class_meta.get("hpMax", class_meta.get("hp_max", 12))),
            "mana_gain": bool(class_meta.get("fMana", class_meta.get("mana_gain", False))),
            "base_group": self._non_blank_value(
                class_meta.get("baseGroup"),
                class_meta.get("base_group"),
                f"{self.state['characterClass'].lower()} basics",
            ),
            "default_group": self._non_blank_value(
                class_meta.get("defaultGroup"),
                class_meta.get("default_group"),
                f"{self.state['characterClass'].lower()} default",
            ),
        }
        prompt_format = {
            "hp": True, "max_hp": False, "mana": True, "max_mana": False,
            "movement": True, "max_movement": False, "xp": False, "max_xp": False,
            "gold": False, "silver": False, "alignment": False, "room_name": False,
            "exits": False, "room_vnum": False, "area_name": False, "carriage_return": False,
        }
        equipped, inventory = self._starter_equipment()
        return PlayerCharacter(
            id=self.generate_mongo_id(),
            account_id=self.account_id,
            name=self.state["name"],
            title="the Newcomer",
            description="",
            race=self.state["race"],
            cloaked=False,
            guild="",
            sex=self.state["sex"],
            character_class=character_class,
            room_id=room_id or "",
            area_id=area_id or "",
            role="player",
            character_flags={"act": "", "comm": "", "affectedBy": ""},
            armor_class={"piercing": 100, "slashing": 100, "bashing": 100, "magic": 100},
            character_attributes=character_attributes,
            temporal_mechanics={"played": 0, "logon": 0, "pulseWait": 0, "pulseDaze": 0},
            equipped=equipped,
            prompt_format=prompt_format,
            inventory=[],
            effects=[],
            skills=self._named_entries(self.state.get("selectedSkills", [])),
            spells=self._named_entries(self.state.get("selectedSpells", [])),
            hit=100,
            max_hit=100,
            mana=100,
            max_mana=100,
            movement=100,
            max_movement=100,
            level=1,
            gold=0,
            silver=0,
            trust=0,
            invis_level=0,
            incog_level=0,
        )

    def build_payload_dict(self) -> dict | None:
        pc = self.build_player_character()
        if pc is None:
            return None
        payload = json.loads(pc.to_json())
        payload.pop("experience", None)
        payload.pop("accumulatedExperience", None)
        payload.pop("experiencePerLevel", None)
        return payload

    def _starter_equipment(self) -> dict[str, dict]:
        equipped: dict[str, dict] = {}
        banner = self._starter_item_from_constant("OBJ_VNUM_SCHOOL_BANNER", zero_cost=True)
        vest = self._starter_item_from_constant("OBJ_VNUM_SCHOOL_VEST", zero_cost=True)
        weapon = self._starter_weapon_item()
        if banner and vest and weapon:
            equipped["light"] = banner
            equipped["torso"] = vest
            equipped["wielded"] = weapon

        if not self._is_two_handed_item(weapon):
            shield = self._starter_item_from_constant("OBJ_VNUM_SCHOOL_SHIELD", zero_cost=True)
            if shield:
                equipped["shield"] = shield

        return equipped

    def _starter_weapon_item(self) -> dict | None:
        weapon_name = str((self.state or {}).get("weapon") or "").strip().lower()
        weapon_vnum = self._school_weapon_vnum(weapon_name)
        if weapon_vnum is None:
            weapon_vnum = self._well_known_object_vnum("OBJ_VNUM_SCHOOL_SWORD")
        if weapon_vnum is None:
            return None
        return self._starter_item_from_vnum(weapon_vnum)

    def _school_weapon_vnum(self, weapon_name: str) -> str | None:
        weapon_key = str(weapon_name or "").strip().lower()
        if not weapon_key:
            return None

        fallback_constants = {
            "axe": "OBJ_VNUM_SCHOOL_AXE",
            "dagger": "OBJ_VNUM_SCHOOL_DAGGER",
            "flail": "OBJ_VNUM_SCHOOL_FLAIL",
            "mace": "OBJ_VNUM_SCHOOL_MACE",
            "polearm": "OBJ_VNUM_SCHOOL_POLEARM",
            "spear": "OBJ_VNUM_SCHOOL_SPEAR",
            "staff": "OBJ_VNUM_SCHOOL_STAFF",
            "sword": "OBJ_VNUM_SCHOOL_SWORD",
            "whip": "OBJ_VNUM_SCHOOL_WHIP",
        }

        weapon_meta = self.weapons.get(weapon_key, {})
        if isinstance(weapon_meta, dict):
            vnum_value = weapon_meta.get("vnum")
            resolved = self._resolve_object_vnum_value(vnum_value)
            if resolved is not None:
                return resolved

        return self._well_known_object_vnum(fallback_constants.get(weapon_key, ""))

    def _starter_item_from_constant(self, constant_name: str, zero_cost: bool = False) -> dict | None:
        vnum = self._well_known_object_vnum(constant_name)
        if vnum is None:
            return None
        return self._starter_item_from_vnum(vnum, zero_cost=zero_cost)

    def _starter_item_from_vnum(self, vnum: str | int, zero_cost: bool = False) -> dict | None:
        item = self.item_lookup.get(str(vnum).strip())
        if not isinstance(item, dict):
            return None

        payload = {
            "id": self.generate_mongo_id(),
            "area_id": item.get("areaId", item.get("area_id", "")),
            "vnum": str(item.get("vnum", "")),
            "name": item.get("name", ""),
            "short_description": item.get("shortDescription", item.get("short_description", "")),
            "long_description": item.get("longDescription", item.get("long_description", "")),
            "material": item.get("material", ""),
            "item_type": item.get("itemType", item.get("item_type", "")),
            "extra_flags": item.get("extraFlags", item.get("extra_flags", "")),
            "wear_flags": item.get("wearFlags", item.get("wear_flags", "")),
            "value0": str(item.get("value0", "")),
            "value1": str(item.get("value1", "")),
            "value2": str(item.get("value2", "")),
            "value3": str(item.get("value3", "")),
            "value4": str(item.get("value4", "")),
            "condition": str(item.get("condition", "")),
            "level": int(item.get("level", 0) or 0),
            "weight": int(item.get("weight", 0) or 0),
            "cost": 0 if zero_cost else int(item.get("cost", 0) or 0),
            "affect_data": list(item.get("affectData", item.get("affect_data", [])) or []),
            "extra_descr": list(item.get("extraDescr", item.get("extra_descr", [])) or []),
            "contains": [],
        }
        return payload

    def _is_two_handed_item(self, item: dict | None) -> bool:
        if not isinstance(item, dict):
            return False

        raw_flags = str(item.get("value4", "")).strip()
        if not raw_flags or raw_flags == "0":
            return False

        two_handed_flag = self._enum_value("weaponType", "WEAPON_TWO_HANDS")
        if raw_flags.isdigit() and two_handed_flag is not None:
            return (int(raw_flags) & two_handed_flag) != 0

        flag_letter = self._flag_letter_for_value(two_handed_flag)
        return bool(flag_letter and flag_letter in raw_flags)

    def _resolve_object_vnum_value(self, value: Any) -> str | None:
        if isinstance(value, (int, float)):
            return str(int(value))
        if not isinstance(value, str):
            return None

        normalized = value.strip()
        if not normalized:
            return None
        if normalized.isdigit():
            return normalized
        if normalized.startswith("OBJ_VNUM_"):
            return self._well_known_object_vnum(normalized)
        return None

    def _well_known_object_vnum(self, name: str) -> str | None:
        enums = self.game_data.get("enums", {}) if isinstance(self.game_data, dict) else {}
        well_known = enums.get("wellKnownObjectVnums", {}) if isinstance(enums, dict) else {}
        value = well_known.get(name)
        if isinstance(value, (int, float)):
            return str(int(value))
        if isinstance(value, str) and value.strip().isdigit():
            return value.strip()
        return None

    def _enum_value(self, enum_name: str, key: str) -> int | None:
        enums = self.game_data.get("enums", {}) if isinstance(self.game_data, dict) else {}
        enum_map = enums.get(enum_name, {}) if isinstance(enums, dict) else {}
        value = enum_map.get(key) if isinstance(enum_map, dict) else None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        return None

    def _flag_letter_for_value(self, value: int | None) -> str | None:
        if value is None:
            return None
        enums = self.game_data.get("enums", {}) if isinstance(self.game_data, dict) else {}
        flag_letters = enums.get("flagLetters", {}) if isinstance(enums, dict) else {}
        for letter, letter_value in flag_letters.items():
            if isinstance(letter_value, (int, float)) and int(letter_value) == value:
                return str(letter)
            if isinstance(letter_value, str) and letter_value.strip().isdigit() and int(letter_value.strip()) == value:
                return str(letter)
        return None

    @staticmethod
    def _non_blank_value(*values: Any) -> Any:
        for value in values:
            if isinstance(value, str):
                if value.strip():
                    return value
                continue
            if value is not None:
                return value
        return ""

    @staticmethod
    def _presented_class_name(class_meta: dict, fallback_name: str) -> str:
        raw_name = class_meta.get("name") if isinstance(class_meta, dict) else None
        if isinstance(raw_name, str) and raw_name.strip():
            return raw_name.strip()
        return str(fallback_name or "").strip().title()

    def _named_entries(self, names: list[str] | None) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        for name in names or []:
            normalized = str(name or "").strip()
            if normalized and normalized == "recall":
                entries.append({"name": normalized, "level": 50})
            elif normalized and normalized in self.ROM_WEAPONS:
                entries.append({"name": normalized, "level": 40})
            else:
                entries.append({"name": normalized, "level": 1})
        return entries

    def _creation_points_lines(self) -> list[str]:
        return [
            f"Creation points: {self.state.get('points', 0)}",
            f"Experience per level: {self.state.get('expPerLevel', 1000)}",
        ]

    def _add_choice(self, value: str) -> list[str]:
        group = self._resolve_option("groups", value)
        if group:
            if group.lower() in {g.lower() for g in self.state["selectedGroups"]}:
                return ["You already know that group!"]
            rating = self._group_rating(group)
            if rating < 1:
                return ["That group is not available."]
            if self.state["pointsChosen"] + rating > 300:
                return ["You cannot take more than 300 creation points."]
            self.state["selectedGroups"].append(group)
            self.state["points"] += rating
            self.state["pointsChosen"] += rating
            self._sync_selected_skills()
            self._refresh_exp()
            return [f"{group} group added"] + self._creation_points_lines()

        skill = self._resolve_skill_choice(value)
        if skill:
            known_names = {s.lower() for s in self.state.get("selectedSkills", [])}
            known_names |= {s.lower() for s in self.state.get("selectedSpells", [])}
            if skill.lower() in known_names:
                return ["You already know that skill!"]
            rating = self._skill_rating(skill)
            if rating < 1:
                return ["That skill is not available."]
            if self.state["pointsChosen"] + rating > 300:
                return ["You cannot take more than 300 creation points."]
            self.state.setdefault("standaloneSkills", []).append(skill)
            self.state["points"] += rating
            self.state["pointsChosen"] += rating
            self._sync_selected_skills()
            self._refresh_exp()
            return [f"{skill} skill added"] + self._creation_points_lines()

        return ["No skills or groups by that name..."]

    def _drop_choice(self, value: str) -> list[str]:
        group = self._resolve_option("groups", value)
        if group and group in self.state["selectedGroups"]:
            if group in self.state["lockedGroups"]:
                return [f"Cannot drop required group '{group}'."]
            rating = self._group_rating(group)
            self.state["selectedGroups"].remove(group)
            self.state["points"] -= rating
            self.state["pointsChosen"] -= rating
            self._sync_selected_skills()
            self._refresh_exp()
            return ["Group dropped."] + self._creation_points_lines()

        skill = self._resolve_skill_choice(value)
        if skill and skill in self.state.get("standaloneSkills", []):
            rating = self._skill_rating(skill)
            self.state["standaloneSkills"].remove(skill)
            self.state["points"] -= rating
            self.state["pointsChosen"] -= rating
            self._sync_selected_skills()
            self._refresh_exp()
            return ["Skill dropped."] + self._creation_points_lines()

        return ["You haven't bought any such skill or group."]

    def _list_group_cost_lines(self) -> list[str]:
        lines: list[str] = []
        groups: list[tuple[str, int]] = []
        skills: list[tuple[str, int]] = []
        class_key = str(self.state.get("characterClass", "")).strip().lower() if self.state else ""
        learned_groups = set(self._chosen_groups())
        learned_skills = set(self._learned_skill_names())
        lines.append("The following skills and groups are available to your chacter:")
        lines.append("(this list may be seen again by typing list)")

        for group in self._available_groups(class_key):
            group_name = str(group.get("name", "")).strip()
            if not group_name:
                continue
            if group_name in learned_groups:
                continue
            rating = int(group.get("rating", -1)) if isinstance(group.get("rating"), (int, float)) else -1
            if rating > 0:
                groups.append((group_name, rating))

        for skill in self._available_skills(class_key):
            skill_name = str(skill.get("name", "")).strip()
            if not skill_name:
                continue
            if skill_name in learned_skills:
                continue
            rating = int(skill.get("rating", -1)) if isinstance(skill.get("rating"), (int, float)) else -1
            if rating > 0:
                skills.append((skill_name, rating))

        lines.append("")
        lines.extend(self._format_cost_table("group", groups))
        lines.append("")
        lines.extend(self._format_cost_table("skill", skills))
        return lines

    def _selected_groups_lines(self) -> list[str]:
        lines: list[str] = []
        chosen_groups = self._chosen_groups()
        groups = sorted((name, self._group_rating(name)) for name in chosen_groups)
        groups = [(n, cp) for n, cp in groups if cp > 0]
        chosen_skills = list(self.state.get("standaloneSkills", []))
        skills = sorted((name, self._skill_rating(name)) for name in chosen_skills)
        skills = [(n, cp) for n, cp in skills if cp > 0]

        lines.extend(self._format_cost_table("group", groups))
        lines.append("")
        lines.extend(self._format_cost_table("skill", skills))
        return lines

    def _chosen_groups(self) -> list[str]:
        if not self.state:
            return []
        return [
            name for name in self.state.get("selectedGroups", [])
            if name not in self.state.get("lockedGroups", [])
        ]

    def _learned_skill_names(self) -> list[str]:
        if not self.state:
            return []
        names: set[str] = set(self.state.get("standaloneSkills", []))
        for group_name in self._chosen_groups():
            group = self.groups.get(group_name, {})
            if not isinstance(group, dict):
                continue
            for skill_name in group.get("skills", []):
                if isinstance(skill_name, str) and skill_name.strip():
                    names.add(skill_name.strip())
        return sorted(names, key=str.lower)

    def _info_lines(self, target: str) -> list[str]:
        target_low = target.strip().lower()
        if target_low == "all":
            all_groups = sorted(str(group_name) for group_name in self.groups.keys())
            return self._format_name_table(all_groups)

        group = self._resolve_option("groups", target)
        if group:
            gmeta = self.groups.get(group, {})
            members: list[str] = []
            if isinstance(gmeta, dict):
                members.extend([str(s).strip() for s in gmeta.get("skills", []) if isinstance(s, str) and s.strip()])
                members.extend([str(s).strip() for s in gmeta.get("spells", []) if isinstance(s, str) and s.strip()])
            if members:
                names = sorted(dict.fromkeys(members), key=str.lower)
                return [f"{group}:"] + self._format_name_table(names)
            return [f"{group}: (no members listed)"]

        skill = self._resolve_skill_choice(target)
        if skill:
            rating = self._skill_rating(skill)
            return [f"{skill}: cost {rating if rating > 0 else 'n/a'}"]

        return ["No group or skill by that name."]

    def _weapon_choice_prompt_lines(self) -> list[str]:
        learned = {s.lower() for s in self.state.get("selectedSkills", [])}
        weapon_choices = sorted(str(w) for w in self.weapons.keys() if str(w).lower() in learned)
        if not weapon_choices:
            weapon_choices = sorted(str(w) for w in self.weapons.keys()) or sorted(self.ROM_WEAPONS)
        return [
            "Please pick a weapon from the following choices:",
            " ".join(weapon_choices),
            "Your choice? ",
        ]

    @staticmethod
    def _format_cost_table(kind: str, rows: list[tuple[str, int]]) -> list[str]:
        lines = [f"{kind:<18} {'cp':<5} {kind:<18} {'cp':<5} {kind:<18} {'cp':<5}"]
        if not rows:
            lines.append("(none)")
            return lines
        chunk: list[tuple[str, int]] = []
        for row in rows:
            chunk.append(row)
            if len(chunk) == 3:
                lines.append(" ".join(f"{name:<18} {cp:<5}" for name, cp in chunk))
                chunk = []
        if chunk:
            lines.append(" ".join(f"{name:<18} {cp:<5}" for name, cp in chunk))
        return lines

    @staticmethod
    def _format_name_table(rows: list[str]) -> list[str]:
        if not rows:
            return ["(none)"]
        lines: list[str] = []
        chunk: list[str] = []
        for name in rows:
            chunk.append(name)
            if len(chunk) == 3:
                lines.append(" ".join(f"{v:<20}" for v in chunk))
                chunk = []
        if chunk:
            lines.append(" ".join(f"{v:<20}" for v in chunk))
        return lines

    def _refresh_exp(self, class_name: str | None = None) -> None:
        if not self.state:
            return
        current_class = class_name or self.state.get("characterClass")
        current_race = self.state.get("race")
        if not current_class or not current_race:
            self.state["expPerLevel"] = 1000
            self.state["trainBonus"] = 0
            return
        self.state["expPerLevel"] = self._exp_per_level(str(current_race), str(current_class), int(self.state.get("pointsChosen", 0)))
        self.state["trainBonus"] = (40 - self.state["points"] + 1) // 2 if self.state.get("points", 0) < 40 else 0

    def _exp_per_level(self, race_name: str, class_name: str, points: int) -> int:
        race_data = self._race_data(race_name)
        class_mult = self._class_multiplier(class_name, race_data)
        if points < 40:
            return int(1000 * ((class_mult // 100) if class_mult else 1))

        expl = 1000
        inc = 500
        rem = points - 40
        while rem > 9:
            expl += inc
            rem -= 10
            if rem > 9:
                expl += inc
                inc *= 2
                rem -= 10
        expl += rem * inc // 10
        return int(expl * class_mult / 100)

    def _race_data(self, race_name) -> dict | None:
        key = str(race_name or "").strip().lower()
        return self.pc_races.get(key)

    def _class_meta(self, class_name):
        return self.class_lookup.get(str(class_name or "").strip().lower(), {})

    def _race_meta(self, race_name):
        return self.race_lookup.get(str(race_name or "").strip().lower(), {})

    def _class_multiplier(self, class_name: str, race_data: dict | None) -> int:
        if not isinstance(race_data, dict):
            return 100
        multipliers = race_data.get("class_mult", race_data.get("classMult", []))
        idx = self.CLASS_MAP.get(str(class_name or "").strip().lower(), 0)
        if isinstance(multipliers, list) and 0 <= idx < len(multipliers):
            value = multipliers[idx]
            if isinstance(value, (int, float)):
                return int(value)
        if isinstance(multipliers, dict):
            value = multipliers.get(str(class_name or "").strip().lower())
            if isinstance(value, (int, float)):
                return int(value)
        return 100

    def _class_index(self, class_name: str | None = None) -> int:
        current_class = str(class_name or (self.state or {}).get("characterClass") or "").strip().lower()
        return self.CLASS_MAP.get(current_class, 0)

    def _class_points(self, class_name: str, race_data: dict | None) -> int:
        if not isinstance(race_data, dict):
            return 0
        total = 0
        for skill_name in race_data.get("skills", []):
            if isinstance(skill_name, str) and skill_name.strip():
                rating = self._skill_rating(skill_name, class_name)
                if rating > 0:
                    total += rating
        return total

    def _race_stats(self, race_name: str):
        race_data = self._race_data(race_name)
        if isinstance(race_data, dict):
            return race_data.get("stats", [])
        return []

    def _race_max_stats(self, race_name: str):
        race_data = self._race_data(race_name)
        if isinstance(race_data, dict):
            return race_data.get("max_stats", race_data.get("maxStats", []))
        return []

    def _race_skills(self, race_name: str):
        race_data = self._race_data(race_name)
        if isinstance(race_data, dict):
            return [skill for skill in race_data.get("skills", []) if isinstance(skill, str) and skill.strip()]
        return []

    def _race_points(self, race_name: str):
        race_data = self._race_data(race_name)
        if isinstance(race_data, dict):
            points = race_data.get("points", 0)
            return int(points) if isinstance(points, (int, float)) else 0
        return 0

    def _class_stats(self, class_name: str, race_data: dict | None) -> dict[str, int]:
        stats = race_data.get("stats", []) if isinstance(race_data, dict) else []
        values = [13, 13, 13, 13, 13]
        for idx, stat in enumerate(stats[:5]):
            if isinstance(stat, (int, float)):
                values[idx] = int(stat)
        return {"str": values[0], "int": values[1], "wis": values[2], "dex": values[3], "con": values[4]}

    def _class_max_stats(self, class_name: str, race_data: dict | None) -> dict[str, int]:
        stats = []
        if isinstance(race_data, dict):
            stats = race_data.get("max_stats", race_data.get("maxStats", []))
        values = [25, 25, 25, 25, 25]
        for idx, stat in enumerate(stats[:5]):
            if isinstance(stat, (int, float)):
                values[idx] = int(stat)
        return {"str": values[0], "int": values[1], "wis": values[2], "dex": values[3], "con": values[4]}

    def _build_available_choices(self, class_name: str):
        class_key = str(class_name or "").strip().lower()
        available_groups = self._available_groups(class_key)
        available_skills = self._available_skills(class_key)
        available_choices = available_groups + available_skills
        return available_choices

    def _available_groups(self, class_key: str):
        available_choices: list[dict] = []
        for group_name, group in self.groups.items():
            if not isinstance(group, dict):
                continue
            rating = self._group_rating(group_name, class_key)
            if rating > 0:
                available_choices.append({"name": group_name, **group, "rating": rating})
        return available_choices

    def _available_skills(self, class_key: str):
        available_choices: list[dict] = []
        for skill in self.skills:
            skill_name = str(skill.get("name", "")).strip()
            if skill_name.lower() == "reserved":
                continue
            if self._is_group_in_selected_groups(skill_name):
                continue
            rating = self._skill_rating(skill_name, class_key)
            if rating > 0:
                available_choices.append({"name": skill_name, "rating": rating})
        return available_choices

    def _is_group_in_selected_groups(self, skill_name: str) -> bool:
        if not self.state:
            return False
        normalized = str(skill_name or "").strip().lower()
        for group_name in self.state.get("selectedGroups", []):
            skills = self.groups.get(group_name, {}).get("skills", [])
            for group_skill in skills:
                if isinstance(group_skill, str) and group_skill.strip().lower() == normalized:
                    return True
        return False

    def _resolve_option(self, option_type: str, value: str) -> str | None:
        normalized = str(value or "").strip().lower()
        if not normalized:
            return None
        if option_type == "races":
            for race in self.races:
                if not isinstance(race, dict):
                    continue
                name = str(race.get("name", "")).strip()
                if name.lower() == normalized:
                    return name
            for race_name, race_data in self.pc_races.items():
                who_name = str((race_data or {}).get("who_name", race_name)).strip()
                if who_name.lower() == normalized or str(race_name).strip().lower() == normalized:
                    return str(race_name)
            return None
        if option_type == "classes":
            for character_class in self.classes:
                if not isinstance(character_class, dict):
                    continue
                name = str(character_class.get("name", "")).strip()
                if name.lower() == normalized:
                    return name
            return None
        if option_type == "groups":
            for group_name in self.groups.keys():
                if str(group_name).strip().lower() == normalized:
                    return str(group_name)
            return None
        if option_type == "weapons":
            for weapon_name in self.weapons.keys():
                if str(weapon_name).strip().lower() == normalized:
                    return str(weapon_name)
            for weapon_name in self.ROM_WEAPONS:
                if weapon_name.lower() == normalized:
                    return weapon_name
            return None
        return None

    def _option_lines(self, option_type: str) -> list[str]:
        if option_type == "races":
            options = [
                str((race_data or {}).get("who_name", race_name)).strip()
                for race_name, race_data in self.pc_races.items()
            ] or [str(race.get("name", "")).strip() for race in self.races if isinstance(race, dict)]
        elif option_type == "classes":
            options = [str(character_class.get("name", "")).strip() for character_class in self.classes if isinstance(character_class, dict)]
        elif option_type == "groups":
            options = [str(group_name).strip() for group_name in self.groups.keys()]
        elif option_type == "weapons":
            options = [str(weapon_name).strip() for weapon_name in self.weapons.keys()] or sorted(self.ROM_WEAPONS)
        else:
            options = []
        options = [option for option in options if option]
        if not options:
            return [f"No {option_type} list available from API."]
        return [f"Available {option_type}: {', '.join(options)}"]

    def _group_rating(self, group_name: str, class_name: str | None = None) -> int:
        class_idx = self._class_index(class_name)
        group = self.groups.get(group_name, {})
        ratings = group.get("rating", []) if isinstance(group, dict) else []
        if isinstance(ratings, list) and 0 <= class_idx < len(ratings):
            value = ratings[class_idx]
            return int(value) if isinstance(value, (int, float)) else -1
        return -1

    def _skill_rating(self, skill_name: str, class_name: str | None = None) -> int:
        class_key = str(class_name or (self.state or {}).get("characterClass") or "").strip().lower()
        if not class_key:
            return -1
        skill_data = self.skill_lookup.get(str(skill_name or "").strip().lower())
        if not isinstance(skill_data, dict):
            spell_data = self.spell_lookup.get(str(skill_name or "").strip().lower())
            skill_data = spell_data if isinstance(spell_data, dict) else {}
        rating_by_class = skill_data.get("ratingByClass", {})
        if isinstance(rating_by_class, dict):
            value = rating_by_class.get(class_key)
            if isinstance(value, (int, float)):
                return int(value)
        ratings = skill_data.get("rating", [])
        class_idx = self._class_index(class_key)
        if isinstance(ratings, list) and 0 <= class_idx < len(ratings):
            value = ratings[class_idx]
            if isinstance(value, (int, float)):
                return int(value)
        return -1

    def _get_groups_by_class(self, class_name: str) -> list[dict]:
        class_key = str(class_name or "").strip().lower()
        return self._available_groups(class_key)

    def _get_listable_skills_by_class(self, class_name: str) -> list[str]:
        class_key = str(class_name or "").strip().lower()
        return [
            str(skill.get("name", "")).strip()
            for skill in self._available_skills(class_key)
            if isinstance(skill, dict) and str(skill.get("name", "")).strip()
        ]

    def _resolve_skill_choice(self, value: str) -> str | None:
        class_name = str((self.state or {}).get("characterClass") or "").strip().lower()
        normalized = str(value or "").strip().lower()
        if not class_name or not normalized:
            return None
        for skill_name in self._get_listable_skills_by_class(class_name):
            if skill_name.lower() == normalized:
                return skill_name
        return None

    def _default_base_groups(self) -> list[str]:
        if not self.state:
            return []
        groups: list[str] = []
        if "rom basics" in self.groups:
            groups.append("rom basics")
        character_class = str(self.state.get("characterClass") or "").strip().lower()
        base_group = f"{character_class} basics"
        if base_group in self.groups and base_group not in groups:
            groups.append(base_group)
        return groups

    def _apply_default_group(self) -> None:
        if not self.state:
            return
        character_class = str(self.state.get("characterClass") or "").strip().lower()
        default_group = f"{character_class} default"
        if default_group not in self.groups or default_group in self.state["selectedGroups"]:
            return
        rating = self._group_rating(default_group)
        self.state["selectedGroups"].append(default_group)
        if rating > 0:
            self.state["points"] += rating
            self.state["pointsChosen"] += rating

    def _sync_selected_skills(self) -> None:
        if not self.state:
            return
        selected_skills: set[str] = set()
        selected_spells: set[str] = set()

        for skill_name in self.state.get("raceSkills", []):
            normalized = str(skill_name).strip().lower()
            if not normalized:
                continue
            if self._is_explicit_spell(normalized):
                selected_spells.add(str(skill_name).strip())
            else:
                selected_skills.add(str(skill_name).strip())

        for group_name in self.state.get("selectedGroups", []):
            group = self.groups.get(group_name, {})
            if not isinstance(group, dict):
                continue
            for skill_name in group.get("skills", []):
                if isinstance(skill_name, str) and skill_name.strip():
                    selected_skills.add(skill_name.strip())
            for spell_name in group.get("spells", []):
                if isinstance(spell_name, str) and spell_name.strip():
                    selected_spells.add(spell_name.strip())

        for skill_name in self.state.get("standaloneSkills", []):
            normalized = str(skill_name).strip().lower()
            if not normalized:
                continue
            if self._is_explicit_spell(normalized):
                selected_spells.add(str(skill_name).strip())
            else:
                selected_skills.add(str(skill_name).strip())

        self.state["selectedSkills"] = sorted(selected_skills, key=str.lower)
        self.state["selectedSpells"] = sorted(selected_spells, key=str.lower)

    def _is_explicit_spell(self, name: str) -> bool:
        normalized = str(name or "").strip().lower()
        if not normalized:
            return False
        skill_entry = self.skill_lookup.get(normalized)
        if isinstance(skill_entry, dict):
            return str(skill_entry.get("kind", "")).strip().lower() == "spell"
        spell_entry = self.spell_lookup.get(normalized)
        if isinstance(spell_entry, dict):
            return str(spell_entry.get("kind", "spell")).strip().lower() == "spell"
        return False

    def _resolve_temple_room(self) -> dict | None:
        return self._temple_room()

    def _temple_vnum(self) -> None:
        enums = self.game_data.get("enums", {}) if isinstance(self.game_data, dict) else {}
        well_known = enums.get("wellKnownRoomVnums", {}) if isinstance(enums, dict) else {}
        value = well_known.get("ROOM_VNUM_TEMPLE")
        if isinstance(value, (int, float)):
            self.TEMPLE_VNUM = int(value)
        if isinstance(value, str) and value.strip().isdigit():
            self.TEMPLE_VNUM = int(value.strip())

    def _temple_room(self):
        self._temple_vnum()
        for room in self.rooms:
            if isinstance(room, dict) and str(room.get("vnum")) == str(self.TEMPLE_VNUM):
                return room
        return None

    @staticmethod
    def generate_mongo_id() -> str:
        timestamp = int(time.time()).to_bytes(4, 'big')
        machine_id = random.getrandbits(24).to_bytes(3, 'big')
        process_id = random.getrandbits(16).to_bytes(2, 'big')
        counter = random.getrandbits(24).to_bytes(3, 'big')
        return (timestamp + machine_id + process_id + counter).hex()
