from .models import Umbrellas

def borrowed_umbrella(request):
    if request.user.is_authenticated:
        umbrella = Umbrellas.objects.filter(borrower=request.user).first()
        if umbrella:
            request.user.borrowed_umbrella = umbrella
        return {"borrowed_umbrella": umbrella}
    return {"borrowed_umbrella": None}