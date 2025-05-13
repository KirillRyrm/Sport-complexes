# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import TrainingType, Trainers, TrainingSessions
from .forms import TrainingTypeForm, TrainerForm, TrainingSessionForm
from gym_app.models import Gym, GymLocation
from django.db import IntegrityError, InternalError
import logging
import os
from django.utils import timezone
from datetime import datetime, timedelta, time
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from training_app.api.serializers import TrainingTypeSerializer, TrainersSerializer, TrainingSessionsSerializer

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

@login_required
@permission_required('auth_app.view_trainers', raise_exception=True)
def trainers_list(request):
    trainers = Trainers.objects.all()
    return render(request, 'trainers/trainers_list.html', {
        'trainers': trainers,
        'is_admin': request.user.user_role == 'admin'
    })


@login_required
@permission_required('auth_app.delete_trainers', raise_exception=True)
def delete_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainers, trainer_id=trainer_id)
    if request.method == 'POST':
        try:
            # Зберігаємо дані для логування та повідомлення
            full_name = f"{trainer.first_name} {trainer.last_name}"
            photo_path = trainer.photo.path if trainer.photo else None

            # Видаляємо тренера
            trainer.delete()

            # Видаляємо фото з медіа, якщо воно існує
            if photo_path and os.path.exists(photo_path):
                os.remove(photo_path)

            messages.success(request, f'Тренера "{full_name}" успішно видалено.')
        except Exception as e:
            messages.error(request, f'Помилка при видаленні тренера "{full_name}".')
        return redirect('trainers_list')
    return redirect('trainers_list')


@login_required
@permission_required('auth_app.view_training_sessions', raise_exception=True)
def training_sessions(request):
    try:
        trainer = Trainers.objects.get(user_credential=request.user)
        sessions = TrainingSessions.objects.filter(trainer=trainer).order_by('session_date', 'start_time')

        current_time = timezone.now()

        # Проходим по каждой сессии и проверяем время её завершения
        for session in sessions:

            #session_start = datetime.combine(session.session_date, session.start_time)
            session_end = datetime.combine(session.session_date, session.end_time)



            # Если сессия завершилась, но статус ещё не установлен как 'завершено'
            if session_end < current_time and session.status != 'завершено':
                session.status = 'завершено'
                session.save(update_fields=['status'])
        return render(request, 'training_sessions/training_sessions_list.html', {
            'sessions': sessions,
            'trainer': trainer
        })
    except Trainers.DoesNotExist:
        messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
        return redirect('home')


@login_required
@permission_required('auth_app.add_training_sessions', raise_exception=True)
def add_training_session(request):
    try:
        trainer = Trainers.objects.get(user_credential=request.user)
    except Trainers.DoesNotExist:
        logger.error(f"User {request.user.username} (role: {request.user.user_role}) attempted to add training session but no matching Trainers record found.")
        messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
        return redirect('home')

    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)
        if form.is_valid():
            try:
                session = form.save(commit=False)
                session.trainer = trainer
                session.save()
                messages.success(request, 'Тренувальну сесію успішно додано.')
                logger.info(f"User {request.user.username} added training session: {session.session_id} on {session.session_date}")
                return redirect('training_sessions')

            except IntegrityError as e:
                logger.error(f"User {request.user.username} failed to add training session: {str(e)}")
                messages.error(request, 'Помилка: сесія на цей час для цього тренера вже існує.')

            except InternalError as e:
                logger.error(
                    f"User {request.user.username} failed to add training session due to InternalError: {str(e)}")
                if 'зайнятий у цей час' in str(e):
                    messages.error(request, f'Помилка: Ви вже маєте заняття у цей час.')
                elif 'уже має заняття на іншій локації' in str(e):
                    messages.error(request, f'Помилка: Ви вже маєте заняття у іншій локації в цей день.')
                else:
                    messages.error(request, 'Сталася внутрішня помилка бази даних. Зверніться до адміністратора.')

        else:
            logger.warning(f"User {request.user.username} failed to add training session: {form.errors}")
    else:
        form = TrainingSessionForm()


    gyms = Gym.objects.all()
    gym_locations = {
        gym.gym_id: [
            {'location_id': loc.location_id, 'location_name': loc.location_name}
            for loc in GymLocation.objects.filter(gym=gym)
        ]
        for gym in gyms
    }
    return render(request, 'training_sessions/add_training_session.html', {
        'form': form,
        'trainer': trainer,
        'gyms': gyms,
        'gym_locations': gym_locations
    })


