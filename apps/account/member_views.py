# # coding=utf-8
#
# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.utils.decorators import method_decorator
# from django.db import transaction, IntegrityError
# from django.db.models import Q, Sum
# from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
# from django.template import RequestContext
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.models import Group, Permission
# from django.utils import timezone
# from django.http import HttpResponseRedirect
# from django.conf import settings
# from django.core.exceptions import PermissionDenied
#
# from models import User
# from forms import AccountForm, MemberAccountForm
# from libs.http import JSONResponse, JSONError
# from libs import utils
# from apps.system.models import VCode
#
# import traceback
#
#
# def member_register(request, template_name, extra_context=None):
#     form = MemberAccountForm(initial={'type': User.MEMBER})
#     referee = request.GET.get('referee')
#     return render_to_response(template_name,
#                               {'form': form, 'referee':referee},
#                               context_instance=RequestContext(request))
#
# def member_register_success(request, template_name, extra_context=None):
#     return render_to_response(template_name,{}, context_instance=RequestContext(request))
#
# @csrf_exempt
# def member_register_save(request):
#     if User.objects.filter(username=request.POST.get('username')).count() > 0:
#         return JSONError(u'帐号已存在！')
#
#     form = MemberAccountForm(request.POST)
#     vcode = request.POST.get('vcode')
#     referee = request.GET.get('referee')
#
#     try:
#         if form.is_valid():
#             rs = VCode.objects.filter(mobile=form.cleaned_data['username']).order_by("-id")
#             if rs.count() == 0:
#                 return JSONError(u'请发送验证码！')
#             vc = rs[0]
#             if (timezone.now() - vc.add_time).seconds > 1800:
#                 return JSONError(u'验证码已过期，请重新发送！')
#             if vc.vcode != vcode:
#                 return JSONError(u'验证码错误！')
#
#             with transaction.atomic():
#                 user = User.objects.create_user(form.cleaned_data['username'],
#                                                 form.cleaned_data['password'],
#                                                 type=User.MEMBER,
#                                                 name=form.cleaned_data['name'])
#                 if referee:
#                     referee = User.objects.filter(username=referee).first()
#                 Member.objects.create(user=user, referee=referee)
#
#                 UserPromoting.objects.create(
#                     src_user=referee,
#                     dest_user=user,
#                     order_no='-',
#                     create_time=timezone.now(),
#                 )
#             return JSONResponse({})
#         else:
#             errors = utils.dump_form_errors(form)
#             return JSONError(errors)
#     except Exception, e:
#         traceback.print_exc()
#         return JSONError(unicode(e))