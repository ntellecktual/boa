import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class PipelineProgressConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time pipeline progress updates."""

    async def connect(self):
        self.run_id = self.scope['url_route']['kwargs']['run_id']
        self.group_name = f'pipeline_{self.run_id}'

        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send current status immediately
        status = await self._get_pipeline_status()
        if status:
            await self.send(text_data=json.dumps(status))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def pipeline_progress(self, event):
        """Handle pipeline progress messages from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'status': event.get('status', ''),
            'progress_pct': event.get('progress_pct', 0),
            'current_step': event.get('current_step', ''),
            'message': event.get('message', ''),
        }))

    async def pipeline_complete(self, event):
        """Handle pipeline completion."""
        await self.send(text_data=json.dumps({
            'type': 'complete',
            'status': 'complete',
            'progress_pct': 100,
            'message': event.get('message', 'Pipeline complete!'),
        }))

    async def pipeline_error(self, event):
        """Handle pipeline errors."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'status': 'failed',
            'message': event.get('message', 'Pipeline failed.'),
        }))

    @database_sync_to_async
    def _get_pipeline_status(self):
        from .models import PipelineRun
        try:
            run = PipelineRun.objects.get(pk=self.run_id)
            return {
                'type': 'progress',
                'status': run.status,
                'progress_pct': run.progress_pct,
                'current_step': run.current_step,
            }
        except PipelineRun.DoesNotExist:
            return None


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for RAG chatbot conversations."""

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'

        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close()
            return

        # Verify user owns the conversation
        has_access = await self._verify_access(user.id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming chat messages."""
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        user = self.scope['user']

        # Save user message
        await self._save_message(user.id, 'user', message)

        # Send typing indicator
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': True,
        }))

        # Generate AI response via RAG
        try:
            response, sources = await self._get_rag_response(user.id, message)
            await self._save_message(user.id, 'assistant', response, sources)

            await self.send(text_data=json.dumps({
                'type': 'message',
                'role': 'assistant',
                'content': response,
                'sources': sources,
            }))
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Sorry, I encountered an error. Please try again.',
            }))
        finally:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': False,
            }))

    @database_sync_to_async
    def _verify_access(self, user_id):
        from .models import ChatConversation
        return ChatConversation.objects.filter(pk=self.conversation_id, user_id=user_id).exists()

    @database_sync_to_async
    def _save_message(self, user_id, role, content, sources=None):
        from .models import ChatMessage
        return ChatMessage.objects.create(
            conversation_id=self.conversation_id,
            role=role,
            content=content,
            sources=sources,
        )

    @database_sync_to_async
    def _get_rag_response(self, user_id, query):
        from .rag_engine import get_rag_response
        from .models import ChatConversation
        conversation = ChatConversation.objects.get(pk=self.conversation_id)
        return get_rag_response(query, conversation.document_id)
