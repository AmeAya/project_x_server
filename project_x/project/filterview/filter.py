from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..permissions import group_required, CustomPermissions
from ..serializers import *


class FilterApiView(APIView):
    """Фильтр на Рекордс"""
    permission_classes = [CustomPermissions, ]

    def post(self, request, *args, **kwargs):
        if request.data['material'] is not None:
            material_id = request.data['material']
        else:
            material_id = None

        try:
            if request.data['mark'] is not None:
                mark_id = request.data['mark']
        except:
            mark_id = None

        try:
            if request.data['constructive'] is not None:
                constructive_id = request.data['constructive']
        except:
            constructive_id = None

        try:
            if request.data['object'] is not None:
                object_id = request.data['object']
        except:
            object_id = None

        try:
            if request.data['block'] is not None:
                block_id = request.data['block']
        except:
            block_id = None

        try:
            if request.data['user'] is not None:
                user_id = request.data['user']
        except:
            user_id = None

        try:
            if request.data['provider'] is not None:
                provider_id = request.data['provider']
        except:
            provider_id = None
        """Фильтр на: Материал, Марка, Конструктив, Объект, Блок, Юзер, Провайдер"""
        if material_id is not None and mark_id is not None and constructive_id is not None and object_id is not None \
                and block_id is not None and user_id is not None and provider_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, mark=mark_id, constructive=constructive_id,
                                                  object=object_id, block=block_id, user=user_id, provider=provider_id)

        elif material_id is not None and mark_id is not None and constructive_id is not None and object_id is not None \
                and block_id is not None and user_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, mark=mark_id, constructive=constructive_id,
                                                  object=object_id, block=block_id, user=user_id)

        elif material_id is not None and mark_id is not None and constructive_id is not None and object_id is not None \
                and block_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, mark=mark_id, constructive=constructive_id,
                                                  object=object_id, block=block_id)

        elif material_id is not None and mark_id is not None and constructive_id is not None and object_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, mark=mark_id, constructive=constructive_id,
                                                  object=object_id)

        elif material_id is not None and mark_id is not None and object_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, mark=mark_id, object=object_id)

        elif material_id is not None and constructive_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, constructive=constructive_id)
        elif material_id is not None and mark_id is not None:
            filters = RecordsModel.objects.filter(material=material_id, mark=mark_id)
        elif material_id is not None:
            filters = RecordsModel.objects.filter(material=material_id)
        elif mark_id is not None:
            filters = RecordsModel.objects.filter(mark=mark_id)
        elif constructive_id is not None:
            filters = RecordsModel.objects.filter(constructive=constructive_id)
        elif user_id is not None:
            filters = RecordsModel.objects.filter(user=user_id)
        elif object_id is not None:
            filters = RecordsModel.objects.filter(object=object_id)
        elif block_id is not None:
            filters = RecordsModel.objects.filter(block=block_id)
        elif provider_id is not None:
            filters = RecordsModel.objects.filter(provider=provider_id)
        return Response(data=RecordsSerializer(filters, many=True).data, status=status.HTTP_200_OK)
