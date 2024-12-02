from channels import layers  # type: ignore[import]


class BaseBroadcaster:
    def __init__(self) -> None:
        self.layer = layers.get_channel_layer()
