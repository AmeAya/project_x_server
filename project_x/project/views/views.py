from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..permissions import group_required, CustomPermissions
from ..serializers import *
from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django.contrib.auth import login, logout
from drf_yasg.utils import swagger_auto_schema
from project.views.tasks import create_records
from ..smtplib.mail import send_mail
import random
import mimetypes


def f_login(request, mail):
    user = CustomUserModel.objects.get(mail=mail)
    if user is not None:
        login(request, user)


def generate_code(user):
    if user == 0:
        while True:
            code = random.randint(100000, 999999)
            try:
                query = CodeModel.objects.get(code=code)
                continue
            except:
                obj = CodeModel(code=code)
                obj.user = None
                obj.save()
                break
        return code
    else:
        while True:
            code = random.randint(100000, 999999)
            try:
                query = CodeModel.objects.get(code=code)
                continue
            except:
                obj = CodeModel(code=code, user=user)
                obj.save()
                break
        return code


class PhoneConfirmationApiView(APIView):
    def post(self, request):
        if 'mail' in request.data.keys():
            mail = request.data['mail']
            request.session['mail'] = mail
            if CustomUserModel.objects.filter(mail=mail).exists():
                new_code = generate_code(CustomUserModel.objects.get(mail=mail))
                send_mail(mail, new_code)
                request.session['new'] = False
                return Response(data={'code': new_code, 'success': 'old user'}, status=status.HTTP_200_OK)
            else:
                new_code = generate_code(0)
                send_mail(mail, new_code)
                request.session['new'] = True
                return Response(data={'code': new_code, 'success': 'new user'}, status=status.HTTP_200_OK)
        elif 'code' in request.data.keys():
            code = str(request.data.get('code'))
            if request.session['new'] is False:
                if CodeModel.objects.filter(code=code).exists():
                    f_login(request, request.session['mail'])
                    del request.session['new']
                    del request.session['mail']
                    CodeModel.objects.get(code=code).delete()
                    return Response(data={'success': 'Auth'}, status=status.HTTP_200_OK)
                else:
                    return Response(data={'error': 'Code is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            elif request.session['new']:
                if CodeModel.objects.filter(code=code).exists():
                    del request.session['new']
                    CodeModel.objects.get(code=code).delete()
                    return Response(data={'success': 'code is valid'}, status=status.HTTP_200_OK)
                else:
                    return Response(data={'error': 'code is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'error': 'sessions error'}, status=status.HTTP_400_BAD_REQUEST)


class LogOutView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response(
                data={'success': 'Logout successfully'},
                status=status.HTTP_200_OK)
        else:
            return Response(
                data={'error': 'You are not logged in'},
                status=status.HTTP_400_BAD_REQUEST)


class RegistrationApiView(APIView):
    def post(self, request, *args, **kwargs):
        if request.data:
            phone = request.data.get('phone')
            mail = request.session['mail']
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            iin = request.data.get('iin')
            position = PositionModel.objects.get(id=request.data.get('position'))
            user = CustomUserModel(
                first_name=first_name,
                phone=phone,
                mail=mail,
                last_name=last_name,
                position=position,
                iin=iin)
            my_group = Group.objects.get(name='not confirmed')
            user.save()
            my_group.user_set.add(user)
            del request.session['mail']
            login(request, user)
            return Response(data={'success': 'user is create'}, status=status.HTTP_201_CREATED)


class UserApiView(APIView):
    queryset = CustomUserModel.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        query = CustomUserModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=CustomUserSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=CustomUserSerializer,
        query_serializer=CustomUserSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create user',
        operation_description='Create new user',
    )
    def post(self, request, *args, **kwargs):
        new_user = CustomUserModel(
            phone=int(request.data['phone']),
            mail=str(request.data['mail']),
            first_name=str(request.data['first_name']),
            last_name=str(request.data['last_name']),
            iin=int(request.data['iin']),
            position=str(request.data['position']),
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_user.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class ObjectApiView(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query = ObjectModel.objects.all()

            paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
            return Response(
                data=ObjectSerializer(paginated_query, many=True).data,
                status=status.HTTP_200_OK)
        else:
            user_groups = []
            for group in request.user.groups.all():
                user_groups.append(group.name)

            if 'CRU' in user_groups:
                user_object = ObjectModel.objects.get(head_of_object=request.user)
                query = ObjectModel.objects.filter(object=user_object)

            elif 'CR' in user_groups:
                user_object = ObjectModel.objects.get(staff__in=[request.user])
                query = ObjectModel.objects.filter(object=user_object)

            elif 'CRUD' or 'R' in user_groups:
                try:
                    if ObjectModel.objects.get(id=request.data.get('object')):
                        query = ObjectModel.objects.filter(id=request.data.get('object'))
                except:
                    query = ObjectModel.objects.all()

            paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
            return Response(
                data=ObjectSerializer(paginated_query, many=True).data,
                status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ObjectSerializer,
        query_serializer=ObjectSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create object',
        operation_description='Create new object',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_object = ObjectModel(
            name=str(request.data['name']),
            head_of_object=request.user,
            staff=request.data['user'],
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_object.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class PositionApiView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query = PositionModel.objects.all()

            paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
            return Response(
                data=PositionSerializer(paginated_query, many=True).data,
                status=status.HTTP_200_OK)
        else:
            user_groups = []
            for group in request.user.groups.all():
                user_groups.append(group.name)

            if 'CRU' in user_groups:
                user_object = ObjectModel.objects.get(head_of_object=request.user)
                query = PositionModel.objects.filter(object=user_object)

            elif 'CR' in user_groups:
                user_object = ObjectModel.objects.get(staff__in=[request.user])
                query = PositionModel.objects.filter(object=user_object)

            elif 'CRUD' or 'R' in user_groups:
                query = PositionModel.objects.all()

            paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
            return Response(
                data=PositionSerializer(paginated_query, many=True).data,
                status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=PositionSerializer,
        query_serializer=PositionSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create position',
        operation_description='Create new position',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_position = PositionModel(
            name=str(request.data['name']),
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_position.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class MaterialViewSets(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        query = MaterialModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=MaterialSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=MaterialSerializer,
        query_serializer=MaterialSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create material',
        operation_description='Create new material',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_material = MaterialModel(
            name=str(request.data['name']),
            author=request.user,
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_material.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class MarkViewSets(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        query = MarkModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=MarkSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=MarkSerializer,
        query_serializer=MarkSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create mark',
        operation_description='Create new mark',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_mark = MarkModel(
            name=str(request.data['name']),
            material=MaterialModel.objects.get(id=request.data['material']),
            author=request.user,
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_mark.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class BlockViewSets(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        query = BlockModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=BlockSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=BlockSerializer,
        query_serializer=BlockSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create block',
        operation_description='Create new block',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_block = BlockModel(
            name=str(request.data['name']),
            object=ObjectModel.objects.get(id=request.data['object']),
            author=request.user,
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_block.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class FloorApiView(APIView):
    permission_classes = [CustomPermissions, ]

    @swagger_auto_schema(
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Get floors',
        operation_description='Get list of all floors',
    )
    def get(self, request, *args, **kwargs):
        query = FloorModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=FloorSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)


class ConstructiveViewSets(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        query = ConstructiveModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=ConstructiveSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ConstructiveSerializer,
        query_serializer=ConstructiveSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create constructive',
        operation_description='Create new constructive',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_construct = ConstructiveModel(
            name=str(request.data['name']),
            author=request.user,
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_construct.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class UnitViewSets(APIView):
    serializer_class = UnitSerializer

    def get(self, request, *args, **kwargs):
        query = UnitModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=UnitSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UnitSerializer,
        query_serializer=UnitSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create unit',
        operation_description='Create new unit',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_unit = UnitModel(
            name=str(request.data['name']),
            author=request.user,
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_unit.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class ProviderViewSets(APIView):
    serializer_class = ProviderSerializer

    def get(self, request, *args, **kwargs):
        query = ProviderModel.objects.all()

        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        return Response(
            data=ProviderSerializer(paginated_query, many=True).data,
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ProviderSerializer,
        query_serializer=ProviderSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create provider',
        operation_description='Create new provider',
    )
    def post(self, request, *args, **kwargs):
        # if request.user.position.name == 'Начальник участка':
        #     obj = ObjectModel.objects.get(head_of_object=request.user)
        # else:
        #     obj = ObjectModel.objects.get(id=1)
        new_provider = ProviderModel(
            name=str(request.data['name']),
            author=request.user,
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d'),
        )
        new_provider.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)


class RecordsApiView(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query = RecordsModel.objects.all()
        else:
            user_groups = []
            for group in request.user.groups.all():
                user_groups.append(group.name)
            if 'CRU' in user_groups:
                user_object = get_object_or_404(ObjectModel, head_of_object=request.user)
                query = RecordsModel.objects.filter(object=user_object, is_hidden=False)
            elif 'CR' in user_groups:
                user_object = get_object_or_404(ObjectModel, staff__in=[request.user])
                query = RecordsModel.objects.filter(object=user_object, is_hidden=False)
            elif 'CRUD' or 'R' in user_groups:
                query = RecordsModel.objects.filter(is_hidden=False)

        params = {}
        if request.GET.lists():
            for param in request.GET.lists():
                params[param[0]] = param[1][0]

            if 'start_date' in params.keys() and 'end_date' in params.keys():
                params['start_date'] = datetime.strptime(params['start_date'], '%d-%m-%Y')
                params['end_date'] = datetime.strptime(params['end_date'], '%d-%m-%Y')
                query = query.filter(date__range=[params['start_date'], params['end_date']])

            models_dict = {
                'material': MaterialModel,
                'mark': MarkModel,
                'object': ObjectModel,
                'block': BlockModel,
                'floor': FloorModel,
                'constructive': ConstructiveModel,
                'unit': UnitModel,
                'user': CustomUserModel,
                'provider': ProviderModel
            }
            for key, value in params.items():
                if key in models_dict.keys():
                    filtered_dict = {key: get_object_or_404(models_dict[key], id=value)}
                    query = query.filter(**filtered_dict)

                if 'deleted' in params.keys():
                    query = query.filter(is_hidden=params['deleted'])
        if 'page' in params.keys():
            page = int(params['page'])
        else:
            page = 1
        if 'download' in params.keys():
                    if bool(params['download']) is True:
                        from ..down_ex import download_exe
                        wb = download_exe(query)
                        return HttpResponseRedirect("records/download")
        query = query.order_by('-date')
        paginated_query = PageNumberPagination().paginate_queryset(query, request, view=self)
        data = {'records': RecordsSerializer(paginated_query, many=True).data}

        data.update({'pagination':
            {
                'page': page,
                'page_size': 15,
                'total_count': len(query)
            }
        })
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=RecordsSerializer,
        query_serializer=RecordsSerializer,
        responses={
            '200': 'Ok Request',
            '400': "Bad Request"
        },
        security=[],
        operation_id='Create record',
        operation_description='Create new records',
    )
    def post(self, request, *args, **kwargs):
        user_groups = []
        for group in request.user.groups.all():
            user_groups.append(group.name)
        if 'CRUD' in user_groups:
            obj=get_object_or_404(ObjectModel, id=request.data['object'])
        elif 'CRU' in user_groups:
            obj = ObjectModel.objects.get(head_of_object=request.user)
        elif 'CR' in user_groups:
            obj = ObjectModel.objects.get(staff__in=[request.user])
        new_record = RecordsModel(
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            material=MaterialModel.objects.get(id=request.data['material']),
            mark=MarkModel.objects.get(id=request.data['mark']),
            object=obj,
            unit=UnitModel.objects.get(id=request.data['unit']),
            count=int(request.data['count']),
            user=request.user,
            provider=ProviderModel.objects.get(id=request.data['provider']),
            comments=request.data['comments'],
            created_at=datetime.now().strftime('%Y-%m-%d'),
            updated_at=datetime.now().strftime('%Y-%m-%d')
        )
        new_record.save()
        if 'block' in request.data.keys():
            for block_id in request.data['block']:
                new_record.block.add(BlockModel.objects.get(id=block_id))
            new_record.save()
        if 'floor' in request.data.keys():
            for floor_id in request.data['floor']:
                new_record.floor.add(FloorModel.objects.get(id=floor_id))
            new_record.save()
        if 'constructive' in request.data.keys() and request.data['constructive'] is not None:
            new_record.constructive = ConstructiveModel.objects.get(id=request.data['constructive'])
            new_record.save()
        return Response(data={'data': 'success'}, status=status.HTTP_201_CREATED)

class RecordsDetailView(APIView):
    def get(self, request, record_id, *args, **kwargs):
        query = get_object_or_404(RecordsModel, id=record_id)
        return Response(data=RecordsDetailSerializer(query, many=False).data, status=status.HTTP_200_OK)

    def put(self, request, record_id, *args, **kwargs):
        user_groups = []
        for group in request.user.groups.all():
            user_groups.append(group.name)
        if 'CRUD' in user_groups or 'CRU' in user_groups:
            old_record = get_object_or_404(RecordsModel, id=record_id)
            new_record = RecordsModel(
                date=old_record.date,
                material=MaterialModel.objects.get(id=request.data['material']),
                mark=MarkModel.objects.get(id=request.data['mark']),
                object=old_record.object,
                unit=UnitModel.objects.get(id=request.data['unit']),
                count=int(request.data['count']),
                user=request.user,
                provider=ProviderModel.objects.get(id=request.data['provider']),
                comments=request.data['comments'],
                created_at=datetime.now().strftime('%Y-%m-%d'),
                updated_at=datetime.now().strftime('%Y-%m-%d')
            )
            new_record.save()
            if 'block' in request.data.keys():
                for block_id in request.data['block']:
                    new_record.block.add(BlockModel.objects.get(id=block_id))
                new_record.save()
            if 'floor' in request.data.keys():
                for floor_id in request.data['floor']:
                    new_record.floor.add(FloorModel.objects.get(id=floor_id))
                new_record.save()
            if 'constructive' in request.data.keys() and request.data['constructive'] is not None:
                try:
                    new_record.constructive = ConstructiveModel.objects.get(id=request.data['constructive'])
                    new_record.save()
                except:
                    pass
            old_record.is_hidden = True
            old_record.save()
            update = RecordsLogModel(
                old_record=old_record,
                new_record=new_record,
                user=request.user
            )
            update.save()
            return Response(data={'data': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'data': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, record_id, *args, **kwargs):
        user_groups = []
        for group in request.user.groups.all():
            user_groups.append(group.name)
        if 'CRUD' in user_groups:
            old_record = get_object_or_404(RecordsModel, id=record_id)
            old_record.is_hidden = True
            old_record.save()
            delete = RecordsDeleteModel(
                old_record=old_record,
                user=request.user
            )
            delete.save()
            return Response(data={'data': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'data': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)


class UserSelfApiView(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_groups = []
            for group in request.user.groups.all():
                user_groups.append(group.name)
            from django.middleware.csrf import get_token
            if 'CRU' in user_groups:
                obj = ObjectModel.objects.get(head_of_object=request.user)
            elif 'CR' in user_groups:
                obj = ObjectModel.objects.get(staff__in=[request.user])
            else:
                obj = "None"
            if obj == "None":
                data = {'user': CustomUserSerializer(request.user).data, 'group': str(request.user.groups.all()[0]),'csrf_token': get_token(request), 'object': str(obj)}
            elif obj != "None":
                data = {'user': CustomUserSerializer(request.user).data, 'group': str(request.user.groups.all()[0]),'csrf_token': get_token(request),'object': ObjectSerializer(obj).data}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data={'message': 'You are not logged in'}, status=status.HTTP_403_FORBIDDEN)

class ObjectBlockView(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, object_id, *args, **kwargs):
        this_object = get_object_or_404(ObjectModel, id=object_id)
        this_blocks = BlockModel.objects.filter(object=this_object)
        return Response(data=BlockSerializer(this_blocks, many=True).data,
                        status=status.HTTP_200_OK)


class MarkMaterialView(APIView):
    permission_classes = [CustomPermissions, ]

    def get(self, request, material_id, *args, **kwargs):
        this_material = get_object_or_404(MaterialModel, id=material_id)
        this_marks = MarkModel.objects.filter(material=this_material)
        return Response(data=MarkSerializer(this_marks, many=True).data,
                        status=status.HTTP_200_OK)

def download_file(request):
    filename = 'file.xlsx'
    path = open(filename, "rb")
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filename)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
