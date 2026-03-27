from django.db import models

class HousePrice(models.Model):
    rent = models.IntegerField(verbose_name="家賃_万円")
    age = models.IntegerField(verbose_name="築年数_年")
    distance = models.IntegerField(verbose_name="駅距離_km")
    layout = models.IntegerField(verbose_name="専有面積_m²")

def __str__(self):
    return f"物件データ:{self.rent}万円/築{self.age}年"