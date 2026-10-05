import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from deck import courtkit as K
from deck import frames as F
from inkkit import geom as G


def _c2_error(geometry):
    return geometry.symmetric_difference(K.rot180(geometry)).area


def test_rot180_and_c2_cover_regions_and_parts():
    region = K.box(188, 302, 271, 421)
    rotated = K.rot180(region)
    assert rotated.bounds == (479.0, 629.0, 562.0, 748.0)
    assert _c2_error(K.c2(region)) == 0
    assert np.array_equal(K.rot180((1, 2), cx=10, cy=10), np.array([19.0, 18.0]))

    part = K.Part(region, K.fill(region, K.RED), K.outline(region))
    whole = K.c2(part)
    assert whole.shape.symmetric_difference(K.rot180(whole.shape)).area == 0
    assert len(whole.fills.marks) == 2
    assert len(whole.lines.marks) == 2


def test_s_curve_is_c2_and_seam_half_is_accepted_by_frames():
    curve = K.s_curve([(115, 600), (220, 615), (305, 573)], n=20)
    rotated_back = np.column_stack((2 * K.AX - curve[::-1, 0], 2 * F.T.CY - curve[::-1, 1]))
    np.testing.assert_allclose(curve, rotated_back, atol=1e-9)

    half = K.seam_half(curve)
    assert tuple(half[-1]) == (K.AX, F.T.CY)
    full = F.seam_points(half, extend=False)
    np.testing.assert_allclose(full, curve, atol=5.1e-5, rtol=0)


def test_rank_none_scene_draws_below_old_band_without_band_clip_or_heal():
    region = K.box(210, 530, 300, 570)
    scene = K.Scene(rank=None).add(
        "robe", K.Part(region, K.fill(region, K.RED), K.outline(region))
    )
    assert K.band_guard(scene, "K") is scene
    with patch.object(F, "court_clip_d", side_effect=AssertionError("band clip used")):
        composed = scene.compose()

    assert not any(mark.role == "_band" for mark in composed.marks)
    bounds = [G.to_shape(mark.d).bounds for mark in composed.marks if mark.d]
    assert max(box[3] for box in bounds) >= 570


def test_tunic_clear_below_can_extend_pattern_past_old_band_limit():
    regions = []

    def capture(region, *_args, **_kwargs):
        regions.append(region)
        return K.C.Frag()

    with patch.object(K, "pattern", side_effect=capture):
        K.tunic(pattern_kind="hatch", clear_below=535)
        K.tunic(pattern_kind="hatch", clear_below=None)
    assert K.R(regions[0]).bounds[3] == 535
    assert K.R(regions[1]).bounds[3] > K.R(regions[0]).bounds[3]


def test_sceptre_visible_to_can_extend_segment_detail_past_old_band_limit():
    with patch.object(K, "clip_in", wraps=K.clip_in) as clipping:
        K.sceptre(K.SceptreSpec(visible_to=545))
    assert clipping.call_count == 1
    zone = clipping.call_args.args[1]
    assert zone.bounds[3] == 545 - 4.5 - K.MEDIUM

    with patch.object(K, "clip_in", wraps=K.clip_in) as clipping:
        K.sceptre(K.SceptreSpec(visible_to=None))
    assert clipping.call_count == 0


def test_zoom_crop_rerenders_exact_vector_region(tmp_path):
    svg = tmp_path / "crop.svg"
    out = tmp_path / "crop.png"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 10">'
        '<rect x="4" y="2" width="4" height="3" fill="#ff0000"/>'
        "</svg>",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "tools/zoom.py", str(svg), "4", "2", "4", "3", "2", str(out)],
        check=True,
    )

    with Image.open(out) as image:
        assert image.size == (8, 6)
        assert image.getpixel((4, 3))[:3] == (255, 0, 0)


def test_zoom_tiles_cover_svg_and_write_card_coordinate_index(tmp_path):
    svg = tmp_path / "tiles.svg"
    outdir = tmp_path / "tiles"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 10">'
        '<rect x="0" y="0" width="20" height="10" fill="#15242b"/>'
        "</svg>",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, "tools/zoom.py", str(svg), "--tiles", str(outdir),
         "--tile", "6", "--overlap", "2", "--zoom", "2"],
        check=True,
    )

    index = json.loads((outdir / "tiles.json").read_text(encoding="utf-8"))
    assert index["viewBox"] == [0.0, 0.0, 20.0, 10.0]
    assert index["region"] == {"x": 0.0, "y": 0.0, "width": 20.0, "height": 10.0}
    assert len(index["tiles"]) == 10
    tiles = index["tiles"]
    assert tiles[0]["x"] == 0 and tiles[0]["y"] == 0
    assert tiles[-1]["x"] == 14 and tiles[-1]["y"] == 4
    first_row = [tile for tile in tiles if tile["row"] == 1]
    assert all(left["x"] + left["width"] >= right["x"] + 2
               for left, right in zip(first_row, first_row[1:]))
    assert all((outdir / tile["file"]).is_file() for tile in tiles)
    assert all(tile["pixels"] == {
        "width": round(tile["width"] * 2),
        "height": round(tile["height"] * 2),
    } for tile in tiles)


def test_synthetic_continuous_court_passes_preview_qa_10a_10b_10s(tmp_path, monkeypatch):
    module = tmp_path / "synthetic_court.py"
    module.write_text(
        """
from deck import courtkit as K
DOUBLE_HEAD = "continuous"
SEAM = K.seam_half(K.s_curve([(120, 600), (220, 615), (305, 573)]))
def build():
    scene = K.Scene(rank=None)
    robe = K.c2(K.box(200, 300, 550, 750))
    scene.part("robe", K.Part(robe, K.fill(robe, K.RED), K.outline(robe)))
    accent = K.c2(K.R(K.circle((320, 450), 28)))
    scene.part("accent", K.Part(accent, K.fill(accent, K.JADE), K.outline(accent)))
    return K.layers(scene.compose())
""",
        encoding="utf-8",
    )
    from tools import preview
    from deck import qa as Q

    qa_dir = tmp_path / "qa"
    monkeypatch.setattr(Q, "QA_DIR", str(qa_dir))
    mod = preview._load_module(str(module), "KH")
    with tempfile.TemporaryDirectory(dir=tmp_path) as sandbox:
        limestone = preview._compose(mod, "KH", "limestone", sandbox)
        white = preview._compose(mod, "KH", "white", sandbox)
        qa = Q.check_piece((limestone, white))
    assert qa["10a"]["ok"] is True, qa["10a"]
    assert qa["10b"]["ok"] is True, qa["10b"]
    assert qa["10s"]["ok"] is True, qa["10s"]
