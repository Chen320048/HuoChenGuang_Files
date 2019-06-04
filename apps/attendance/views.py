# coding:utf-8
import tablib
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from django.utils import timezone

from apps.classes.models import Grade,Kindergarten
from apps.system.models import BizLog
from apps.account.models import User
from libs.http import JSONResponse, JSONError
from libs import utils
from forms import *
from ningmeng import settings


@csrf_exempt
@permission_required('account.manage_teacher')
def attendance_list(request, template_name, extra_context=None):
    form_edit = AttendanceEditForm()
    classes = Classes.objects.all().values("id")
    if request.user.type == User.KINDERGARTENOR:
        classes = classes.filter(grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
    if request.user.type == User.TEACHER:  # 教师
        classes = classes.filter(pk=request.user.bind_teacher.classes.id)
    student = Student.objects.filter(classes__in=classes)
    form_list = []
    for row in student:
        form_add = AttendanceForm(initial={'student':row.id})
        form_add.order_fields(['student','status','notes'])
        form_list.append(form_add)
    return render_to_response(template_name, context={'form':form_edit,'form_list':form_list},context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_teacher')
def attendance_data(request):
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    status = request.POST.get('status')
    stuname = request.POST.get('stuname')
    export = request.POST.get('export')
    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    today = request.POST.get('today')
    user = request.user
    if not any([q,keyword,status,stuname,export,date_begin,date_end,today]):
        # 默认展示当天考勤
        rows = Attendance.objects.filter(date=strfdate(timezone.now())).order_by('-date')
    else:
        rows = Attendance.objects.all().order_by('-date')
    classes = Classes.objects.all().values("id")
    if request.user.type == User.KINDERGARTENOR:
        classes = classes.filter(grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
    if request.user.type == User.TEACHER:  # 教师
        classes = classes.filter(pk=request.user.bind_teacher.classes.id)
    rows = rows.filter(classes__in=classes)
    if today:
        rows = rows.filter(date=today)
    if status:
        rows = rows.filter(status=status)
    if stuname:
        rows = rows.filter(student__name__icontains=stuname)
    if keyword and len(keyword) > 0:
        if q == 'name':
            rows = rows.filter(student__name__icontains=keyword)
        if q == 'type':
            rows = rows.filter(status=keyword)
    if date_begin:
        rows = rows.filter(date__gte=date_begin)
    if date_end:
        rows = rows.filter(date__lte=date_end )
    if export:  # 进行考勤导出时(复合查询结果,由js的变量进行控制)
        headers = (u'姓名',u'班级',u'年级', u'考勤', u'时间', u'备注',)

        rows = rows.values('student__name', 'classes__name', 'classes__grade__name', 'status', 'date', 'notes')

        data = []
        for row in rows:  # 使导出的xlsx文件格式规范不出现编号，null等字符串
            if row['student__name'] is None:
                row['student__name'] = u'无'
            if row['classes__name'] is None:
                row['classes__name'] = u'无'
            if row['classes__grade__name'] is None:
                row['classes__grade__name'] = u'无'
            if row['status'] is None:
                row['status'] = Attendance.STATUS_CHOICES[row['status']][1]
            if row['date'] is None:
                row['date'] = u'无'
            if row['notes'] is None:
                row['notes'] = u''
            row['status'] = Attendance.STATUS_CHOICES[row['status']][1]
            data.append(
                (
                    row['student__name'] + ' ',
                    row['classes__name'],
                    row['classes__grade__name'],
                    row['status'],
                    row['date'],
                    row['notes'],
                )
            )

        data = tablib.Dataset(*data, headers=headers, title=u"数据")

        filename = settings.TMP_ROOT + "/export_member.xlsx"
        open(filename, 'wb').write(data.xlsx)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=考勤表.xlsx'
        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出考勤数据")
        return response
    else:
        rows, total = utils.get_page_data(request, rows)

        data = []
        for row in rows:
            item = {}
            item = row.to_dict()
            data.append(item)
        dict = {"total": total, "rows": data}
        return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_teacher')
def attendance_save(request):
    id = request.GET.get('id')
    if id == None:
        # 多个学生考勤信息
        try:
            with transaction.atomic():
                classes = request.user.bind_teacher.classes
                att = Attendance.objects.filter(classes=classes,date=utils.strfdate(timezone.now()))
                if att.exists():
                    return JSONError(u'今日考勤已生成,请勿重复操作')
                stu_dict = dict(request.POST)
                for i in range(len(stu_dict['student'])):
                    stu = Student.objects.get(id=stu_dict['student'][i])
                    Attendance.objects.create(student=stu,classes=classes,submitter=request.user,status=stu_dict['status'][i],notes=stu_dict['notes'][i])
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"添加学生[%s]考勤,id=%d" % (stu.name, stu.id))
                return JSONResponse({})
        except Exception, e:
            return JSONError(str(e))
    else:
        att = get_object_or_404(Attendance,pk=id)
        att.notes = request.POST['notes']
        att.status = int(request.POST['status'])
        att.save()
        BizLog.objects.addnew(request.user, BizLog.UPDATE,u"修改学生[%s]考勤,id=%d" % (att.student.name, att.id))
        return JSONResponse({'id': att.id})



@csrf_exempt
@permission_required('account.manage_teacher')
def student_data(request):
    try:
        rows = Student.objects.filter(classes=request.user.bind_teacher.classes)
        data = []
        for row in rows:
            item = {
                'id':row.id,
                'name':row.name
            }
            data.append(item)
        return JSONResponse(data)
    except Exception, e:
        return JSONError(str(e))


@csrf_exempt
def student_list(request, template_name, extra_context=None):
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_teacher'):
        raise PermissionDenied()
    classes = []
    grade = []
    if request.user.type == User.KINDERGARTENOR:  # 当前登录用户幼儿园园长可使用班级年级查询
        classes = Classes.objects.filter(grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
        grade = Grade.objects.filter(kindergarten=request.user.bind_kindergartenor.kindergarten)
    return render_to_response(template_name, {'class': classes, 'grade': grade},
                              context_instance=RequestContext(request))


@csrf_exempt
def student_attendance(request):
    """个人考勤"""
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_teacher'):
        raise PermissionDenied()

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    export = request.POST.get('export')
    name = request.POST.get('stuname')
    user = request.user
    attendance = Attendance.objects.all()
    students = Student.objects.all()
    if user.type == User.TEACHER:
        attendance = attendance.filter(classes=request.user.bind_teacher.classes)
        students = students.filter(classes__class_teacher=user.bind_teacher)
    elif user.type == User.KINDERGARTENOR:
        attendance = attendance.filter(classes__grade__kindergarten=user.bind_kindergartenor.kindergarten)
        students = students.filter(classes__grade__kindergarten=user.bind_kindergartenor.kindergarten)
    if date_begin:
        attendance = attendance.filter(date__gte=date_begin)
    if date_end:
        attendance = attendance.filter(date__lte=date_end)

    if keyword and len(keyword)>0:
        if q == 'name':
            students = students.filter(name__icontains=keyword)
        elif q == 'class':
            students = students.filter(classes_id=keyword)
        elif q == 'grade':
            students = students.filter(classes__grade_id=keyword)
    if name:
        students = students.filter(name__icontains=name)
    if keyword and len(keyword) > 0:
        if q == 'name':
            students = students.filter(name__icontains=keyword)
    students,total = utils.get_page_data(request,students)
    data = []
    for stu in students:
        info = {}
        att = attendance.filter(student=stu)
        abs = Absence.objects.filter(student=stu).exclude(status=Absence.REFUSE)  # 待审核和审核通过的申请
        if date_begin:
            abs = abs.filter(date__gte=date_begin)
        if date_end:
            abs = abs.filter(date__lte=date_end)
        info['unrefund_count'] = 0
        if abs.exists():
            for row in abs:
                info['unrefund_count'] += row.days
        info['count'] = att.count()  # 考勤总次数
        info['normal_count'] = att.filter(status=Attendance.NORMAL).count()  # 正常考勤次数
        info['absence_count'] = info['count'] - info['normal_count']  # 缺勤
        info['refund_count'] = info['absence_count'] - info['unrefund_count']  # 未申请退费的考勤
        info['class'] = stu.classes and stu.classes.name or ""
        info['grade'] = stu.classes and stu.classes.grade.name or ""
        info['student'] = stu.name
        data.append(info)
    return JSONResponse({'rows': data, 'total': total})

@csrf_exempt
@permission_required('account.manage_teacher')
def refund_list(request, template_name, extra_context=None):
    # if not request.user.has_perm('account.manage_teacher') and not request.user.has_perm('account.manage_company'):
    #     raise PermissionDenied()

    form = RefundSubForm(request=request)  # 在构建form对象时传入request参数
    form.order_fields(['student','days','balance','submit_notes',])  # 对form字段进行排序,包含所有字段
    return render_to_response(template_name,{'form':form,},context_instance=RequestContext(request))


@csrf_exempt
def refund_data(request):
    if not request.user.has_perm('account.manage_teacher') and not request.user.has_perm('account.manage_company'):
        raise PermissionDenied()
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    export = request.POST.get('export')
    stuname = request.POST.get('stuname')
    user = request.user
    if user.type == User.TEACHER:
        rows = Absence.objects.filter(student__classes=user.bind_teacher.classes).order_by('-date')
    elif user.type == User.COMPANY:  # 园企具有查看所有幼儿园的学生的缺勤退费申请
        rows = Absence.objects.all().order_by('-date')
    if keyword and len(keyword) > 0:
        if q == 'kinder':
            rows = rows.filter(student__classes__grade__kindergarten=keyword)
        elif q == 'status':
            rows = rows.filter(status=keyword)
        elif q == 'name':
            rows = rows.filter(student__name=keyword)
    if date_begin:
        rows = rows.filter(date__gte=date_begin)
    if date_end:
        rows = rows.filter(date__lte=date_end )
    if stuname:
        rows = rows.filter(student__name=keyword)
    rows, total = utils.get_page_data(request, rows)
    data = []
    for row in rows:
        data.append(row.to_dict())
    return JSONResponse({'rows': data, 'total': total})


@csrf_exempt
@permission_required('account.manage_teacher')
def refund_save(request):
    # if not request.user.has_perm('account.manage_teacher') and not request.user.has_perm('account.manage_company'):
    #     raise PermissionDenied()
    id = request.GET.get('id')
    # 对发起退费申请的学生进行是否可进行缺勤退费的申请  (暂不开放修改功能)
    stu_id = request.POST.get('student')
    try:
        days = int(request.POST.get('days'))
    except ValueError:
        return JSONError(u'无效的缺勤天数')
    if days <= 0:
        return JSONError(u'无效的缺勤天数')
    rows = Attendance.objects.filter(student_id=stu_id)
    total_count = rows.count()  # 学生考勤总数
    normal_count = rows.filter(status=Attendance.NORMAL).count()  # 该学生正常考勤总数
    absence_count = total_count - normal_count  # 缺勤数
    unrefund_count = 0

    rows = Absence.objects.filter(student_id=stu_id).exclude(status=Absence.REFUSE)  # 新申请退费时,查询出已经通过的和待审核的申请退费

    if rows.exists():
        for row in rows:
            unrefund_count += row.days  # 计算出该学生的已经申请的总退费数
    refund_count = absence_count - unrefund_count  # 可申请退费的缺勤次数
    if refund_count <= 0:
        return JSONError(u'该学生可申请退费的天数为0')
    if days > refund_count:  # 前端输入的天数进行判断
        return JSONError(u'申请退费的天数超过可退费天数')


    if id == None:
        form = RefundSubForm(request.POST,request=request)  # 注意构建form对象时传入request,否则modelform报错
    else:
        m = get_object_or_404(Absence,pk=id)
        form = RefundSubForm(request.POST,instance=m,request=request)
    try:
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.student = form.cleaned_data['student']
                instance.save()
                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加考勤退费申请[%s],id=%d" % (instance.student.name, instance.id))
                else:
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"修改考勤退费申请[%s],id=%d" % (instance.student.name, instance.id))

            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


@csrf_exempt
@permission_required('account.manage_company')
def refund_review_list(request, template_name, extra_context=None):
    form = RefundReviewForm()
    kinder = Kindergarten.objects.all()
    return render_to_response(template_name, {'form': form, 'kinder': kinder}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_company')
def refund_review_save(request):
    id = request.GET.get('id')
    status = request.GET.get('action')  # 1表示通过，2表示拒绝
    review_notes = request.POST.get('review_notes')
    try:
        with transaction.atomic():
            abs = get_object_or_404(Absence, pk=id)
            abs.status = int(status)
            abs.review_notes = review_notes
            abs.save()
            BizLog.objects.addnew(request.user, BizLog.INSERT, u"审核考勤退费申请[%s],id=%d,审核结果[%s]" % (abs.student.name, abs.id, Absence.STATUS_CHOICES[int(status)][1]))
        return JSONResponse({'id': abs.id})
    except Exception, e:
        return JSONError(unicode(e))