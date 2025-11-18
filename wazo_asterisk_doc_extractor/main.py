# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import argparse
import json
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

tag_to_quote = [
    "emphasis",
    "filename",
    "literal",
    "replaceable",
    "warning",
]


def trim_spaces(s: str) -> str:
    # Turn all kind of white spaces to a single one
    return " ".join(s.split())


def reformat_block(string: str) -> str:
    # Replace some tags by quotes and remove all other tags
    for tag in tag_to_quote:
        string = string.replace(f"<{tag}>", '"')
        string = string.replace(f"</{tag}>", '"')
    elem = ElementTree.fromstring(string)
    string = ElementTree.tostring(elem, encoding="utf-8", method="text").decode("utf-8")
    return trim_spaces(string)


def extract_para(elem: Element) -> str:
    parts = [
        reformat_block(ElementTree.tostring(para, encoding="utf-8").decode("utf-8"))
        for para in elem.findall("para")
    ]
    return "\n".join(parts)


def extract_node(elem: Element) -> str:
    notes = [extract_para(note) for note in elem.findall("note")]
    return "\n".join(notes)


def extract_choices(elem: Element) -> dict[str, str]:
    return {
        enum.attrib["name"]: extract_para(enum) if enum.text else ""
        for enum in elem.findall("./*enum")
    }


def extract_pjsip_option(elem: Element) -> dict[str, str | None | dict]:
    synopsis, description, note = "", "", ""
    choices = {}

    for e in elem:
        if e.tag == "synopsis" and e.text is not None:
            synopsis = trim_spaces(e.text)
        if e.tag == "description":
            description = extract_para(e)
            note = extract_node(e)
            choices = extract_choices(e)

    return {
        "name": elem.attrib["name"],
        "default": elem.attrib.get("default"),
        "synopsis": synopsis,
        "description": description,
        "note": note,
        "choices": choices,
    }


def extract_pjsip_doc_section(elem: Element) -> dict[str, dict[str, str | None | dict]]:
    return {
        option.attrib["name"]: extract_pjsip_option(option)
        for option in elem
        if "name" in option.attrib
    }


def extract_pjsip_doc(
    root: Element,
) -> dict[str, dict[str, dict[str, str | None | dict]]]:
    sections = root.findall(".//*[@name='res_pjsip']/configFile/")
    return {
        section.attrib["name"]: extract_pjsip_doc_section(section)
        for section in sections
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    filename = args.file

    root = ElementTree.parse(filename).getroot()
    doc = extract_pjsip_doc(root)
    print(json.dumps(doc))
