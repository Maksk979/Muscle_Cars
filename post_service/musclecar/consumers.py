import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Post
from django.core.exceptions import ObjectDoesNotExist

class LikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "likes"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        posts = await sync_to_async(list)(Post.objects.all())
        for post in posts:
            await self.send(text_data=json.dumps({
                "like_count": post.like_count,
                "post_id": post.id,
            }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        post_id = data.get("post_id")
    
        if action == "like":
            try:
                post = await sync_to_async(Post.objects.get)(id=post_id)
            except ObjectDoesNotExist:
                print(f"Post with id {post_id} not found")
                return

            if data.get("toggle"):
                post.like_count = max(0, post.like_count - 1)
            else:
                post.like_count += 1
            await sync_to_async(post.save)()

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_update",
                    "like_count": post.like_count,
                    "post_id": post_id
                }
            )

    async def send_update(self, event):
        await self.send(text_data=json.dumps({
            "like_count": event["like_count"],
            "post_id": event["post_id"],
        }))