from django.db import models


class TimeFieldTZ(models.Field):
    def db_type(self, connection):
        return 'timetz'
