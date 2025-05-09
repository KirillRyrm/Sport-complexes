from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Gym, Equipment
from .forms import GymForm, EquipmentForm
from django.db import IntegrityError

# Create your views here.


@login_required
@permission_required('auth_app.view_gyms', raise_exception=True)
def gym_list(request):
    gyms = Gym.objects.all()
    return render(request, 'gym_app/gym_list.html', {'gyms': gyms})


@login_required
@permission_required('auth_app.add_gyms', raise_exception=True)
def add_gym(request):
    if request.method == 'POST':
        form = GymForm(request.POST)
        if form.is_valid():
            Gym.objects.create(
                gym_name=form.cleaned_data['gym_name'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
            )
            messages.success(request, 'Спортивний зал успішно додано.')
            #logger.info(f"User {request.user.username} added gym: {form.cleaned_data['gym_name']}")
            return redirect('gym_list')
    else:
        form = GymForm()
    return render(request, 'gym_app/add_gym.html', {'form': form})

@login_required
@permission_required('auth_app.change_gyms', raise_exception=True)
def edit_gym(request, gym_id):
    gym = get_object_or_404(Gym, gym_id=gym_id)
    if request.method == 'POST':
        form = GymForm(request.POST, instance=gym)
        if form.is_valid():
            form.save()
            messages.success(request, 'Інформацію про зал успішно оновлено.')
           # logger.info(f"User {request.user.username} updated gym: {gym.gym_name}")
            return redirect('gym_list')
    else:
        form = GymForm(instance=gym)
    return render(request, 'gym_app/edit_gym.html', {'form': form, 'gym': gym})

@login_required
@permission_required('auth_app.delete_gyms', raise_exception=True)
def delete_gym(request, gym_id):
    gym = get_object_or_404(Gym, gym_id=gym_id)
    if request.method == 'POST':
        gym_name = gym.gym_name
        gym.delete()
        messages.success(request, f'Спортивний зал "{gym_name}" успішно видалено.')
        #logger.info(f"User {request.user.username} deleted gym: {gym_name}")
        return redirect('gym_list')
    return redirect('gym_list')



class GymListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gyms = Gym.objects.all().values('gym_id', 'gym_name', 'address', 'phone', 'email')
        #logger.debug(f"API accessed by user: {request.user.username}")
        return Response(list(gyms))


################### equipment #####################

@login_required
@permission_required('auth_app.view_equipment', raise_exception=True)
def equipment_list(request):
    equipment = Equipment.objects.all()
    return render(request, 'equipment/equipment_list.html', {'equipment': equipment})

@login_required
@permission_required('auth_app.add_equipment', raise_exception=True)
def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            try:
                equipment = Equipment.objects.create(
                    equipment_name=form.cleaned_data['equipment_name'],
                    description=form.cleaned_data['description']
                )
                messages.success(request, 'Обладнання успішно додано.')
                return redirect('equipment_list')
            except IntegrityError as e:
                messages.error(request, 'Помилка: не вдалося додати обладнання. Перевірте унікальність назви.')
    else:
        form = EquipmentForm()
    return render(request, 'equipment/add_equipment.html', {'form': form})

@login_required
@permission_required('auth_app.change_equipment', raise_exception=True)
def edit_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, equipment_id=equipment_id)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Інформацію про обладнання успішно оновлено.')
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'equipment/edit_equipment.html', {'form': form, 'equipment': equipment})

@login_required
@permission_required('auth_app.delete_equipment', raise_exception=True)
def delete_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, equipment_id=equipment_id)
    if request.method == 'POST':
        equipment_name = equipment.equipment_name
        equipment.delete()
        messages.success(request, f'Обладнання "{equipment_name}" успішно видалено.')
        return redirect('equipment_list')
    return redirect('equipment_list')


class EquipmentListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.has_perm('auth_app.view_equipment'):
            return Response({"error": "Permission denied"}, status=403)
        equipment = Equipment.objects.all().values('equipment_id', 'equipment_name', 'description')
        return Response(list(equipment))