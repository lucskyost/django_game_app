from django.db.utils import OperationalError
import MySQLdb
from channels.consumer import AsyncConsumer
from .models import Game, GameMatrix, GameHistory
from channels.db import database_sync_to_async
from .helper import *
from channels.exceptions import StopConsumer
from django.core.exceptions import ObjectDoesNotExist
import json

class GameConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.game_code = self.scope['url_route']['kwargs']['game_code']
        self.game_matrix_id = self.scope['url_route']['kwargs']['game_matrix_id']
        self.player_name = self.scope['url_route']['kwargs']['player_name']
        self.player_type = self.scope['url_route']['kwargs']['player_type']

        game_object = await database_sync_to_async(Game.objects.filter)(game_code=self.game_code)
        game_exists = await database_sync_to_async(game_object.exists)()
        player_object = await database_sync_to_async(Game.objects.filter)(game_code=self.game_code, game_opponent='to-be-decided')
        player_exists = await database_sync_to_async(player_object.exists)()

        if(not game_exists or player_exists):
            await self.channel_layer.group_add(self.game_code, self.channel_name)

        self.game_id = await setup_game(self.game_code, self.game_matrix_id, self.player_name, self.player_type)
        print(f"[DEBUG] Created game_id: {self.game_id}")
        await self.send({
            'type':'websocket.accept',
        })

    async def websocket_receive(self, event):
        await update_matrix(self.game_matrix_id, event['text'], self.player_type)
        self.result = await check_winner(self.game_matrix_id)

        # Lưu lịch sử đấu khi trận đấu kết thúc
        if self.result in [44, 11, False]:
            try:
                game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
                game_matrix = await database_sync_to_async(GameMatrix.objects.get)(id=self.game_matrix_id)
                winner = self.player_name if self.result in [44, 11] else 'Draw'
                await database_sync_to_async(GameHistory.objects.using('history_db').create)(
                    player1=game.game_creator,
                    player2=game.game_opponent if game.game_opponent != 'to-be-decided' else None,
                    game_code=self.game_code,
                    winner=winner,
                    board=game_matrix.matrix_map
                )
            except Game.DoesNotExist:
                print(f"[ERROR] Game with ID {self.game_id} not found in DB.")
                raise StopConsumer()

        if self.result == 44:
            await self.channel_layer.group_send(self.game_code, {
                'type': 'send.message',
                'message': json.dumps({"msg_type":"result", "msg":self.player_name})
            })
        elif self.result == 11:
            await self.channel_layer.group_send(self.game_code, {
                'type': 'send.message',
                'message': json.dumps({"msg_type":"result", "msg":self.player_name})
            })
        elif self.result == False:
            await self.channel_layer.group_send(self.game_code, {
                'type': 'send.message',
                'message': json.dumps({"msg_type":"result", "msg":"game drawn"})
            })

        await self.channel_layer.group_send(self.game_code, {
            'type': 'send.message',
            'message': json.dumps({"msg_type":"chance", "position":event['text'], "symbol":self.player_type})
        })

    async def send_message(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['message']
        })

    async def websocket_disconnect(self, event):
        try:
            game_matrix = await database_sync_to_async(GameMatrix.objects.get)(id=self.game_matrix_id)
            await database_sync_to_async(game_matrix.delete)()
        except ObjectDoesNotExist:
            print(f"[WARN] GameMatrix with id {self.game_matrix_id} not found. Possibly already deleted.")
        except Exception as e:
            print(f"[ERROR] Unexpected error during disconnect: {e}")

        raise StopConsumer()


"""    async def websocket_disconnect(self, event):
        game_matrix = await database_sync_to_async(GameMatrix.objects.get)(id=self.game_matrix_id)
        await database_sync_to_async(game_matrix.delete)()
        raise StopConsumer()"""

