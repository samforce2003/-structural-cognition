#!/usr/bin/env python3
"""知乎自动发布脚本 —— 基于 zh_mcp_server 的 ZhuHuPoster"""
import sys, os, json, argparse

sys.path.insert(0, r"D:\projects\zh_mcp_server")
os.environ["PATH"] = r"D:\projects\zh_mcp_server;" + os.environ.get("PATH", "")

from write_zhihu import ZhuHuPoster

def publish_article(title, content, headless=True):
    poster = ZhuHuPoster(headless=headless)
    logged_in = poster.login()
    if not logged_in:
        print("ERROR: Login failed")
        poster.close()
        return False
    result = poster.post_article(title, content)
    poster.close()
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--no-headless", action="store_true")
    args = parser.parse_args()
    
    success = publish_article(args.title, args.content, headless=not args.no_headless)
    if success:
        print("PUBLISH_SUCCESS")
    else:
        print("PUBLISH_FAILED")
        sys.exit(1)
