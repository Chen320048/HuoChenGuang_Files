# coding=utf-8
import traceback

import tablib
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied

from apps.system.models import BizLog
from apps.account.models import User,KindergartenManager
from forms import *
from libs import utils
from libs.http import JSONResponse, JSONError


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def grade_list(request, template_name, extra_context=None):
    """年级管理,幼儿园管理权限"""
    grade_form = GradeForm()
    class_form = ClassForm()
    return render_to_response(template_name,{'form': grade_form,'form_sub':class_form},context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def grade_data(request):
    """年级管理(登录的幼儿园校长的幼儿园年级)"""
    rows = Grade.objects.all()
    if request.user.type == User.KINDERGARTENOR:
        rows = rows.filter(kindergarten=request.user.bind_kindergartenor.kindergarten)
    rows, total = utils.get_page_data(request, rows)
    data = []
    for row in rows:
        data.append(row.to_dict())
    dict = {"total":total, "rows":data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def grade_save(request):
    id = request.GET.get('id')

    if id == None:
        form = GradeForm(request.POST)
    else:
        m = get_object_or_404(Grade, pk=id)
        form = GradeForm(request.POST, instance=m)

    try:
        if form.is_valid():
            with transaction.atomic():
                if id == None:
                    instance = form.save(commit=False)
                    kindergarten = Kindergarten.objects.filter(kinder_managers=request.user.bind_kindergartenor).first()
                    instance.kindergarten = kindergarten
                    instance.save()
                    BizLog.objects.addnew(request.user, BizLog.INSERT,
                                          u"添加年级[%s],id=%d" % (instance.name, instance.id))
                else:
                    instance = form.save()
                    BizLog.objects.addnew(request.user, BizLog.UPDATE,
                                          u"修改年级[%s],id=%d" % (instance.name, instance.id))

            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def class_data(request):
    """班级"""
    grder_id = request.GET.get('grade_id')
    rows = Classes.objects.filter(grade__id=grder_id)
    rows, total = utils.get_page_data(request, rows)
    data = []
    for row in rows:
        data.append(row.to_dict())
    dict = {"total":total, "rows":data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def class_save(request):
    id = request.GET.get('id')
    if id == None:
        form = ClassForm(request.POST)
    else:
        m = get_object_or_404(Classes, pk=id)
        form = ClassForm(request.POST, instance=m)
    try:
        if form.is_valid():
            with transaction.atomic():
                instance = form.save()
                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT,
                                          u"添加班级[%s],id=%d" % (instance.name, instance.id))
                else:
                    instance = form.save()
                    BizLog.objects.addnew(request.user, BizLog.UPDATE,
                                          u"修改班级[%s],id=%d" % (instance.name, instance.id))

            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


@csrf_exempt
def student_list(request,template_name, extra_context=None):
    """学生管理页面"""
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_teacher'):
        raise PermissionDenied()
    form = StudentForm(request=request)  # 构建表单时传入request对象
    classes = Classes.objects.all()
    grade = Grade.objects.all()
    if request.user.type == User.KINDERGARTENOR:  # 当前登录用户幼儿园园长可使用班级年级查询
        classes = classes.filter(grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
        grade = grade.filter(kindergarten=request.user.bind_kindergartenor.kindergarten)

    return render_to_response(template_name, {'form': form,'class':classes,'grade':grade}, context_instance=RequestContext(request))


@csrf_exempt
def student_data(request):
    """学生信息"""
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_teacher'):
        raise PermissionDenied()
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    export = request.POST.get('export')
    rows = Student.objects.all()
    if request.user.type == User.TEACHER:  # 教师
        rows = rows.filter(classes=request.user.bind_teacher.classes)
    if request.user.type == User.KINDERGARTENOR:  # 园长查看所属幼儿园的所有学生
        rows = rows.filter(classes__grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
    if keyword and len(keyword)>0:
        if q == 'student_name':
            rows = rows.filter(name__icontains=keyword)
        elif q == 'gender':
            rows = rows.filter(gender=keyword)
        elif q == 'class':
            rows = rows.filter(classes_id=keyword)
        elif q == 'grade':
            rows = rows.filter(classes__grade_id=keyword)

    if export:
        headers = (u'姓名', u'性别', u'年龄', u'班级', u'年级', u'备注')

        rows = rows.values('name','gender','age','classes__name','classes__grade__name','notes')

        data = []
        for row in rows:#使导出的xlsx文件格式规范不出现编号，null等字符串
            if row['name'] is None:
                row['name'] = u'无'
            if row['gender'] is None:
                row['gender'] = u'无'
            if row['age'] is None:
                row['age'] = u'无'
            if row['classes__name'] is None:
                row['classes__name'] = u'无'
            if row['classes__grade__name'] is None:
                row['classes__grade__name'] = u'无'
            if row['notes'] is None:
                row['notes'] = u'无'
            row['gender'] = Student.GENDER_CHOICES[row['gender']][1]
            data.append(
                (
                    row['name']+' ',
                    row['gender'],
                    row['age'],
                    row['classes__name'],
                    row['classes__grade__name'],
                    row['notes'],
                )
            )

        data = tablib.Dataset(*data, headers=headers, title=u"数据")


        filename = settings.TMP_ROOT + "/export_member.xlsx"
        open(filename, 'wb').write(data.xlsx)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=学生表.xlsx'
        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出学生列表数据")
        return response
    else:
        rows, total = utils.get_page_data(request, rows)

        data = []
        for row in rows:
            item = row.to_dict()
            data.append(item)

        dict = {"total": total, "rows": data}
        return JSONResponse(dict)


@csrf_exempt
def student_save(request):
    """班级学生管理中的修改添加学生功能"""
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_teacher'):
        raise PermissionDenied()
    id = request.GET.get('id')
    if id == None:
        form = StudentForm(request.POST,request=request)
    else:
        m = get_object_or_404(Student, pk=id)
        form = StudentForm(request.POST, instance=m,request=request)
    try:
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(commit=False)
                instance.classes = form.cleaned_data['classes']
                instance.save()
                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT,u"添加学生[%s],id=%d" % (instance.name, instance.id))
                else:
                    BizLog.objects.addnew(request.user, BizLog.UPDATE,u"修改学生[%s],id=%d" % (instance.name, instance.id))

                # name = 'icon'
                # for file in request.FILES:
                #     filename = utils.handle_image_upload(request, Student.path_and_rename, request.FILES[file], name,
                #                                          instance)
                #     if file == name:
                #         instance.icon = filename
                #         instance.save()

            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


