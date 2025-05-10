from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import TrainingType, Trainers
from .forms import TrainingTypeForm, TrainerForm
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

### training type ####

@login_required
@permission_required('auth_app.view_training_type', raise_exception=True)
def training_type_list(request):
    training_types = TrainingType.objects.all()
    return render(request, 'training_type/training_type_list.html', {'training_types': training_types})

@login_required
@permission_required('auth_app.add_training_type', raise_exception=True)
def add_training_type(request):
    if request.method == 'POST':
        form = TrainingTypeForm(request.POST)
        if form.is_valid():
            try:
                training_type = TrainingType.objects.create(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description']
                )
                messages.success(request, 'Тип тренування успішно додано.')
                return redirect('training_type_list')
            except IntegrityError as e:
                messages.error(request, 'Помилка: не вдалося додати тип тренування. Перевірте унікальність назви.')
    else:
        form = TrainingTypeForm()
    return render(request, 'training_type/add_training_type.html', {'form': form})

@login_required
@permission_required('auth_app.change_training_type', raise_exception=True)
def edit_training_type(request, training_type_id):
    training_type = get_object_or_404(TrainingType, training_type_id=training_type_id)
    if request.method == 'POST':
        form = TrainingTypeForm(request.POST, instance=training_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Інформацію про тип тренування успішно оновлено.')
            return redirect('training_type_list')
    else:
        form = TrainingTypeForm(instance=training_type)
    return render(request, 'training_type/edit_training_type.html', {'form': form, 'training_type': training_type})

@login_required
@permission_required('auth_app.delete_training_type', raise_exception=True)
def delete_training_type(request, training_type_id):
    training_type = get_object_or_404(TrainingType, training_type_id=training_type_id)
    if request.method == 'POST':
        title = training_type.title
        training_type.delete()
        messages.success(request, f'Тип тренування "{title}" успішно видалено.')
        return redirect('training_type_list')
    return redirect('training_type_list')


### trainers ###
@login_required
def trainer_profile(request):
    try:
        trainer = Trainers.objects.get(user_credential=request.user)
    except Trainers.DoesNotExist:
        messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
        return redirect('home')

    if request.user.user_role != 'trainer':
        messages.error(request, 'Доступ до профілю тренера дозволено лише тренерам.')
        return redirect('home')

    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Профіль успішно оновлено.')
                return redirect('trainer_profile')
            except IntegrityError as e:
                messages.error(request, 'Помилка: не вдалося оновити профіль. Перевірте унікальність телефону.')
    else:
        form = TrainerForm(instance=trainer)

    return render(request, 'trainers/trainer_profile.html', {
        'trainer': trainer,
        'form': form
    })

