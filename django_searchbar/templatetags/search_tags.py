
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from people.models import Friendship

register = template.Library()


@register.filter(name='connection')
def connection(person, mate):
    try:
        friendship = Friendship.objects.get(from_person=person, to_person=mate)
        direction = 'left'
    except ObjectDoesNotExist:
        try:
            friendship = Friendship.objects.get(from_person=mate, to_person=person)
            direction = 'right'
        except ObjectDoesNotExist:
            return False

    return ({
        Friendship.APROVED: 'approved',
        Friendship.PENDING: 'pending',
        Friendship.BLOCKED: 'blocked',
    }.get(friendship.status), direction, friendship.approval_date or friendship.request_date or None)


@register.filter(name='requested_friendship')
def requested_friendship(person, mate):
    return person.requested_friendship(mate)


@register.filter(name='friendship_aproved')
def friendship_aproved(person, mate):
    return person.friendship_aproved(mate)


@register.filter
def in_loop(mate, person):
    return person.in_loop(mate)


class AssignFriendsToNode(template.Node):

    def __init__(self, obj, context_var_name):
        self.obj = template.Variable(obj)
        self.context_var_name = context_var_name

    def render(self, context):
        actor = self.obj.resolve(context)
        context[self.context_var_name] = Friendship.objects.filter(Q(to_person=actor) | Q(from_person=actor)).filter(status=Friendship.APROVED)
        return ''


@register.tag
def get_friends(parser, token):
    """
    Assigns the friends of the actor to a variable in the context
    {% get_friends actor as friend_list %}
    """
    try:
        bits = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('This tag requires arguments')

    if len(bits) != 4:
        raise template.TemplateSyntaxError('This tag requires exactly three arguments')
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("Second argument to tag must be 'as'")

    return AssignFriendsToNode(bits[1], bits[3])
