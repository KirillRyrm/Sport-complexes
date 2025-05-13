from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from training_app.models import Trainers
from .models import Client, ClientSubscription
from .forms import ClientForm, BalanceTopUpForm, PurchaseSubscriptionForm
from auth_app.models import UserCredentials
from django.db import IntegrityError, transaction
import logging
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

@login_required
@permission_required(('auth_app.view_clients', 'auth_app.change_clients'), raise_exception=True)
def client_profile(request):
    try:
        # Отримуємо профіль клієнта
        client = Client.objects.get(user_credential=request.user)

        # Перевіряємо роль
        if request.user.user_role != 'client':
            logger.warning(f"User {request.user.username} (role: {request.user.user_role}) attempted to access client profile")
            messages.error(request, 'Доступ до профілю клієнта дозволено лише клієнтам.')
            return redirect('home')

        # Ініціалізація форм
        client_form = ClientForm(instance=client)
        balance_form = BalanceTopUpForm()

        # Обробка POST-запитів
        if request.method == 'POST':
            if 'update_profile' in request.POST:
                # Оновлення профілю
                client_form = ClientForm(request.POST, instance=client)
                if client_form.is_valid():
                    try:
                        client_form.save()
                        logger.info(f"User {request.user.username} updated client profile: {client.user_id}")
                        messages.success(request, 'Профіль успішно оновлено.')
                        return redirect('client_profile')
                    except IntegrityError:
                        logger.warning(f"User {request.user.username} failed to update profile due to unique constraint")
                        messages.error(request, 'Помилка: email або телефон уже використовуються.')
            elif 'top_up_balance' in request.POST:
                # Поповнення балансу
                balance_form = BalanceTopUpForm(request.POST)
                if balance_form.is_valid():
                    amount = balance_form.cleaned_data['amount']
                    try:
                        client.balance += amount
                        client.save()
                        logger.info(f"User {request.user.username} topped up balance by {amount} for client: {client.user_id}")
                        messages.success(request, f'Баланс поповнено на {amount} грн.')
                        return redirect('client_profile')
                    except Exception as e:
                        logger.error(f"Error topping up balance for user {request.user.username}: {str(e)}")
                        messages.error(request, 'Помилка при поповненні балансу.')
                else:
                    logger.warning(f"User {request.user.username} submitted invalid balance top-up data")
                    messages.error(request, 'Помилка: введіть коректну суму.')

        # Логуємо успішний перегляд
        logger.info(f"User {request.user.username} viewed client profile: {client.user_id}")

        context = {
            'client': client,
            'trainer': client.trainer if client.trainer else None,
            'client_form': client_form,
            'balance_form': balance_form,
        }
        return render(request, 'clients/client_profile.html', context)

    except Client.DoesNotExist:
        #messages.error(request, 'Профіль клієнта не знайдено. Зверніться до адміністратора.')
        return redirect('create_profile')
    except Exception as e:
        logger.error(f"Error viewing client profile for user {request.user.username}: {str(e)}")
        messages.error(request, 'Сталася помилка при завантаженні профілю.')
        return redirect('home')


@login_required
@permission_required('auth_app.change_clients', raise_exception=True)
def create_profile(request):
    try:
        # Перевіряємо, чи профіль уже існує
        if Client.objects.filter(user_credential=request.user).exists():
            logger.info(f"User {request.user.username} already has a client profile, redirecting to client_profile")
            messages.info(request, 'Ваш профіль уже створено.')
            return redirect('client_profile')

        # Перевіряємо роль
        if request.user.user_role != 'client':
            logger.warning(f"User {request.user.username} (role: {request.user.user_role}) attempted to create client profile")
            messages.error(request, 'Створення профілю дозволено лише клієнтам.')
            return redirect('home')

        if request.method == 'POST':
            form = ClientForm(request.POST)
            if form.is_valid():
                try:
                    client = form.save(commit=False)
                    client.user_credential = request.user
                    client.save()
                    logger.info(f"User {request.user.username} created client profile: {client.user_id}")
                    messages.success(request, 'Профіль успішно створено!')
                    return redirect('client_profile')
                except IntegrityError:
                    logger.warning(f"User {request.user.username} failed to create profile due to unique constraint")
                    messages.error(request, 'Помилка: email або телефон уже використовуються.')
                except Exception as e:
                    logger.error(f"Error creating client profile for user {request.user.username}: {str(e)}")
                    messages.error(request, 'Сталася помилка при створенні профілю.')
            else:
                logger.warning(f"User {request.user.username} submitted invalid form data")
                messages.error(request, 'Помилка: перевірте правильність даних.')
        else:
            form = ClientForm()

        context = {
            'form': form,
        }
        return render(request, 'clients/create_profile.html', context)

    except Exception as e:
        logger.error(f"Error accessing create profile for user {request.user.username}: {str(e)}")
        messages.error(request, 'Сталася помилка при завантаженні сторінки.')
        return redirect('home')

