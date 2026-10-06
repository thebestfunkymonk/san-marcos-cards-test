import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from deck import tokens as T
from tools import density


def rectangle_svg(hatched=False, paper_hole=False):
    lines = "".join(
        f'<path d="M{x} 20V140" stroke="{T.INK}" stroke-width="2"/>'
        for x in range(23, 140, 7)
    ) if hatched else ""
    hole = f'<rect x="60" y="60" width="40" height="40" fill="{T.PAPER}"/>' if paper_hole else ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160">'
        f'<rect width="160" height="160" fill="{T.PAPER}"/>'
        f'<rect x="20" y="20" width="120" height="120" fill="{T.JADE}"/>'
        f"{lines}{hole}</svg>"
    )


def test_flat_rectangle_is_one_big_eroded_ink_patch():
    result = density.analyze_svg(rectangle_svg())
    patches = result.metrics["flat_patches"]
    assert len(patches) == 1
    assert patches[0]["ink"] == "jade"
    assert 11000 < patches[0]["area_px"] < 13000
    assert patches[0]["bbox"] == [25.0, 25.0, 135.0, 135.0]
    assert result.metrics["largest_flat_patch"] == patches[0]
    assert result.metrics["paper_inside_figure_patches"] == []


def test_hatching_removes_flat_patch_and_increases_even_detail():
    flat = density.analyze_svg(rectangle_svg()).metrics
    hatched = density.analyze_svg(rectangle_svg(hatched=True)).metrics
    assert hatched["flat_patches"] == []
    assert hatched["largest_flat_patch"] == {"area_px": 0.0, "bbox": None, "ink": None}
    assert hatched["score"] > flat["score"]
    assert hatched["low_detail_fraction"] < flat["low_detail_fraction"]


def test_paper_outside_figure_is_excluded_and_inside_is_informational():
    result = density.analyze_svg(rectangle_svg(paper_hole=True)).metrics
    paper = result["paper_inside_figure_patches"]
    assert len(paper) == 1
    assert paper[0]["bbox"] == [65.0, 65.0, 95.0, 95.0]
    assert paper[0]["area_px"] == 900
    assert result["largest_flat_patch"]["ink"] == "jade"
    assert all(tile["bbox"][0] >= 0 for tile in result["tiles"])


def test_metrics_and_heatmap_are_deterministic():
    first = density.analyze_svg(rectangle_svg())
    second = density.analyze_svg(rectangle_svg())
    assert first.metrics == second.metrics
    assert np.array_equal(np.asarray(first.heatmap), np.asarray(second.heatmap))


def test_deck_system_marks_do_not_count_as_figure_detail():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050">'
        f'<g id="paper"><rect width="750" height="1050" fill="{T.PAPER}"/></g>'
        f'<g id="jade"><g class="court-top"><rect x="300" y="300" '
        f'width="120" height="120" fill="{T.JADE}"/></g></g>'
        f'<g id="ink"><g class="frame"><rect x="145" y="60" width="450" '
        f'height="900" fill="{T.INK}"/></g></g></svg>'
    )
    result = density.analyze_svg(svg).metrics
    assert result["art_window"] == [139.0, 55.0, 611.0, 995.0]
    assert result["figure_area_px"] == 14400
    assert len(result["flat_patches"]) == 1
    assert result["largest_flat_patch"]["bbox"] == [305.0, 305.0, 415.0, 415.0]


def test_empty_figure_returns_finite_zero_metrics():
    result = density.analyze_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30"/>'
    ).metrics
    assert result["score"] == 0
    assert result["low_detail_fraction"] == 0
    assert result["tiles"] == []
    assert result["flat_patches"] == []


