import json
from pathlib import Path

import pytest

from avwf.planner import build_plan, split_script, write_plan


def test_split_script_keeps_all_text_and_respects_limit():
    chunks = split_script("第一句很短。第二句也很短！第三句继续。", max_chars=20)
    assert "".join(chunks).replace(" ", "") == "第一句很短。第二句也很短！第三句继续。"
    assert all(len(chunk) <= 20 for chunk in chunks)


def test_split_script_rejects_small_limit():
    with pytest.raises(ValueError, match="at least 20"):
        split_script("内容", max_chars=19)


def test_build_plan_and_write_plan(tmp_path: Path):
    script = tmp_path / "script.txt"
    script.write_text("这是一条数据说明。数据增长 20%。", encoding="utf-8")
    plan = build_plan(
        script,
        title="示例",
        aspect_ratio="9:16",
        max_chars=30,
        chars_per_second=4.0,
        local_assets=["assets/cover.mp4"],
    )
    output = tmp_path / "plan.json"
    write_plan(plan, output)
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["project"]["title"] == "示例"
    assert saved["scenes"][0]["id"] == "scene-001"
    assert saved["estimated_total_seconds"] > 0
