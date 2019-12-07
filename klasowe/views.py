from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginView
from .forms import (
    AddClassForm,
    AddClassCodeForm,
    UsernameChangeForm,
    EmailChangeForm,
    NewEventForm,
    NewYearForm
)
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models.functions import Coalesce
from .models import (
    ClassCode,
    Year,
    Student,
    MonthPayment,
    Event,
    EventPayment
)
import json
import random
import datetime


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main-panel')
    return CustomLoginView.as_view(template_name="klasowe/login.html")(request)


def email_exists(request):
    if request.user.email:
        return True
    else:
        return False


@login_required
def email_change(request):
    if request.method == "POST":
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.warning(request, 'Ten adres email jest już przypisany do jakiegoś konta.')
                return redirect('email-change')
            else:
                User.objects.filter(id=request.user.id).update(email=email)
                messages.success(request, 'Zmiana adresu email przebiegła pomyślnie')
                return redirect('main-panel')
        else:
            messages.warning(request, 'Niepoprawny adres email.')
            return redirect('email-change')
    context = {
        'title': 'Zmiana emaila',
        'h1': 'Zmiana adresu email',
        'form': EmailChangeForm()
    }
    return render(request, 'klasowe/change-email.html', context)


@login_required
def password_changed(request):
    return Student.objects.get(user=request.user).pass_changed


@login_required
def password_change_done(request):
    Student.objects.filter(user_id=request.user.id).update(pass_changed=True)
    messages.success(request, 'Zmiana hasła przebiegła pomyślnie.')
    return redirect('main-panel')


@login_required
def username_change(request):
    if request.method == "POST":
        form = UsernameChangeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if not User.objects.filter(username=username).exists():
                User.objects.filter(id=request.user.id).update(username=username)
                messages.success(request, 'Zmiana nazwy użytkownika przebiegła pomyślnie.')
                return redirect('main-panel')
        else:
            messages.warning(request, 'Ta nazwa użytkownika jest już zajęta, lub używasz znaków specjalnych.')
            return redirect('username_change')

    context = {
        'title': 'Zmiana loginu',
        'h1': 'Zmiana nazwy użytkownika',
        'form': UsernameChangeForm
    }
    return render(request, 'klasowe/username-change.html', context)


@login_required
def main_panel(request):
    request.session['role'] = Student.objects.get(user__username=request.user).role_fk.name
    if not password_changed(request):
        return redirect('password_change')
    if not email_exists(request):
        return redirect('email-change')

    user_student = Student.objects.get(user__username=request.user)
    role = request.session['role']
    class_code_id = user_student.class_code_fk.id
    years = Year.objects.filter(class_code_fk_id=class_code_id).order_by('year')

    year_now = Year.objects.filter(class_code_fk_id=class_code_id).order_by(Coalesce('year', 'year').desc()).first().year
    if request.GET.get('year'):
        year_now = request.GET.get('year')

    user_payments = MonthPayment.objects.filter(student_fk_id=user_student.id, year_fk__year=year_now)

    if role == 'admin':
        if request.method == 'POST':
            MonthPayment.objects.filter(class_code_fk_id=class_code_id, year_fk__year=year_now).delete()
            for payment in request.POST:
                if payment != 'csrfmiddlewaretoken':
                    payment = payment.split('_')
                    year_now_id = Year.objects.get(year=year_now, class_code_fk_id=class_code_id).id
                    MonthPayment.objects.create(student_fk_id=payment[0], class_code_fk_id=class_code_id, month=payment[1], year_fk_id=year_now_id)

        students_payments = MonthPayment.objects.filter(class_code_fk_id=class_code_id, year_fk__year=year_now)
        students = Student.objects.filter(class_code_fk_id=class_code_id).order_by('user__last_name')
        context = {
            'title': 'Panel główny',
            'h1': 'Twoje płatności',
            'student': user_student,
            'user_payments': user_payments,
            'years': years,
            'year_choosed': year_now,
            'students_payments': students_payments,
            'students': students
        }
    else:
        context = {
            'title': 'Panel główny',
            'h1': 'Twoje płatności',
            'student': user_student,
            'user_payments': user_payments,
            'years': years,
            'year_choosed': year_now
        }
    return render(request, 'klasowe/main-panel.html', context)