@login_required
@permission_required('auth_app.view_clients', raise_exception=True)
def clients_list(request):
    try:
        clients_data = []

        if request.user.user_role == 'trainer':
            try:
                trainer = Trainers.objects.get(user_credential=request.user)
                clients = Client.objects.filter(trainer=trainer)
                # Для тренеров показываем только клиентов с профилем Client
                for client in clients:
                    clients_data.append({
                        'user': client.user_credential,
                        'client': client
                    })
                logger.info(f"Trainer {request.user.username} viewed their clients list")
            except Trainers.DoesNotExist:
                logger.warning(f"User {request.user.username} has no trainer profile")
                messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
                return redirect('home')
        elif request.user.user_role == 'admin':
            # Для админов показываем всех пользователей с user_role='client'
            users = UserCredentials.objects.filter(user_role='client')
            for user in users:
                client = Client.objects.filter(user_credential=user).first()
                clients_data.append({
                    'user': user,
                    'client': client
                })
            logger.info(f"Admin {request.user.username} viewed all clients list")
        else:
            logger.warning(
                f"User {request.user.username} (role: {request.user.user_role}) attempted to access clients list")
            messages.error(request, 'Доступ до списку клієнтів дозволено лише тренерам або адміністраторам.')
            return redirect('home')

        context = {
            'clients_data': clients_data,
            'user_role': request.user.user_role,
        }
        return render(request, 'clients/clients_list.html', context)

    except Exception as e:
        logger.error(f"Error viewing clients list for user {request.user.username}: {str(e)}")
        messages.error(request, 'Сталася помилка при завантаженні списку клієнтів.')
        return redirect('home')



@login_required
@permission_required('auth_app.delete_clients', raise_exception=True)
def delete_client(request, user_id):
    try:
        # Перевіряємо роль
        if request.user.user_role != 'admin':
            logger.warning(f"User {request.user.username} (role: {request.user.user_role}) attempted to delete client {user_id}")
            messages.error(request, 'Видалення клієнтів дозволено лише адміністраторам.')
            return redirect('clients_list')

        if request.method == 'POST':
            try:
                user = UserCredentials.objects.get(user_credential_id=user_id)
                # Проверяем наличие профиля Client для получения имени
                try:
                    client_info = Client.objects.get(user_credential=user)
                    client_name = f"{client_info.first_name} {client_info.last_name}"
                except Client.DoesNotExist:
                    client_name = user.username  # Используем username, если нет профиля Client

                user.delete()  # Видаляє UserCredentials і пов'язаний Client через CASCADE
                logger.info(f"Admin {request.user.username} deleted client: {user_id} ({client_name})")
                messages.success(request, f'Клієнт {client_name} успішно видалений.')
                return redirect('clients_list')
            except UserCredentials.DoesNotExist:
                logger.warning(f"User {user_id} not found for deletion by user {request.user.username}")
                messages.error(request, 'Клієнт не знайдений.')
                return redirect('clients_list')
        else:
            logger.warning(f"Invalid request method for delete_client by user {request.user.username}")
            messages.error(request, 'Невалідний запит для видалення.')
            return redirect('clients_list')

    except Exception as e:
        logger.error(f"Error deleting client {user_id} by user {request.user.username}: {str(e)}")
        messages.error(request, 'Сталася помилка при видаленні клієнта.')
        return redirect('clients_list')


### client_subscriptions ###
@login_required
@permission_required('auth_app.view_client_subscriptions', raise_exception=True)
def client_subscriptions_list(request):
    try:
        subscriptions = []

        if request.user.user_role == 'client':
            try:
                client = Client.objects.get(user_credential=request.user)
                subscriptions = ClientSubscription.objects.filter(user=client).select_related('user', 'subscription')
                logger.info(f"Client {request.user.username} viewed their subscriptions list")
            except Client.DoesNotExist:
                logger.warning(f"User {request.user.username} has no client profile")
                messages.error(request, 'Профіль клієнта не знайдено. Створіть профіль.')
                return redirect('create_profile')
        elif request.user.user_role == 'trainer':
            try:
                trainer = Trainers.objects.get(user_credential=request.user)
                subscriptions = ClientSubscription.objects.filter(user__trainer=trainer).select_related('user', 'subscription')
                logger.info(f"Trainer {request.user.username} viewed their clients' subscriptions list")
            except Trainers.DoesNotExist:
                logger.warning(f"User {request.user.username} has no trainer profile")
                messages.error(request, 'Профіль тренера не знайдено. Зверніться до адміністратора.')
                return redirect('home')
        elif request.user.user_role == 'admin':
            subscriptions = ClientSubscription.objects.all().select_related('user', 'subscription')
            logger.info(f"Admin {request.user.username} viewed all client subscriptions list")
        else:
            logger.warning(
                f"User {request.user.username} (role: {request.user.user_role}) attempted to access client subscriptions list")
            messages.error(request, 'Доступ до списку абонементів не дозволено.')
            return redirect('home')

        context = {
            'subscriptions': subscriptions,
            'user_role': request.user.user_role,
        }
        return render(request, 'client_subscriptions/client_subscriptions_list.html', context)

    except Exception as e:
        logger.error(f"Error viewing client subscriptions list for user {request.user.username}: {str(e)}")
        messages.error(request, 'Сталася помилка при завантаженні списку абонементів.')
        return redirect('home')


