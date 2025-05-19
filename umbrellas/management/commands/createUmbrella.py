from django.core.management.base import BaseCommand
from umbrellas.models import Umbrellas, UmbrellaLog
import secrets
import json

class Command(BaseCommand):
    help = "傘のデータを作成する"

    def add_arguments(self, parser):
        parser.add_argument("new_umbrellas", type=int, help="作成する傘の数")
        parser.add_argument("place", type=str, choices=Umbrellas.STATUS_PRACE, help="傘の場所を選択")
        parser.add_argument("umbrella_type", type=str, choices=Umbrellas.STATUS_UMBRELLA_TYPE, help="傘の種類を選択")

    def handle(self, *args, **options):
        umbrellas_data = {}

        # 入力を取得
        new_umbrellas = options["new_umbrellas"]
        place = options["place"]
        umbrella_type = options["umbrella_type"]

        i = 1
        for _ in range(new_umbrellas):
            # ランダム文字生成
            umbrella_name = secrets.token_hex(3)
            # 傘生成
            umbrella, created = Umbrellas.objects.get_or_create(
                umbrella_name = umbrella_name,
                place = place,
                umbrella_type = umbrella_type,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ 傘を作成しました: {umbrella}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ 既に存在します: {umbrella}"))
            
            # ログに入れるための傘の名前のdict
            umbrellas_data['umbrella_name'] = umbrella_name
            umbrellas_data['place'] = place
            umbrellas_data['umbrella_type'] = umbrella_type
            umbrellas_data['borrower'] = None

            i += 1

        # ログのデータを挿入
        UmbrellaLog.objects.create(
            umbrella_log = umbrellas_data,
        )