@login_required
def event_create(request):
    if request.session['role'] == 'admin':
        user_student = Student.objects.get(user__username=request.user)
        class_code_id = user_student.class_code_fk.id

        if request.method == 'POST':
            name = request.POST['name']
            date = request.POST['date']
            value = request.POST['value']
            new_event = Event.objects.create(class_code_id=class_code_id, name=name, date=date, value=value)
            for student in request.POST:
                if student != 'name' and student != 'date' and student != 'value' and student != 'csrfmiddlewaretoken':
                    if Student.objects.get(id=student).class_code_fk.id == class_code_id:
                        EventPayment.objects.create(event_fk_id=new_event.id, student_fk_id=student, paid=False)
            messages.success(request, 'Pomyślnie utworzono wydarzenie.')
            return redirect('events-show')

        students = Student.objects.filter(class_code_fk_id=class_code_id).order_by('user__last_name')
        context = {
            'title': 'Nowe wydarzenie',
            'h1': 'Stwórz wydarzenie',
            'form': NewEventForm,
            'students': students
        }
        return render(request, 'klasowe/event-create.html', context)
    else:
        return redirect('main-panel')


def event_details(request):
    user_student = Student.objects.get(user__username=request.user)
    class_code_id = user_student.class_code_fk.id
    if request.method == 'POST' and request.session['role'] == 'admin':
        if Event.objects.filter(id=request.session['event_id'], class_code_id=class_code_id).exists():
            EventPayment.objects.filter(event_fk_id=request.session['event_id']).update(paid=False)
            for event_pay in request.POST:
                if event_pay != 'csrfmiddlewaretoken':
                    EventPayment.objects.filter(event_fk_id=request.session['event_id'], student_fk_id=event_pay).update(paid=True)
    if request.session['event_id']:
        event_id = request.session['event_id']
    if request.session['role'] == 'admin':
        payments = EventPayment.objects.filter(event_fk_id=event_id)
    else:
        payments = EventPayment.objects.filter(event_fk_id=event_id, student_fk_id=request.user.id)
    details = Event.objects.get(id=event_id)
    context = {
        'title': 'Szczegóły wydarzenia',
        'h1': 'Płatności wydarzenia',
        'event_payments': payments,
        'name': details.name,
        'date': details.date,
        'value': details.value
    }
    return render(request, 'klasowe/event-details.html', context)


@login_required
def event_delete(request, event):
    user_student = Student.objects.get(user__username=request.user)
    class_code_id = user_student.class_code_fk.id
    if Event.objects.filter(id=event, class_code_id=class_code_id).exists() and request.session['role'] == 'admin':
        Event.objects.filter(id=event).delete()
        messages.success(request, 'Pomyślnie usunięto wydarzenie.')
    else:
        messages.warning(request, 'Nie udało się usunąć wydarzenia.')
    return redirect('events-show')


@login_required
def events_show(request):
    user_student = Student.objects.get(user__username=request.user)
    class_code_id = user_student.class_code_fk.id
    if request.method == "POST":
        event_id = request.POST.get('event_id')
        request.session['event_id'] = event_id
        return redirect('event-details')
    if request.session['role'] == 'admin':
        events = Event.objects.filter(class_code_id=class_code_id).order_by('-date')
    else:
        user_in_payments = EventPayment.objects.filter(student_fk_id=request.user.id).order_by('-id')
        if user_in_payments:
            events = []
            for event in user_in_payments:
                events.append(Event.objects.get(id=event.event_fk.id))

    context = {
        'title': 'Wydarzenia',
        'h1': 'Wybierz wydarzenie',
        'events': events
    }
    return render(request, 'klasowe/events-show.html', context)


