# coding=utf-8

from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from common_views import *
from news_views import *
from advert_views import *
from order_views import *
from pay_views import *
from member_views import *
from finance_views import *
from store_views import *

#会员相关
urlpatterns = (
    url(r'verifycode/$', verifycode),  # 获取图形验证码
    url(r'mobile_vcode/$', mobile_vcode),  # 获取验证码
    url(r'register/check/$', register_check),  # 注册，验证
    url(r'register/$', register),  # 注册
    url(r'version/app/$', version_app),
    url(r'register/finish/$', register_finish),  # 注册，完成(完善资料)
    url(r'reset_password/check/$', reset_password_check),  # 重置密码-检测
    url(r'reset_password/$', reset_password),  # 重置密码
    url(r'auth/$', auth),  # 登录验证并返回token
    url(r'auth/weixin/$', auth_weixin),  # 登录验证并返回token
    url(r'token/(?P<token>.{24})/(?P<user>\d+)/$', token),  # 验证token是否有效
    url(r'user/change_password/$', user_change_password),  # 用户修改密码
    url(r'visit/$', visit),  # 访问统计
    url(r'feedback/submit/$', feedback_submit),  # 提交反馈
    url(r'feedback/mine/$', feedback_mine),  # 用户的反馈
    url(r'feedback/mine/unread/count/$', feedback_mine_unread_count),  # 用户的反馈回复未读条数
    url(r'version/app/$', version_app),  # app版本
    url(r'version/ios/$', version_ios),  # ios版本的状态
)

#会员相关
urlpatterns += (
    url(r'member/profile/save/$', member_profile_save),  # 会员信息修改
    url(r'member/profile/$', member_profile),  # 会员信息

    url(r'member/collection/list/$', collection_list),  # 我的收藏,我的关注
    url(r'member/footmark/list/$', member_footmark_list),  # 我的足迹
    url(r'member/promoting/list/$', member_promoting_list),  # 我的收益金列表

    url(r'member/collection/add/$', collection_add),  # 添加收藏、关注
    url(r'member/collection/del/$', collection_del),  # 取消收藏、关注

    url(r'member/address/list/$', address_list),  # 收货地址列表
    url(r'member/address/save/$', address_save),  # 收货地址添加或修改
    url(r'member/address/del/$', address_del),  # 收货地址删除
)

# 订单相关api
urlpatterns += (
    url(r'order/(?P<type>\w+)/price/$', order_price),  # 读取订单单价 名师培优teach|互动答疑ask

    url(r'order/store/save/$', order_store_save),  # 商城订单保存
    url(r'order/recharge/save/$', order_recharge_save),  # 充值订单保存

    url(r'order/list/$', order_list),  # 我的订单
    url(r'order/(?P<id>\d+)/$', order_detail),  # 订单详情

    url(r'order/notify/unreadcount/$', order_notify_unreadcount),  # 我的消息未读数
    url(r'order/notify/(?P<id>\d+)/read/$', order_notify_read),  # 阅读消息
    url(r'order/notify/list/$', order_notify_list),  # 我的消息列表
)

#商城相关
urlpatterns += (
    url(r'store/product/category/(?P<id>\d+)/list/$', store_product_category_list),  # 商品分类
    url(r'store/product/category/list/$', store_product_category_list),  # 商品分类
    url(r'store/product/list/$', store_product_list),  # 商品列表
    url(r'store/product/(?P<id>\d+)/$', store_product_detail),  # 商品详情

    url(r'store/cart/$', store_cart),  # 购物车内容
    url(r'store/cart/add/$', store_cart_add),  # 添加到购物车
    url(r'store/cart/remove/$', store_cart_remove),  # 从购物车移除
    url(r'store/cart/clear/$', store_cart_clear),  # 清空购物车移除
    url(r'store/cart/update/$', store_cart_update),  # 更新数量
    url(r'store/cart/num/$', store_cart_num),  # 购物车数量
)

# 新闻相关api
urlpatterns += (
    url(r'news/list/$', news_list),  # 新闻列表
    url(r'news/(?P<id>\d+)/$', news_detail_by_id),  # 新闻详细信息
    url(r'news/single/$', news_detail_by_title),  # 新闻详细信息
)

# 广告相关api
urlpatterns += (
    url(r'advert/list/$', advert_list),  # 广告列表
    url(r'advert/video/$', advert_video),  # 片头广告
)

# 财务相关
urlpatterns += (
    url(r'finance/drawing/account/save/$', drawing_account_save),  # 保存提现账户
    url(r'finance/drawing/account/$', drawing_account),  # 提现账户

    url(r'finance/drawing/add/$', drawing_add),  # 提现
    url(r'finance/drawing/list/$', drawing_list),  # 提现记录

    url(r'finance/journals/list/$', journals_list),  # 账户流水
)

#支付相关
urlpatterns += (
    url(r'pay/notify/alipay/$', via_alipay_notify),
    url(r'pay/create/alipay/$', alipay_create),

    url(r'pay/notify/wxpay/$', via_wxpay_notify),
    url(r'pay/create/wxpay/$', wxpay_create),

    url(r'pay/create/balance_pay/$', balance_pay),

    url(r'pay/iap/finish/$', iap_finish),
)