def test_cli_writes_json_and_heatmap_with_card_coordinates(tmp_path):
    svg = tmp_path / "flat.svg"
    svg.write_text(rectangle_svg(), encoding="utf-8")
    output = tmp_path / "out"
    script = Path(__file__).resolve().parents[2] / "tools" / "density.py"
    run = subprocess.run(
        [sys.executable, str(script), str(svg), "--out", str(output)],
        check=True, capture_output=True, text=True,
    )
    metrics = json.loads((output / "flat-current.json").read_text())
    assert "score" in run.stdout
    assert metrics["largest_flat_patch"]["ink"] == "jade"
    with Image.open(output / "flat-current-heatmap.png") as image:
        assert image.size == (160, 160)


def test_id_resolution_and_ref_use_cards_stem(monkeypatch):
    assert density.resolve_svg("qh") == density.ROOT / "cards" / "QH.svg"
    calls = []

    def show(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, rectangle_svg(), "")

    monkeypatch.setattr(density.subprocess, "run", show)
    assert density.read_reference(Path("/tmp/preview/QH.svg"), "b4e26982") == rectangle_svg()
    assert calls == [["git", "-C", str(density.ROOT), "show", "b4e26982:cards/QH.svg"]]


def test_compare_cli_writes_both_reports_and_heatmaps(tmp_path, monkeypatch, capsys):
    svg = tmp_path / "QH.svg"
    svg.write_text(rectangle_svg(hatched=True), encoding="utf-8")
    monkeypatch.setattr(density, "read_reference", lambda *_: rectangle_svg())
    out = tmp_path / "comparison"
    assert density.main([str(svg), "--ref", "baseline", "--out", str(out)]) == 0
    stdout = capsys.readouterr().out
    assert "ref (baseline)" in stdout and "current" in stdout
    assert sorted(path.name for path in out.iterdir()) == [
        "QH-current-heatmap.png", "QH-current.json", "QH-ref-heatmap.png", "QH-ref.json",
    ]
    current = json.loads((out / "QH-current.json").read_text())
    reference = json.loads((out / "QH-ref.json").read_text())
    assert reference["revision"] == "baseline"
    assert current["score"] > reference["score"]
    assert current["largest_flat_patch"]["area_px"] == 0


def test_multiple_inks_rank_top_five_without_merging():
    squares = "".join(
        f'<rect x="{i * 50 + 5}" y="5" width="40" height="40" fill="{colour}"/>'
        for i, colour in enumerate([T.JADE, T.RED, T.FOIL, T.INK, T.JADE, T.RED])
    )
    result = density.analyze_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 50">'
        f"{squares}</svg>"
    ).metrics
    assert result["flat_patch_count"] == 6
    assert len(result["flat_patches"]) == 5
    assert {patch["ink"] for patch in result["flat_patches"]} == {"jade", "red", "gold", "ink"}
    assert all(patch["area_px"] == 900 for patch in result["flat_patches"])


def test_white_and_limestone_stock_have_identical_metrics():
    limestone = density.analyze_svg(rectangle_svg()).metrics
    white = density.analyze_svg(rectangle_svg().replace(T.PAPER, T.WHITE)).metrics
    assert limestone == white


def test_window_edge_is_eroded_and_bbox_uses_viewbox_origin():
    result = density.analyze_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="100 200 80 80">'
        f'<rect x="100" y="200" width="80" height="80" fill="{T.RED}"/></svg>'
    ).metrics
    assert result["largest_flat_patch"] == {
        "area_px": 4900.0, "bbox": [105.0, 205.0, 175.0, 275.0], "ink": "red",
    }


def test_court_extraction_preserves_definitions_clips_and_transforms():
    result = density.analyze_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050">'
        '<defs><clipPath id="mask"><rect x="0" y="0" width="60" height="60"/>'
        '</clipPath></defs><g id="jade" transform="translate(300 300)">'
        f'<g class="court-top"><g clip-path="url(#mask)">'
        f'<rect width="120" height="120" fill="{T.JADE}"/></g></g></g></svg>'
    ).metrics
    assert result["figure_area_px"] == 3600
    assert result["largest_flat_patch"]["bbox"] == [305.0, 305.0, 355.0, 355.0]
