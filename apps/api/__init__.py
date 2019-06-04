from django.contrib.auth import authenticate

def check_user(request):
    user = request.GET.get('user')
    token = request.GET.get('token')
    if user and token:
        user = authenticate(pk=user, token=token)
    else:
        user = None

    return user