from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

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
    list_display = ("name", "minimum_players", "ranked", "estimated_duration", "decay")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "score", "first_name", "last_name", "is_staff")
