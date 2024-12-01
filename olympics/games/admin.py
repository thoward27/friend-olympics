from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Fixture, Game, User


class FixtureRankInline(admin.TabularInline):
    model = Fixture.users.through


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    inlines = (FixtureRankInline,)
    list_display = ("game", "started", "ended", "applied")
    list_filter = ["game__name", ("ended", admin.EmptyFieldListFilter), "applied", "users"]
    ordering = ("-started",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = (
        "name",
        "minimum_players",
        "maximum_players",
        "ranked",
        "estimated_duration",
        "decay",
        "randomness",
    )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "score", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password", "score")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
