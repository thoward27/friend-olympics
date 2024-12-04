from django.apps import AppConfig


class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gamenight.games"

    def ready(self) -> None:
        import iommi
        from django.templatetags import static
        from iommi import Style, register_style, style_bootstrap5

        boostrap5p = Style(
            style_bootstrap5.bootstrap5,
            base_template="base.html",
            root__assets__iommi_js=iommi.Asset.js(attrs__src=static.static("games/iommi.js")),
            root__assets__select2_dark=iommi.Asset.css(
                attrs__href=static.static("games/select2.css"),
            ),
        )
        register_style("bootstrap5p", boostrap5p)
