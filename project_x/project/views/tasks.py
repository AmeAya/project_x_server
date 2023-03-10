from celery import shared_task
from main.celery import celery_app
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from ..models import *


@celery_app.task(serializer='pickle')
def create_records(user, data, *args, **kwargs):
    if user.position.name == 'Начальник участка':
        obj = ObjectModel.objects.get(head_of_object=user)
    else:
        obj = ObjectModel.objects.get(id=1)
    new_record = RecordsModel(
        date=datetime.now().strftime('%Y-%m-%d %H:%M'),
        material=MaterialModel.objects.get(id=data['material']),
        mark=MarkModel.objects.get(id=data['mark']),
        object=obj,
        constructive=ConstructiveModel.objects.get(id=data['constructive']),
        unit=UnitModel.objects.get(id=data['unit']),
        count=int(data['count']),
        user=user,
        provider=ProviderModel.objects.get(id=data['provider']),
        comments=data['comments'],
        created_at=datetime.now().strftime('%Y-%m-%d'),
        updated_at=datetime.now().strftime('%Y-%m-%d')
    )
    new_record.save()
    if 'block' in data.keys():
        for block_id in data['block']:
            new_record.block.add(BlockModel.objects.get(id=block_id))
        new_record.save()
    if 'floor' in data.keys():
        for floor_id in data['floor']:
            new_record.floor.add(FloorModel.objects.get(id=floor_id))
        new_record.save()
        return {"status": True}