@login_required
def years_manage(request):
    if request.session['role'] == 'admin':
        user_student = Student.objects.get(user__username=request.user)
        class_code_id = user_student.class_code_fk.id
        if request.method == 'POST':
            year = request.POST.get('year')
            if Year.objects.filter(class_code_fk_id=class_code_id, year=year).exists():
                messages.warning(request, 'Ten rok już istnieje.')
                return redirect('years-manage')
            elif int(year) < 2000 or int(year) > 2099:
                messages.warning(request, 'Nieprawidłowa wartość.')
                return redirect('years-manage')
            else:
                Year.objects.create(year=year, class_code_fk_id=class_code_id)
                messages.success(request, 'Pomyślnie dodano rok.')
                return redirect('years-manage')
        years = Year.objects.filter(class_code_fk_id=class_code_id)
        context = {
            'title': 'Zarządzanie rokiem szkolnym',
            'h1': 'Lata szkolne',
            'form': NewYearForm(),
            'years': years
        }
        return render(request, 'klasowe/years-manage.html', context)
    else:
        redirect('main-panel')


@login_required
def year_delete(request, id):
    if request.session['role'] == 'admin':
        user_student = Student.objects.get(user__username=request.user)
        class_code_id = user_student.class_code_fk.id
        if Year.objects.filter(id=id, class_code_fk_id=class_code_id).exists() and Year.objects.filter(class_code_fk_id=class_code_id).exclude(id=id).exists():
            Year.objects.filter(id=id).delete()
            messages.success(request, 'Pomyślnie usunięto rok szkolny.')
            return redirect('years-manage')
        else:
            messages.warning(request, 'Nie udało się usunąć roku. Musi istnieć przynajmniej jeden rekord.')
            return redirect('years-manage')
    else:
        return redirect('main-panel')

# adding class start
def generate_password():
    chars = '0123456789abcdefghiklmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for i in range(6))


def remove_accents(text):
    strange = 'ŮôῡΒძěἊἦëĐᾇόἶἧзвŅῑἼźἓŉἐÿἈΌἢὶЁϋυŕŽŎŃğûλВὦėἜŤŨîᾪĝžἙâᾣÚκὔჯᾏᾢĠфĞὝŲŊŁČῐЙῤŌὭŏყἀхῦЧĎὍОуνἱῺèᾒῘᾘὨШūლἚύсÁóĒἍŷöὄЗὤἥბĔõὅῥŋБщἝξĢюᾫაπჟῸდΓÕűřἅгἰშΨńģὌΥÒᾬÏἴქὀῖὣᾙῶŠὟὁἵÖἕΕῨčᾈķЭτἻůᾕἫжΩᾶŇᾁἣჩαἄἹΖеУŹἃἠᾞåᾄГΠКíōĪὮϊὂᾱიżŦИὙἮὖÛĮἳφᾖἋΎΰῩŚἷРῈĲἁéὃσňİΙῠΚĸὛΪᾝᾯψÄᾭêὠÀღЫĩĈμΆᾌἨÑἑïოĵÃŒŸζჭᾼőΣŻçųøΤΑËņĭῙŘАдὗპŰἤცᾓήἯΐÎეὊὼΘЖᾜὢĚἩħĂыῳὧďТΗἺĬὰὡὬὫÇЩᾧñῢĻᾅÆßшδòÂчῌᾃΉᾑΦÍīМƒÜἒĴἿťᾴĶÊΊȘῃΟúχΔὋŴćŔῴῆЦЮΝΛῪŢὯнῬũãáἽĕᾗნᾳἆᾥйᾡὒსᾎĆрĀüСὕÅýფᾺῲšŵкἎἇὑЛვёἂΏθĘэᾋΧĉᾐĤὐὴιăąäὺÈФĺῇἘſგŜæῼῄĊἏØÉПяწДĿᾮἭĜХῂᾦωთĦлðὩზკίᾂᾆἪпἸиᾠώᾀŪāоÙἉἾρаđἌΞļÔβĖÝᾔĨНŀęᾤÓцЕĽŞὈÞუтΈέıàᾍἛśìŶŬȚĳῧῊᾟάεŖᾨᾉςΡმᾊᾸįᾚὥηᾛġÐὓłγľмþᾹἲἔбċῗჰხοἬŗŐἡὲῷῚΫŭᾩὸùᾷĹēრЯĄὉὪῒᾲΜᾰÌœĥტ'
    replacements = 'UoyBdeAieDaoiiZVNiIzeneyAOiiEyyrZONgulVoeETUiOgzEaoUkyjAoGFGYUNLCiIrOOoqaKyCDOOUniOeiIIOSulEySAoEAyooZoibEoornBSEkGYOapzOdGOuraGisPngOYOOIikoioIoSYoiOeEYcAkEtIuiIZOaNaicaaIZEUZaiIaaGPKioIOioaizTIYIyUIifiAYyYSiREIaeosnIIyKkYIIOpAOeoAgYiCmAAINeiojAOYzcAoSZcuoTAEniIRADypUitiiIiIeOoTZIoEIhAYoodTIIIaoOOCSonyKaAsSdoACIaIiFIiMfUeJItaKEISiOuxDOWcRoiTYNLYTONRuaaIeinaaoIoysACRAuSyAypAoswKAayLvEaOtEEAXciHyiiaaayEFliEsgSaOiCAOEPYtDKOIGKiootHLdOzkiaaIPIIooaUaOUAIrAdAKlObEYiINleoOTEKSOTuTEeiaAEsiYUTiyIIaeROAsRmAAiIoiIgDylglMtAieBcihkoIrOieoIYuOouaKerYAOOiaMaIoht'
    translator = str.maketrans(strange, replacements)
    return text.translate(translator)


