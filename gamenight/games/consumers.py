import logging

from channels.generic import websocket  # type: ignore[import]

from gamenight.games import models


class UserScoreConsumer(websocket.AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.username = self.scope["url_route"]["kwargs"]["username"]
        await self.channel_layer.group_add(self.username, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: str) -> None:
        logging.info("Disconnected: %s", close_code)
        await self.channel_layer.group_discard(self.username, self.channel_name)

    async def receive(self, text_data: str) -> None:
        """When a user manually hits refresh.

        We pass score=None to trigger a reload from the database.
        """
        logging.info("Received: %s", text_data)
        await self.channel_layer.group_send(
            self.username,
            {"type": "user.score", "score": None},
        )

    async def user_score(self, event: dict) -> None:
        """Send the user's score to the client.

        If we get the score, we send it. Otherwise, we fetch it from the database.
        """
        logging.warning("User score: %s", event)
        if not (score := event.get("score")):
            user = await models.User.objects.aget(username=self.username)
            score = user.score
        await self.send(
            text_data=f'<div id="{self.username}-score" class="score">{score}</div>',
        )
