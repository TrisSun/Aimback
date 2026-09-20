from django.conf import settings

from apps.ai import constants
from apps.ai.providers.dashscope import DashscopeProvider
from apps.ai.providers.fake import FakeProvider


def get_provider():
    name = getattr(settings, "AI_EMBEDDING_PROVIDER", constants.PROVIDER_DASHSCOPE)
    if name == constants.PROVIDER_FAKE:
        return FakeProvider()
    return DashscopeProvider()
