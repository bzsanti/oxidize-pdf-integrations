"""Fixtures: programmatic PDFs built with oxidize-pdf itself (no binary assets)."""

from __future__ import annotations

import pathlib

import oxidize_pdf as op
import pytest


def _write_sample_pdf(target: pathlib.Path) -> pathlib.Path:
    doc = op.Document()

    page1 = op.Page.a4()
    page1.set_font(op.Font.HELVETICA, 14.0)
    page1.text_at(50.0, 760.0, "Chapter 1: Introduction")
    page1.set_font(op.Font.HELVETICA, 12.0)
    page1.text_at(50.0, 730.0, "This is the first paragraph of the document.")
    page1.text_at(50.0, 710.0, "It contains important information about the topic.")
    doc.add_page(page1)

    page2 = op.Page.a4()
    page2.set_font(op.Font.HELVETICA, 14.0)
    page2.text_at(50.0, 760.0, "Chapter 2: Details")
    page2.set_font(op.Font.HELVETICA, 12.0)
    page2.text_at(50.0, 730.0, "More detailed information follows here.")
    page2.text_at(50.0, 710.0, "Including an additional sentence for context.")
    doc.add_page(page2)

    doc.save(str(target))
    return target


@pytest.fixture
def sample_pdf(tmp_path: pathlib.Path) -> pathlib.Path:
    return _write_sample_pdf(tmp_path / "sample.pdf")