@login_required
@permission_required('auth_app.change_training_sessions', raise_exception=True)
def edit_training_session(request, session_id):
    try:
        trainer = Trainers.objects.get(user_credential=request.user)
    except Trainers.DoesNotExist:
        logger.error(f"User {request.user.username} (role: {request.user.user_role}) attempted to edit training session but no matching Trainers record found.")
        messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
        return redirect('home')

    session = get_object_or_404(TrainingSessions, session_id=session_id, trainer=trainer)

    if request.method == 'POST':
        form = TrainingSessionForm(request.POST, instance=session)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Тренувальну сесію успішно оновлено.')
                logger.info(f"User {request.user.username} updated training session: {session.session_id} on {session.session_date}")
                return redirect('training_sessions')
            except IntegrityError as e:
                logger.error(f"User {request.user.username} failed to update training session: {str(e)}")
                messages.error(request, 'Помилка: сесія на цей час для цього тренера вже існує.')
        else:
            logger.warning(f"User {request.user.username} failed to update training session: {form.errors}")
    else:
        form = TrainingSessionForm(instance=session)

    gyms = Gym.objects.all()
    gym_locations = {
        gym.gym_id: [
            {'location_id': loc.location_id, 'location_name': loc.location_name}
            for loc in GymLocation.objects.filter(gym=gym)
        ]
        for gym in gyms
    }
    return render(request, 'training_sessions/edit_training_session.html', {
        'form': form,
        'trainer': trainer,
        'gyms': gyms,
        'gym_locations': gym_locations,
        'session': session
    })

@login_required
@permission_required('auth_app.delete_training_sessions', raise_exception=True)
def delete_training_session(request, session_id):
    try:
        trainer = Trainers.objects.get(user_credential=request.user)
    except Trainers.DoesNotExist:
        logger.error(f"User {request.user.username} (role: {request.user.user_role}) attempted to delete training session but no matching Trainers record found.")
        messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
        return redirect('home')

    session = get_object_or_404(TrainingSessions, session_id=session_id, trainer=trainer)

    if request.method == 'POST':
        session_date = session.session_date
        session.delete()
        messages.success(request, 'Тренувальну сесію успішно видалено.')
        logger.info(f"User {request.user.username} deleted training session: {session_id} on {session_date}")
        return redirect('training_sessions')

    return redirect('training_sessions')

### api requests ###
# @login_required
# @permission_required('training_app.view_training_sessions', raise_exception=True)
# def training_sessions_api(request):
#     try:
#         trainer = Trainers.objects.get(user_credential=request.user)
#
#         api_url = "127.0.0.1:8000/api/locations/"
#         response = requests.get(api_url)
#
#         locations = []
#         if response.status_code == 200:
#             locations = response.json()
#         else:
#             messages.error(request, 'Не вдалося отримати список локацій. Спробуйте пізніше.')
#
#         # Фільтрація сесій
#         location_id = request.GET.get('location_id')
#         sessions = TrainingSessions.objects.filter(trainer=trainer)
#         if location_id:
#             try:
#                 sessions = sessions.filter(location_id=int(location_id))
#             except ValueError:
#                 messages.error(request, 'Невалідний ідентифікатор локації.')
#
#         sessions = sessions.order_by('session_date', 'start_time')
#
#         return render(request, 'training_app/training_sessions_list.html', {
#             'sessions': sessions,
#             'trainer': trainer,
#             'locations': locations
#         })
#     except Trainers.DoesNotExist:
#         messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
#         return redirect('home')

