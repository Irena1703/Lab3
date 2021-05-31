from .models import Link
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class LinkSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    class Meta:
        model = Link
        fields = ['url', 'created_at', 'origin_link', 'zipped_link', 'user', 'counter']
        extra_kwargs = {'zipped_link': {'required': False, 'read_only': True},
                        'created_at': {'read_only' : True}, 'counter': {'read_only' : True}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['zipped_link'] = "{0}://{1}/{2}/".format(self.context['request'].scheme, \
            self.context['request'].get_host(), ret['zipped_link'])
        return ret

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']