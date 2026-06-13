"""YouTube 视频数据抓取器 — 最小可用版本。

用法:
    python fetch_youtube.py <videoId或链接> [输出目录]

需要:
    环境变量 YOUTUBE_API_KEY 或在 ~/.youtube_api_key 文件中存放 API key

输出:
    <输出目录>/report.md  (cheat-retro 读这个文件)

依赖:
    google-api-python-client
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from googleapiclient.discovery import build

CST = timezone(timedelta(hours=8))


def get_api_key() -> key_str:
    key = os.environ.get("YOUTUBE_API_KEY", "")
    if not key:
        key_file = Path.home() / ".youtube_api_key"
        if key_file.exists():
            key = key_file.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(
            "未找到 YouTube API key。\n"
            "请设置环境变量 YOUTUBE_API_KEY 或创建文件 ~/.youtube_api_key"
        )
    return key


def extract_video_id(text: str) -> str:
    """从链接或纯 videoId 中提取 YouTube video ID。"""
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    raise ValueError(f"无法从 '{text}' 中提取 YouTube video ID")


def fetch_video_info(video_id: str, youtube) -> dict:
    resp = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id,
    ).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError(f"未找到视频 {video_id}")
    return items[0]


def fetch_comments(video_id: str, youtube, max_results: int = 20) -> list:
    comments = []
    try:
        resp = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=max_results,
            textFormat="plainText",
        ).execute()
        for item in resp.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "user": snippet.get("authorDisplayName", ""),
                "content": snippet.get("textDisplay", ""),
                "likes": snippet.get("likeCount", 0),
                "time": snippet.get("publishedAt", "")[:16].replace("T", " "),
            })
    except Exception as e:
        print(f"  评论抓取失败（可能是关闭了评论）: {e}")
    comments.sort(key=lambda x: x["likes"], reverse=True)
    return comments[:20]


def parse_duration(iso_duration: str) -> int:
    """将 ISO 8601 时长 (PT1H2M3S) 转换为秒。"""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if not m:
        return 0
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def render_report(info: dict, comments: list) -> str:
    snippet = info.get("snippet", {})
    stats = info.get("statistics", {})
    content = info.get("contentDetails", {})

    pub_date = snippet.get("publishedAt", "")[:16].replace("T", " ")
    duration_sec = parse_duration(content.get("duration", "PT0S"))
    duration_min = duration_sec / 60

    view_count = int(stats.get("viewCount", 0))
    like_count = int(stats.get("likeCount", 0))
    comment_count = int(stats.get("commentCount", 0))

    lines = []
    lines.append("# YouTube 视频数据报告")
    lines.append("")
    lines.append(f"- **标题**: {snippet.get('title', '')}")
    lines.append(f"- **videoId**: {info.get('id', '')}")
    lines.append(f"- **发布时间**: {pub_date}")
    lines.append(f"- **时长**: {duration_min:.1f} 分钟 ({duration_sec}s)")
    lines.append(f"- **频道**: {snippet.get('channelTitle', '')}")
    lines.append(f"- **描述**: {snippet.get('description', '')[:300]}")
    lines.append("")
    lines.append("## 数据快照")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|---|---:|")
    lines.append(f"| 播放 | {view_count} |")
    lines.append(f"| 点赞 | {like_count} |")
    lines.append(f"| 评论 | {comment_count} |")
    lines.append("")

    if view_count > 0:
        like_ratio = like_count / view_count * 100
        comment_ratio = comment_count / view_count * 100
        lines.append("## 派生比率")
        lines.append("")
        lines.append("| 比率 | 值 |")
        lines.append("|---|---:|")
        lines.append(f"| 赞播比 | {like_ratio:.2f}% |")
        lines.append(f"| 评播比 | {comment_ratio:.2f}% |")
        lines.append("")

    if comments:
        lines.append("## Top 评论（按热度）")
        lines.append("")
        lines.append("| # | 用户 | 评论 | 赞 | 时间 |")
        lines.append("|---:|---|---|---::|---|")
        for i, c in enumerate(comments[:20], 1):
            content_text = c["content"].replace("|", "\\|").replace("\n", " ")[:80]
            lines.append(f"| {i} | {c['user']} | {content_text} | {c['likes']} | {c['time']} |")
        lines.append("")

    lines.append("---")
    lines.append(f"*抓取时间: {datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')} CST*")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_youtube.py <videoId或链接> [输出目录]")
        sys.exit(1)

    video_id = extract_video_id(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

    api_key = get_api_key()
    youtube = build("youtube", "v3", developerKey=api_key)

    print(f"正在抓取 {video_id} ...")
    info = fetch_video_info(video_id, youtube)
    print(f"  标题: {info['snippet']['title']}")
    print(f"  播放: {info['statistics'].get('viewCount', 0)}")
    comments = fetch_comments(video_id, youtube)

    report = render_report(info, comments)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"报告已写入: {report_path}")


if __name__ == "__main__":
    main()
