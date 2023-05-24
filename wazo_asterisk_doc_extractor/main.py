# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import argparse
from xml.etree import ElementTree

tag_to_quote = [
    "emphasis",
    "filename",
    "literal",
    "replaceable",
    "warning",
]


def trim_spaces(s):
    # Turn all kind of white spaces to a single one
    return " ".join(s.split())


def reformat_block(s):
    # Replace some tags by quotes and remove all other tags
    for tag in tag_to_quote:
        s = s.replace(f"<{tag}>", '"')
        s = s.replace(f"</{tag}>", '"')
    elem = ElementTree.fromstring(s)
    s = ElementTree.tostring(elem, encoding="utf8", method="text").decode("utf8")
    return trim_spaces(s)


def extract_para(elem):
    parts = [
        reformat_block(ElementTree.tostring(para, encoding="utf8").decode("utf8"))
        for para in elem.findall("para")
    ]
    return "\n".join(parts)


def extract_node(elem):
    notes = [extract_para(note) for note in elem.findall("note")]
    return "\n".join(notes)


def extract_choices(elem):
    return {
        enum.attrib["name"]: extract_para(enum) if enum.text else ""
        for enum in elem.findall("./*enum")
    }


def extract_pjsip_option(elem):
    synopsis, description, note = "", "", ""
    choices = {}

    for e in elem:
        if e.tag == "synopsis":
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


def extract_pjsip_doc_section(elem):
    return {
        option.attrib["name"]: extract_pjsip_option(option)
        for option in elem
        if "name" in option.attrib
    }


def extract_pjsip_doc(root):
    sections = root.findall(".//*[@name='res_pjsip']/configFile/")
    return {
        section.attrib["name"]: extract_pjsip_doc_section(section)
        for section in sections
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    filename = args.file

    root = ElementTree.parse(filename).getroot()
    doc = extract_pjsip_doc(root)
    print(json.dumps(doc))
