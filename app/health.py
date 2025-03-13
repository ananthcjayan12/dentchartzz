from django.http import JsonResponse

def health_check(request):
    """
    Health check endpoint to ensure the application is running properly.
    This endpoint doesn't require authentication.
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'DentChartzz is up and running!'
    }) 