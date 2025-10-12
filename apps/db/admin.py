from django.contrib import admin

import apps.db.models as models_ref
from utils.register_models import register_models


# Register your models here.
register_models(models_ref, admin.site.register)
