from django.core.management.base import BaseCommand
from umbrellas.models import Umbrellas, UmbrellaLog
import secrets
import json

class Command(BaseCommand):
    help = "傘のデータを作成する"

    STATUS_PRACE = [
        ('Library', '図書館'),
        ('North cafeteria', '北食堂'),
        ('Central cafeteria', '中央食堂'),
        ('Engineering faculty', '工学部棟'),
        ('Agriculture faculty', '農学部棟'),
        ('Sience faculty', '理系複合棟'),
        ('Literal faculty', '文系複合棟'),
        ('Senbaru domitory', '千原寮共用棟'),
    ]

    def add_arguments(self, parser):
        parser.add_argument("new_umbrellas", type=int, help="作成する傘の数")
        parser.add_argument("place", type=str, choices=self.STATUS_PRACE, help="傘の場所を選択")

    def handle(self, *args, **options):
        umbrellas_data = {}

        # 入力を取得
        new_umbrellas = options["new_umbrellas"]
        place = options["place"]

        i = 1
        for _ in range(new_umbrellas):
            # ランダム文字生成
            umbrella_name = secrets.token_hex(3)
            # 傘生成
            umbrella, created = Umbrellas.objects.get_or_create(
                umbrella_name = umbrella_name,
                place = place,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ 傘を作成しました: {umbrella}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ 既に存在します: {umbrella}"))
            
            # ログに入れるための傘の名前のdict
            umbrellas_data['umbrella_name'] = umbrella_name
            umbrellas_data['place'] = place
            umbrellas_data['borrower'] = None

            i += 1

        # ログのデータを挿入
        UmbrellaLog.objects.create(
            umbrella_log = umbrellas_data,
        )