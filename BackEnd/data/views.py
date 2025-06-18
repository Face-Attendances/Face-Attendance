from django.http import JsonResponse

def index(request):
    """
    Trang chủ tạm thời cho app data.
    """
    return JsonResponse({'message': 'Data app is up and running!'})
