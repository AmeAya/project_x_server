from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager


class AbstractTimeTracker(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=('Дата добавление'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=('Дата обновление'))

    class Meta:
        abstract = True
        ordering = ('updated_at', 'created_at')


class PositionModel(AbstractTimeTracker):
    name = models.CharField('Должность', max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class CustomUserModel(AbstractBaseUser, PermissionsMixin, AbstractTimeTracker):
    phone = models.CharField(max_length=15, unique=True, verbose_name='Номер телефона', default=' ')
    mail = models.CharField(max_length=50, unique=True, verbose_name='Почта', default=' ')
    first_name = models.CharField(max_length=30, blank=False, null=False, verbose_name='Имя')
    last_name = models.CharField(max_length=30, blank=False, null=False, verbose_name='Фамилия')
    iin = models.CharField(max_length=12, unique=True, blank=False, null=False, verbose_name='ИИН')
    position = models.ForeignKey(PositionModel, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Должность')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'mail'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name', 'iin']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('mail', )

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name)


class CodeModel(AbstractTimeTracker):
    code = models.CharField(max_length=6, blank=True, null=True, unique=True)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, blank=True, null=True)
    expire_date = models.DateTimeField(default=timezone.now()+timezone.timedelta(minutes=5))


class ObjectModel(AbstractTimeTracker):
    name = models.CharField('Название объекта', max_length=50)
    head_of_object = models.ForeignKey(CustomUserModel, blank=True, null=True, on_delete=models.CASCADE, related_name='object_head')
    staff = models.ManyToManyField(CustomUserModel, related_name='object_staff')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'


class MaterialModel(AbstractTimeTracker):
    name = models.CharField('Название материала', max_length=50)
    author = models.ForeignKey(CustomUserModel, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class MarkModel(AbstractTimeTracker):
    name = models.CharField('Название марки', max_length=50)
    material = models.ForeignKey(MaterialModel, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUserModel, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Марка'
        verbose_name_plural = 'Марки'


class BlockModel(AbstractTimeTracker):
    name = models.CharField('Название блока', max_length=50)
    object = models.ForeignKey(ObjectModel, blank=True, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUserModel, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'


class FloorModel(AbstractTimeTracker):
    FLOOR_CHOICES = [(str(i), i) for i in range(-2, 21)]
    name = models.CharField(verbose_name='этаж', max_length=12, choices=FLOOR_CHOICES, default=0)

    class Meta:
        verbose_name = 'Этаж'
        verbose_name_plural = 'Этажи'

    def __str__(self):
        return self.name


class ConstructiveModel(AbstractTimeTracker):
    name = models.CharField('Название конструктива', max_length=50)
    author = models.ForeignKey(CustomUserModel, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Конструктив'
        verbose_name_plural = 'Конструктивы'


class UnitModel(AbstractTimeTracker):
    name = models.CharField('Единица измерения', max_length=50)
    author = models.ForeignKey(CustomUserModel, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Измерения'
        verbose_name_plural = 'Измерении'


class ProviderModel(AbstractTimeTracker):
    name = models.CharField('Поставщик', max_length=50)
    author = models.ForeignKey(CustomUserModel, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class RecordsModel(AbstractTimeTracker):
    date = models.DateTimeField('Дата заполнения')
    material = models.ForeignKey(MaterialModel, on_delete=models.CASCADE, verbose_name='Материал')
    mark = models.ForeignKey(MarkModel, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Марка')
    object = models.ForeignKey(ObjectModel, on_delete=models.CASCADE, verbose_name='Объект')
    block = models.ManyToManyField(BlockModel, verbose_name='Блок')
    floor = models.ManyToManyField(FloorModel, blank=True, verbose_name='Этаж')
    constructive = models.ForeignKey(ConstructiveModel, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Конструктив')
    unit = models.ForeignKey(UnitModel, on_delete=models.CASCADE, verbose_name='ед. изм.')
    count = models.IntegerField('Количество')
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, verbose_name='Пользователь')
    provider = models.ForeignKey(ProviderModel, on_delete=models.CASCADE, verbose_name='Потсавщик')
    comments = models.CharField('Коментарии', blank=True, null=True, max_length=255)
    is_hidden = models.BooleanField(default=False, null=False, blank=False)

    def get_block_name(self):
        return ", ".join([p.name for p in self.block.all()])

    def get_floor_name(self):
        return ", ".join([p.name for p in self.floor.all()])

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'


class RecordsDeleteModel(AbstractTimeTracker):
    old_record = models.OneToOneField(RecordsModel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Таблица удаление записи'
        verbose_name_plural = 'Таблица удаление записи'


class RecordsLogModel(AbstractTimeTracker):
    old_record = models.ForeignKey(RecordsModel, on_delete=models.CASCADE, related_name='Старая_запись', null=False, blank=False)
    new_record = models.ForeignKey(RecordsModel, on_delete=models.CASCADE, related_name='Новая_запись', null=True, blank=True)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Таблица изменений записей'
        verbose_name_plural = 'Таблица изменений записей'
