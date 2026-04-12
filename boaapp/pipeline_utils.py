"""
WebSocket-aware helper for sending pipeline progress updates.
Works with both sync (Celery eager) and async contexts.
"""

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def send_pipeline_update(run_id, status, progress_pct, current_step='', message=''):
    """Send a progress update through the channel layer and update the DB."""
    from .models import PipelineRun

    # Update database
    try:
        run = PipelineRun.objects.get(pk=run_id)
        run.status = status
        run.progress_pct = progress_pct
        run.current_step = current_step
        if status == 'complete':
            run.completed_at = timezone.now()
        elif status == 'failed':
            run.error_message = message
            run.completed_at = timezone.now()
        run.save()
    except PipelineRun.DoesNotExist:
        logger.warning(f"PipelineRun {run_id} not found")
        return

    # Send WebSocket message
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        group_name = f'pipeline_{run_id}'

        if status == 'complete':
            msg_type = 'pipeline_complete'
        elif status == 'failed':
            msg_type = 'pipeline_error'
        else:
            msg_type = 'pipeline_progress'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': msg_type.replace('.', '_'),
                'status': status,
                'progress_pct': progress_pct,
                'current_step': current_step,
                'message': message,
            }
        )
    except Exception as e:
        # WebSocket is optional — don't fail the pipeline if WS isn't available
        logger.debug(f"Could not send WS update for pipeline {run_id}: {e}")
