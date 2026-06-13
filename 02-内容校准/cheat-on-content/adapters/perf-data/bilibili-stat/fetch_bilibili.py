"""B站视频数据抓取器 — 最小可用版本。

用法:
    python fetch_bilibili.py <BV号或链接> [输出目录]

输出:
    <输出目录>/report.md  (cheat-retro 读这个文件)

依赖:
    httpx
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx

CST = timezone(timedelta(hours=8))

API_VIDEO = "https://api.bilibili.com/x/web-interface/view"
API_COMMENTS = "https://api.bilibili.com/x/v2/reply/main"
API_LIKE = "https://api.bilibili.com/x/web-interface/view/like/info"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
}


def extract_bvid(text: str) -> str:
    """从链接或纯 BV 号中提取 BV id。"""
    m = re.search(r"(BV[A-Za-z0-9]+)", text)
    if m:
        return m.group(1)
    raise ValueError(f"无法从 '{text}' 中提取 BV 号")


def fetch_video_info(bvid: str, client: httpx.Client) -> dict:
    resp = client.get(API_VIDEO, params={"bvid": bvid}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"B站 API 返回错误: {data.get('message', data)}")
    return data["data"]


def fetch_comments(oid: int, client: httpx.Client, max_pages: int = 3) -> list:
    """抓取热门评论（按热度排序）。"""
    comments = []
    for pn in range(1, max_pages + 1):
        resp = client.get(
            API_COMMENTS,
            params={"type": 1, "oid": oid, "mode": 3, "pn": pn, "ps": 20},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            break
        replies = data.get("data", {}).get("replies") or []
        for r in replies:
            comments.append({
                "user": r.get("member", {}).get("uname", ""),
                "content": r.get("content", {}).get("message", ""),
                "likes": r.get("like", 0),
                "time": datetime.fromtimestamp(
                    r.get("ctime", 0), tz=CST
                ).strftime("%Y-%m-%d %H:%M"),
            })
        if not data.get("data", {}).get("cursor", {}).get("is_end", True):
            continue
        break
    comments.sort(key=lambda x: x["likes"], reverse=True)
    return comments[:20]


def render_report(info: dict, comments: list) -> str:
    stat = info.get("stat", {})
    pub_date = datetime.fromtimestamp(info.get("pubdate", 0), tz=CST).strftime("%Y-%m-%d %H:%M")
    duration_min = info.get("duration", 0) / 60

    lines = []
    lines.append(f"# B站视频数据报告")
    lines.append("")
    lines.append(f"- **标题**: {info.get('title', '')}")
    lines.append(f"- **BV号**: {info.get('bvid', '')}")
    lines.append(f"- **AV号**: {info.get('aid', '')}")
    lines.append(f"- **发布时间**: {pub_date}")
    lines.append(f"- **时长**: {duration_min:.1f} 分钟 ({info.get('duration', 0)}s)")
    lines.append(f"- **UP主**: {info.get('owner', {}).get('name', '')}")
    lines.append(f"- **分区**: {info.get('tname', '')}")
    lines.append(f"- **描述**: {info.get('desc', '')[:300]}")
    lines.append("")
    lines.append("## 数据快照")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|---|---:|")
    lines.append(f"| 播放 | {stat.get('view', 0)} |")
    lines.append(f"| 弹幕 | {stat.get('danmaku', 0)} |")
    lines.append(f"| 点赞 | {stat.get('like', 0)} |")
    lines.append(f"| 投币 | {stat.get('coin', 0)} |")
    lines.append(f"| 收藏 | {stat.get('favorite', 0)} |")
    lines.append(f"| 转发 | {stat.get('share', 0)} |")
    lines.append(f"| 评论 | {stat.get('reply', 0)} |")
    lines.append("")

    view = stat.get("view", 0)
    if view > 0:
        like_ratio = stat.get("like", 0) / view * 100
        coin_ratio = stat.get("coin", 0) / view * 100
        fav_ratio = stat.get("favorite", 0) / view * 100
        reply_ratio = stat.get("reply", 0) / view * 100
        lines.append("## 派生比率")
        lines.append("")
        lines.append(f"| 比率 | 值 |")
        lines.append(f"|---|---:|")
        lines.append(f"| 赞播比 | {like_ratio:.2f}% |")
        lines.append(f"| 币播比 | {coin_ratio:.2f}% |")
        lines.append(f"| 收播比 | {fav_ratio:.2f}% |")
        lines.append(f"| 评播比 | {reply_ratio:.2f}% |")
        lines.append("")

    if comments:
        lines.append("## Top 评论（按热度）")
        lines.append("")
        lines.append(f"| # | 用户 | 评论 | 赞 | 时间 |")
        lines.append(f"|---:|---|---|---::|---|")
        for i, c in enumerate(comments[:20], 1):
            content = c["content"].replace("|", "\\|").replace("\n", " ")[:80]
            lines.append(f"| {i} | {c['user']} | {content} | {c['likes']} | {c['time']} |")
        lines.append("")

    lines.append("---")
    lines.append(f"*抓取时间: {datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')} CST*")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_bilibili.py <BV号或链接> [输出目录]")
        sys.exit(1)

    bvid = extract_bvid(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    print(f"正在抓取 {bvid} ...")
    with httpx.Client(headers=HEADERS) as client:
        info = fetch_video_info(bvid, client)
        aid = info.get("aid", 0)
        print(f"  标题: {info.get('title', '')}")
        print(f"  播放: {info.get('stat', {}).get('view', 0)}")
        comments = fetch_comments(aid, client)

    report = render_report(info, comments)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"报告已写入: {report_path}")


if __name__ == "__main__":
    main()
