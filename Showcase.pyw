#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Theme showcase script for VS Code screenshots.
Intentionally feature-rich code to display syntax highlighting.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, TypedDict


# ------------------------------------------------------------
# constants and config
# ------------------------------------------------------------

APP_NAME = "FSOCIETY::SHOWCASE"
BUILD = "0.9.9-preview"
ROOT = Path(__file__).resolve().parent
GLOW_RED = "#ff003c"
PURE_BLACK = "#000000"

ANSI = {
	"reset": "\x1b[0m",
	"red": "\x1b[31m",
	"green": "\x1b[32m",
	"cyan": "\x1b[36m",
	"bold": "\x1b[1m",
}


class ThemeTone(Enum):
	SHADOW = auto()
	BLOOD = auto()
	STATIC = auto()
	GLITCH = auto()


class UserProfile(TypedDict):
	name: str
	role: Literal["operator", "observer", "ghost"]
	score: int
	enabled: bool


@dataclass(slots=True)
class Panel:
	id: int
	title: str
	tone: ThemeTone
	tags: set[str] = field(default_factory=set)
	meta: dict[str, Any] = field(default_factory=dict)

	def label(self) -> str:
		prefix = f"{ANSI['bold']}{ANSI['red']}"
		suffix = ANSI["reset"]
		return f"{prefix}[{self.id:02}] {self.title:<16}{suffix}"


def tracer(func: Callable[..., Any]) -> Callable[..., Any]:
	def wrapper(*args: Any, **kwargs: Any) -> Any:
		logging.debug("CALL %s args=%s kwargs=%s", func.__name__, args, kwargs)
		return func(*args, **kwargs)

	return wrapper


@contextlib.contextmanager
def frame(name: str) -> Iterable[None]:
	border = f"+{'-' * 20}+"
	print(border)
	print(f"| {name:^18} |")
	print(border)
	try:
		yield
	finally:
		print(border)


@tracer
def parse_signal(text: str) -> dict[str, str | int] | None:
	pattern = re.compile(r"^(?P<kind>[A-Z_]+):(?P<value>\d{2,4})$")
	if match := pattern.match(text.strip()):
		return {
			"kind": match.group("kind"),
			"value": int(match.group("value")),
		}
	return None


def style_line(level: int, content: str) -> str:
	palette = [ANSI["cyan"], ANSI["green"], ANSI["red"]]
	color = palette[level % len(palette)]
	return f"{color}{content}{ANSI['reset']}"


async def fake_ping(host: str, delay: float = 0.12) -> tuple[str, bool, float]:
	started = datetime.now(tz=timezone.utc)
	await asyncio.sleep(delay)
	ok = random.random() > 0.18
	ms = (datetime.now(tz=timezone.utc) - started).total_seconds() * 1000
	return host, ok, ms


async def collect_metrics(hosts: list[str]) -> list[tuple[str, bool, float]]:
	tasks = [fake_ping(h, delay=0.06 + i * 0.02) for i, h in enumerate(hosts)]
	return await asyncio.gather(*tasks)


def render_panels(panels: list[Panel]) -> None:
	for panel in panels:
		match panel.tone:
			case ThemeTone.BLOOD:
				marker = "!!"
			case ThemeTone.SHADOW:
				marker = ".."
			case ThemeTone.STATIC:
				marker = "~~"
			case ThemeTone.GLITCH:
				marker = "//"
			case _:
				marker = "??"

		info = ", ".join(sorted(panel.tags)) or "none"
		print(f"{panel.label()}  {marker} tags=[{info}]  meta={panel.meta}")


def demo_data() -> tuple[list[Panel], list[UserProfile]]:
	panels = [
		Panel(1, "auth gateway", ThemeTone.BLOOD, {"token", "oauth"}, {"latency": 12.8}),
		Panel(2, "control bus", ThemeTone.SHADOW, {"queue", "retry"}, {"workers": 4}),
		Panel(3, "signal map", ThemeTone.GLITCH, {"heat", "nodes"}, {"segments": 42}),
		Panel(4, "archive", ThemeTone.STATIC, set(), {"readonly": True}),
	]

	users: list[UserProfile] = [
		{"name": "zero", "role": "operator", "score": 98, "enabled": True},
		{"name": "delta", "role": "observer", "score": 64, "enabled": False},
		{"name": "omega", "role": "ghost", "score": 88, "enabled": True},
	]
	return panels, users


def query_preview() -> str:
	sql = """
	SELECT u.name, u.role, p.title, p.tone
	FROM users AS u
	JOIN panels AS p ON p.id = u.score % 4 + 1
	WHERE u.enabled = 1 AND u.score >= 70
	ORDER BY u.score DESC;
	""".strip()
	return sql


async def main() -> None:
	logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

	with frame(f"{APP_NAME} {BUILD}"):
		print(style_line(2, f"root={ROOT}"))
		print(style_line(0, f"palette.red={GLOW_RED}  palette.bg={PURE_BLACK}"))

	panels, users = demo_data()
	render_panels(panels)

	enabled_users = [u for u in users if u["enabled"]]
	role_map = {u["name"]: u["role"] for u in enabled_users}
	scores = [u["score"] for u in users]
	stats = {
		"max": max(scores),
		"min": min(scores),
		"avg": round(sum(scores) / len(scores), 2),
	}

	print("\nactive roles:", role_map)
	print("stats:", stats)

	lines = [
		"ALERT:404",
		"PING:200",
		"BROKEN_line",
		"TRACE:1337",
	]
	parsed = [parse_signal(line) for line in lines]
	print("\nparsed signals:", [p for p in parsed if p is not None])

	print("\nsql preview:\n", query_preview())

	hosts = ["node-a.local", "node-b.local", "vault.internal"]
	pings = await collect_metrics(hosts)
	for host, ok, ms in pings:
		icon = "OK" if ok else "FAIL"
		print(f"{host:<16} {icon:<4} {ms:7.2f} ms")


if __name__ == "__main__":
	# This script is designed mainly for theme screenshots.
	asyncio.run(main())
