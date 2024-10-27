import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from argus.quiz.constant import answers_list
from argus.quiz.models import QuizScore, QuizSession
from argus.quiz.tasks import start_timer


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")

        if message_type == "answer-question":
            choice = text_data_json.get("choice")
            question_id = text_data_json["question_id"]
            session_id = text_data_json["room_id"]
            user_name = text_data_json["user_name"]
            response = "incorrect"
            for answer in answers_list:
                if answer.get("question_id") == question_id:
                    if choice and choice == answer.get("correct_choice"):
                        response = "correct"
            await self.update_score(session_id, user_name, response)
            await self.send(
                text_data=json.dumps({"choice": choice, "message": response})
            )
            room_name = self.scope["url_route"]["kwargs"]["room_name"]
            activity_group_name = "session_%s" % room_name
            activity_msg = {
                "type": "update_activity",
                "message": f"{user_name} answers question {question_id} {response}ly.",
                "question_id": question_id,
            }
            ranking = await self.get_ranking(session_id)
            if ranking:
                activity_msg["ranking"] = ranking
            await self.channel_layer.group_send(activity_group_name, activity_msg)

    @database_sync_to_async
    def update_score(self, session_id, user_name, response):
        try:
            user_score = QuizScore.objects.get(
                quiz_session__session_id=session_id, username=user_name
            )
            if response == "correct":
                user_score.score = user_score.score + 1
            user_score.current_question += 1
            user_score.save()
        except QuizScore.DoesNotExist:
            quiz_session = QuizSession.objects.filter(
                session_id=session_id, is_active=True
            ).first()
            if user_name and quiz_session:
                QuizScore.objects.create(
                    quiz_session=quiz_session,
                    username=user_name,
                    score=1 if response == "correct" else 0,
                    max_score=len(answers_list),
                )

    @database_sync_to_async
    def get_ranking(self, session_id):
        quiz_session = QuizSession.objects.get(session_id=session_id)
        return list(
            QuizScore.objects.filter(quiz_session=quiz_session)
            .all()
            .order_by("-score")
            .values("username", "score", "max_score", "current_question")
        )


class TimerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "timer_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")

        if message_type == "start_timer":
            session_id = text_data_json["room_id"]
            quiz_duration = text_data_json.get("duration", 60)
            await self.update_session_status(session_id)
            start_timer.delay(self.room_group_name, quiz_duration, self.room_name)

    async def timer_update(self, event):
        remaining_time = event["remaining_time"]
        await self.send(
            text_data=json.dumps({"type": "timer", "remaining_time": remaining_time})
        )

    async def timer_ended(self, event):
        await self.send(
            text_data=json.dumps({"type": "timer", "message": "Time is up!"})
        )

    @database_sync_to_async
    def update_session_status(self, session_id):
        try:
            quiz_session = QuizSession.objects.get(
                session_id=session_id, is_active=True
            )
            quiz_session.status = "in progress"
            quiz_session.save()
        except QuizScore.DoesNotExist:
            pass


class ActivityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.activity_group_name = "session_%s" % self.room_name

        await self.channel_layer.group_add(self.activity_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.activity_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.activity_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def update_activity(self, event):
        message = event["message"]
        ranking = event.get("ranking")
        question_id = event["question_id"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "ranking": ranking,
                    "question_id": question_id,
                }
            )
        )