def generate_login(name, surname):
    numbers = '0123456789'
    random_numbers = ''.join(random.choice(numbers) for i in range(4))
    login = remove_accents(name.lower()) + remove_accents(surname.lower()) + random_numbers
    return login


def validate_users(array):
    if array:
        new_arr = []
        for item in array:
            if item['name'] and item['surname']:
                name = item['name'].title()
                surname = item['surname'].title()
            else:
                return False
            if len(name) <= 30 and len(surname) <= 30 and not name.isnumeric() and not surname.isnumeric() and name.isalnum() and surname.isalnum():
                password = generate_password()
                login = generate_login(name, surname)
                temp_list = {
                    'name': name,
                    'surname': surname,
                    'login': login,
                    'password': password
                }
                new_arr.append(temp_list)
            else:
                return False
    else:
        return False
    return new_arr


def validate_classcode(classcode):
    if classcode:
        if len(classcode) <= 5 and not classcode.isnumeric() and classcode.isalnum():
            validated_classcode = remove_accents(classcode.lower())
            return validated_classcode
        else:
            return False


def add_class(request):
    if request.method == 'POST':
        users = json.loads(request.POST.get('objUsers'))
        class_code = request.POST.get('codeClass')
        validated_classcode = validate_classcode(class_code)
        validated_users = validate_users(users)
        if validated_classcode and validated_users:
            classcode = ClassCode.objects.create(code=validated_classcode)
            Year.objects.create(year=datetime.datetime.now().year, class_code_fk_id=classcode.id)
            admin = True
            for user in validated_users:
                user = User.objects.create_user(username=user['login'], first_name=user['name'], last_name=user['surname'], password=user['password'])
                if admin:
                    Student.objects.create(id=user.id, user=user, pass_changed=False, role_fk_id=2, class_code_fk_id=classcode.id)
                    admin = False
                else:
                    Student.objects.create(id=user.id, user=user, pass_changed=False, role_fk_id=1, class_code_fk_id=classcode.id)
            return HttpResponse(json.dumps(validated_users))
        else:
            return HttpResponse('False')

    context = {
        'title': 'Utwórz klasę',
        'form_user': AddClassForm,
        'form_code': AddClassCodeForm
    }
    return render(request, 'klasowe/add-class.html', context)

# adding class end
