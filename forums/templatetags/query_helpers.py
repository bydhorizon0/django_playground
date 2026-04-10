from typing import Any

from django import template
from django.http import HttpRequest

register = template.Library()


@register.simple_tag
def replace_query_param(request: HttpRequest, field: str, value: Any):
    # 현재 request의 GET 파라미터를 복사
    updated_params = request.GET.copy()
    # 원하는 필드만 교체
    updated_params[field] = value
    # 다시 쿼리 스트링으로 변환 (?a=1&b=2...)
    return updated_params.urlencode()