@login_required
@permission_required('auth_app.add_client_subscriptions', raise_exception=True)
def purchase_subscription(request):
    try:
        if request.user.user_role != 'client':
            logger.warning(f"User {request.user.username} (role: {request.user.user_role}) attempted to purchase subscription")
            messages.error(request, 'Покупка абонемента дозволена лише клієнтам.')
            return redirect('home')
        try:
            client = Client.objects.get(user_credential=request.user)
        except Client.DoesNotExist:
            logger.warning(f"User {request.user.username} has no client profile")
            messages.error(request, 'Профіль клієнта не знайдено. Створіть профіль.')
            return redirect('create_profile')
        if request.method == 'POST':
            form = PurchaseSubscriptionForm(request.POST)
            if form.is_valid():
                subscription = form.cleaned_data['subscription']
                try:
                    with transaction.atomic():
                        if client.balance < subscription.price:
                            logger.warning(f"User {request.user.username} has insufficient balance for subscription {subscription.subscription_id}")
                            messages.error(request, 'Недостатньо коштів на балансі.')
                            return redirect('client_profile')
                        start_date = datetime.now()
                        end_date = start_date + timedelta(days=subscription.duration_days)
                        client_subscription = ClientSubscription(
                            user=client,
                            subscription=subscription,
                            start_date=start_date,
                            end_date=end_date
                        )
                        client_subscription.clean()
                        client_subscription.save()
                        client.balance -= subscription.price
                        client.save()
                        logger.info(f"User {request.user.username} purchased subscription {subscription.subscription_id} for client {client.user_id}")
                        messages.success(request, f'Абонемент "{subscription.subscription_name}" успішно придбано!')
                        return redirect('client_subscriptions_list')
                except ValidationError as e:
                    logger.warning(f"Validation error for user {request.user.username} purchasing subscription: {str(e)}")
                    messages.error(request, f'Помилка: {str(e)}')
                except Exception as e:
                    logger.error(f"Error purchasing subscription for user {request.user.username}: {str(e)}")
                    messages.error(request, 'Сталася помилка при покупці абонемента.')
            else:
                logger.warning(f"User {request.user.username} submitted invalid subscription purchase form")
                messages.error(request, 'Помилка: виберіть коректний абонемент.')
        else:
            form = PurchaseSubscriptionForm()
        context = {
            'form': form,
            'client': client,
        }
        return render(request, 'client_subscriptions/purchase_subscription.html', context)
    except Exception as e:
        logger.error(f"Error accessing purchase subscription for user {request.user.username}: {str(e)}")
        messages.error(request, 'Сталася помилка при завантаженні сторінки покупки.')
        return redirect('home')


@login_required
@permission_required('auth_app.delete_client_subscriptions', raise_exception=True)
def delete_subscription(request, user_subscription_id):
    try:
        if request.method == 'POST':
            try:
                subscription = ClientSubscription.objects.get(user_subscription_id=user_subscription_id)
                subscription_name = subscription.subscription.subscription_name
                client_name = f"{subscription.user.first_name} {subscription.user.last_name}"
                subscription.delete()
                messages.success(request, f'Абонемент "{subscription_name}" для клієнта {client_name} успішно видалено.')
                return redirect('client_subscriptions_list')
            except ClientSubscription.DoesNotExist:
                messages.error(request, 'Абонемент не знайдено.')
                return redirect('client_subscriptions_list')
        else:
            messages.error(request, 'Невалідний запит для видалення.')
            return redirect('client_subscriptions_list')
    except Exception as e:
        messages.error(request, 'Сталася помилка при видаленні абонемента.')
        return redirect('client_subscriptions_list')


### client_goals ###
