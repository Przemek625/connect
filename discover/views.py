from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django_gravatar.helpers import get_gravatar_url, has_gravatar

from .forms import FilterMemberForm
from accounts.models import UserSkill


User = get_user_model()


@login_required
def dashboard(request):
    """
    Shows all members as a list - with the capacity to filter by
    member skills and roles.
    """
    # Get additional profile data
    user = request.user

    working_offline = False
    # working_offline = True

    if not working_offline:
        user.gravatar_exists = has_gravatar(user.email)

    # Display members
    listed_users = User.objects.filter(
        is_active=True
    ).order_by(
        'first_name'
    ).prefetch_related(
        'userskill_set',
        'userskill_set__skill',
        'roles',
        'link',
    )

    if request.method == 'GET':
        form = FilterMemberForm(request.GET)
        if form.is_valid():
            skills = form.cleaned_data['selected_skills']
            roles = form.cleaned_data['selected_roles']

            if skills:
                listed_users = listed_users.filter(
                    skill__in=skills
                ).distinct()
            if roles:
                listed_users = listed_users.filter(
                    roles__in=roles
                ).distinct()
    else:
        form = FilterMemberForm()

    context = {
        'user' : user,
        'listed_users': listed_users,
        'form': form,
    }

    return render(request, 'discover/list.html', context)


@login_required
def map(request):
    """
    Shows all members on a world map.
    """
    return render(request, 'discover/map.html')


