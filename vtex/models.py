from django.db import models
from item.models import (Sku, Group, Color)


class ExportSku(models.Model):
    base_sku = models.ForeignKey(to=Sku, related_name="export_sku", on_delete=models.CASCADE)
    group = models.ForeignKey(to=Group, related_name="export_sku_group", on_delete=models.CASCADE)
    color = models.ForeignKey(to=Color, related_name="export_sku_color", on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.base_sku)

    class Meta:
        app_label = "vtex"
        db_table = "vtex_export_sku"
