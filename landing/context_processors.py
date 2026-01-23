from django.conf import settings


def analytics(request):
    """Context processor para disponibilizar Google Analytics ID nos templates"""
    return {
        'GA4_MEASUREMENT_ID': settings.GA4_MEASUREMENT_ID,
    }
