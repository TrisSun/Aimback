from django.core.management.base import BaseCommand

from apps.ai.embed import process_pending, sync_searchable_posts


class Command(BaseCommand):
    help = "同步可搜索帖子的向量任务并处理 pending 行。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="只跑一轮后退出（默认）。",
        )
        parser.add_argument(
            "--loop",
            action="store_true",
            help="按 interval 秒循环处理。",
        )
        parser.add_argument("--interval", type=int, default=5)
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument(
            "--skip-sync",
            action="store_true",
            help="不扫描帖子、只处理已有 pending。",
        )

    def handle(self, *args, **options):
        interval = max(1, options["interval"])
        limit = max(1, options["limit"])
        looping = options["loop"]

        def _round() -> int:
            if not options["skip_sync"]:
                synced = sync_searchable_posts()
                self.stdout.write(f"synced posts={synced}")
            done = process_pending(limit=limit)
            self.stdout.write(f"embedded={done}")
            return done

        if looping:
            import time

            self.stdout.write(f"loop interval={interval}s limit={limit}")
            while True:
                _round()
                time.sleep(interval)
        else:
            _round()
