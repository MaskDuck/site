"""Converters from Django models to data interchange formats and back."""

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, ValidationError
from rest_framework_bulk import BulkSerializerMixin

from .models import (
    BotSetting, DeletedMessage,
    DocumentationLink, Infraction,
    LogEntry, MessageDeletionContext,
    Nomination, OffTopicChannelName,
    Reminder, Role,
    SnakeFact, SnakeIdiom,
    SnakeName, SpecialSnake,
    Tag, User
)


class BotSettingSerializer(ModelSerializer):
    """A class providing (de-)serialization of `BotSetting` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = BotSetting
        fields = ('name', 'data')


class DeletedMessageSerializer(ModelSerializer):
    """
    A class providing (de-)serialization of `DeletedMessage` instances.

    The serializer generally requires a valid `deletion_context` to be
    given, which should be created beforehand. See the `DeletedMessage`
    model for more information.
    """

    author = PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    deletion_context = PrimaryKeyRelatedField(
        queryset=MessageDeletionContext.objects.all(),
        # This will be overridden in the `create` function
        # of the deletion context serializer.
        required=False
    )

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = DeletedMessage
        fields = (
            'id', 'author',
            'channel_id', 'content',
            'embeds', 'deletion_context'
        )


class MessageDeletionContextSerializer(ModelSerializer):
    """A class providing (de-)serialization of `MessageDeletionContext` instances."""

    deletedmessage_set = DeletedMessageSerializer(many=True)

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = MessageDeletionContext
        fields = ('actor', 'creation', 'id', 'deletedmessage_set')
        depth = 1

    def create(self, validated_data):
        """
        Return a `MessageDeletionContext` based on the given data.

        In addition to the normal attributes expected by the `MessageDeletionContext` model
        itself, this serializer also allows for passing the `deletedmessage_set` element
        which contains messages that were deleted as part of this context.
        """

        messages = validated_data.pop('deletedmessage_set')
        deletion_context = MessageDeletionContext.objects.create(**validated_data)
        for message in messages:
            DeletedMessage.objects.create(
                deletion_context=deletion_context,
                **message
            )

        return deletion_context


class DocumentationLinkSerializer(ModelSerializer):
    """A class providing (de-)serialization of `DocumentationLink` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = DocumentationLink
        fields = ('package', 'base_url', 'inventory_url')


class InfractionSerializer(ModelSerializer):
    """A class providing (de-)serialization of `Infraction` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = Infraction
        fields = (
            'id', 'inserted_at', 'expires_at', 'active', 'user', 'actor', 'type', 'reason', 'hidden'
        )

    def validate(self, attrs):
        """Validate data constraints for the given data and abort if it is invalid."""

        infr_type = attrs.get('type')

        expires_at = attrs.get('expires_at')
        if expires_at and infr_type in ('kick', 'warning'):
            raise ValidationError({'expires_at': [f'{infr_type} infractions cannot expire.']})

        hidden = attrs.get('hidden')
        if hidden and infr_type in ('superstar',):
            raise ValidationError({'hidden': [f'{infr_type} infractions cannot be hidden.']})

        return attrs


class ExpandedInfractionSerializer(InfractionSerializer):
    """A class providing expanded (de-)serialization of `Infraction` instances.

    In addition to the fields of `Infraction` objects themselves, this
    serializer also attaches the `user` and `actor` fields when serializing.
    """

    def to_representation(self, instance):
        """Return the dictionary representation of this infraction."""

        ret = super().to_representation(instance)

        user = User.objects.get(id=ret['user'])
        user_data = UserSerializer(user).data
        ret['user'] = user_data

        actor = User.objects.get(id=ret['actor'])
        actor_data = UserSerializer(actor).data
        ret['actor'] = actor_data

        return ret


class LogEntrySerializer(ModelSerializer):
    """A class providing (de-)serialization of `LogEntry` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = LogEntry
        fields = (
            'application', 'logger_name', 'timestamp',
            'level', 'module', 'line', 'message'
        )


class OffTopicChannelNameSerializer(ModelSerializer):
    """A class providing (de-)serialization of `OffTopicChannelName` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = OffTopicChannelName
        fields = ('name',)

    def to_representation(self, obj):
        """
        Return the representation of this `OffTopicChannelName`.

        This only returns the name of the off topic channel name. As the model
        only has a single attribute, it is unnecessary to create a nested dictionary.
        Additionally, this allows off topic channel name routes to simply return an
        array of names instead of objects, saving on bandwidth.
        """

        return obj.name


class SnakeFactSerializer(ModelSerializer):
    """A class providing (de-)serialization of `SnakeFact` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = SnakeFact
        fields = ('fact',)


class SnakeIdiomSerializer(ModelSerializer):
    """A class providing (de-)serialization of `SnakeIdiom` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = SnakeIdiom
        fields = ('idiom',)


class SnakeNameSerializer(ModelSerializer):
    """A class providing (de-)serialization of `SnakeName` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = SnakeName
        fields = ('name', 'scientific')


class SpecialSnakeSerializer(ModelSerializer):
    """A class providing (de-)serialization of `SpecialSnake` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = SpecialSnake
        fields = ('name', 'images', 'info')


class ReminderSerializer(ModelSerializer):
    """A class providing (de-)serialization of `Reminder` instances."""

    author = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = Reminder
        fields = ('active', 'author', 'channel_id', 'content', 'expiration', 'id')


class RoleSerializer(ModelSerializer):
    """A class providing (de-)serialization of `Role` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = Role
        fields = ('id', 'name', 'colour', 'permissions')


class TagSerializer(ModelSerializer):
    """A class providing (de-)serialization of `Tag` instances."""

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = Tag
        fields = ('title', 'embed')


class UserSerializer(BulkSerializerMixin, ModelSerializer):
    """A class providing (de-)serialization of `User` instances."""

    roles = PrimaryKeyRelatedField(many=True, queryset=Role.objects.all(), required=False)

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = User
        fields = ('id', 'avatar_hash', 'name', 'discriminator', 'roles', 'in_guild')
        depth = 1


class NominationSerializer(ModelSerializer):
    """A class providing (de-)serialization of `Nomination` instances."""

    actor = PrimaryKeyRelatedField(queryset=User.objects.all())
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata defined for the Django REST Framework."""

        model = Nomination
        fields = (
            'id', 'active', 'actor', 'reason', 'user',
            'inserted_at', 'unnominate_reason', 'unwatched_at')
        depth = 1

    def validate(self, attrs):
        active = attrs.get("active")

        unnominate_reason = attrs.get("unnominate_reason")
        if active and unnominate_reason:
            raise ValidationError(
                {'unnominate_reason': "An active nomination can't have an unnominate reason"}
            )
        return attrs
