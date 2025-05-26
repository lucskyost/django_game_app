from django.shortcuts import render, HttpResponse
from .forms import PlayerForm
from .models import GameMatrix, GameHistory
import random

# Create your views here.
def index(request):
    game_code = str(random.randint(111111,999999))
    player_form = PlayerForm(initial={'game_code': game_code})
    try:
        history = GameHistory.objects.using('history_db').all().order_by('-created_at')[:5]
    except (OperationalError, MySQLdb._exceptions.OperationalError):
        history = []
    return render(request, 'game/index.html', {'player_form': player_form, 'history': history})

def game(request):
    game_matrix, created = GameMatrix.objects.get_or_create(game_code=request.POST.get('game_code'))
    game_matrix_id = game_matrix.id
    if request.method == 'POST':
        data = {
            'player_name': request.POST.get('player_name'),
            'game_code': request.POST.get('game_code'),
            'i_have_game_code': request.POST.get('i_have_game_code'),
            'game_matrix_id': game_matrix_id,
        }
        return render(request, 'game/game.html', data)
    else:
        return HttpResponse('<h1>Bad Request...</h1>')