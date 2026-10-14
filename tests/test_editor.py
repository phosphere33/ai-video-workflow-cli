from pathlib import Path

from avwf.editor import broll_command, build_inserts, load_catalog, parse_srt, terms, write_manifest


def test_terms_supports_chinese_creator_tags():
    assert terms("\u53e3\u64ad\u5b57\u5e55\u63d0\u5347\u5b8c\u64ad\u7387") == ("\u53e3\u64ad\u5b57\u5e55\u63d0\u5347\u5b8c\u64ad\u7387",)


def test_chinese_catalog_tags_match_inside_a_caption(tmp_path: Path):
    srt = tmp_path / "talk.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\n\u53e3\u64ad\u5b57\u5e55\u63d0\u5347\u5b8c\u64ad\u7387\n", encoding="utf-8")
    catalog = tmp_path / "broll.csv"
    catalog.write_text("path,tags,rights_note,source_url\nasset.mp4,\u53e3\u64ad|\u5b57\u5e55|\u5b8c\u64ad\u7387,owned,https://example.com/a\n", encoding="utf-8")
    insert = build_inserts(parse_srt(srt), load_catalog(catalog))[0]
    assert insert.match_terms == ("\u53e3\u64ad", "\u5b57\u5e55", "\u5b8c\u64ad\u7387")


def test_parse_srt_and_match_catalog(tmp_path: Path):
    srt = tmp_path / "talk.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nEditing rework is too slow.\n\n2\n00:00:02,000 --> 00:00:04,000\nCaptions can improve completion.\n", encoding="utf-8")
    catalog = tmp_path / "broll.csv"
    catalog.write_text("path,tags,rights_note,source_url\nassets/timeline.mp4,editing|rework,own footage,https://example.com/license\n", encoding="utf-8")
    inserts = build_inserts(parse_srt(srt), load_catalog(catalog))
    assert inserts[0].asset == "assets/timeline.mp4"
    assert inserts[0].match_terms == ("editing", "rework")
    assert inserts[1].asset is None


def test_write_manifest_includes_editorial_checks(tmp_path: Path):
    video = tmp_path / "talk.mp4"
    video.write_bytes(b"sample video bytes")
    srt = tmp_path / "talk.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")
    output = tmp_path / "review.json"
    write_manifest(video, srt, build_inserts(parse_srt(srt), []), output)
    assert "Verify every caption" in output.read_text(encoding="utf-8")


def test_broll_command_uses_only_existing_assets(tmp_path: Path):
    video = tmp_path / "talk.mp4"
    asset = tmp_path / "cutaway.mp4"
    video.write_bytes(b"video")
    asset.write_bytes(b"broll")
    srt = tmp_path / "talk.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nEditing rework\n", encoding="utf-8")
    catalog = tmp_path / "broll.csv"
    catalog.write_text(f"path,tags,rights_note,source_url\n{asset},editing|rework,owned,https://example.com/a\n", encoding="utf-8")
    command = broll_command(video, build_inserts(parse_srt(srt), load_catalog(catalog)), tmp_path / "rough.mp4")
    assert "-filter_complex" in command
    assert "overlay=0:0" in " ".join(command)
