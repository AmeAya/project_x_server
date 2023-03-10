from ..models import *
from rest_framework import serializers
from ..models import CustomUserModel


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ('id', 'phone', 'first_name', 'last_name', 'iin', 'position')
        read_only_fields = ('created_at', 'updated_at')

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'phone': instance.phone,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'iin': instance.iin,
            'position': PositionSerializer(instance.position).data
        }


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionModel
        fields = ['id', 'name', ]

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name
        }


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = ('first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialModel
        fields = ('id','name', 'author')


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkModel
        fields = ('id','name', 'material', 'author')


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockModel
        fields = ('id','name', 'object', 'author')


class ConstructiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockModel
        fields = ('id','name', 'author')


class ObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectModel
        fields = ['id', 'name', 'head_of_object', 'staff']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockModel
        fields = ('id','name', 'author')


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockModel
        fields = ('id','name', 'author')


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockModel
        fields = ('id','name', )


class RecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordsModel
        fields = ['id','material', 'mark', 'block', 'floor', 'constructive',
                  'unit', 'count', 'provider', 'comments']

    def to_representation(self, instance):
        representation = dict()
        representation['id'] = instance.id
        representation['date'] = instance.date.strftime('%d-%m-%Y %H-%M')
        representation['mark'] = instance.mark.name
        representation['material'] = instance.material.name
        representation['object'] = instance.object.name
        representation['block'] = []
        for block in instance.block.all():
            representation['block'].append(block.name)
        representation['floor'] = []
        for floor in instance.floor.all():
            representation['floor'].append(floor.name)
        if instance.constructive is not None:
            representation['constructive'] = instance.constructive.name
        else:
            representation['constructive'] = ""
        representation['unit'] = instance.unit.name
        representation['count'] = instance.count
        representation['user'] = instance.user.position.name + ": " + instance.user.first_name + " " + instance.user.last_name
        representation['provider'] = instance.provider.name
        representation['comments'] = instance.comments
        return representation


class RecordsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordsModel
        fields = "__all__"

    def to_representation(self, instance):
        representation = dict()
        representation['date'] = instance.date.strftime('%d-%m-%Y %H-%M')
        representation['mark'] = MarkSerializer(instance.mark).data
        representation['material'] = MaterialSerializer(instance.material).data
        representation['object'] = ObjectSerializer(instance.object).data
        representation['block'] = BlockSerializer(instance.block, many=True).data
        representation['floor'] = FloorSerializer(instance.floor, many=True).data
        if instance.constructive is not None:
            representation['constructive'] = ConstructiveSerializer(instance.constructive).data
        else:
            representation['constructive'] = ""
        representation['unit'] = UnitSerializer(instance.unit).data
        representation['count'] = instance.count
        representation['user'] = CustomUserSerializer(instance.user).data
        representation['provider'] = ProviderSerializer(instance.provider).data
        representation['comments'] = instance.comments
        return representation
