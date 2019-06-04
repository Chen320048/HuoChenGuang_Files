#coding=utf-8
import json
import uuid

from aliyunsdkcore import client
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkcore.profile import region_provider

from django.conf import settings


class SMS:
    def __init__(self):
        PRODUCT_NAME = "Dysmsapi"
        DOMAIN = "dysmsapi.aliyuncs.com"

        ACCESS_KEY_ID = "LTAIGC9qxzJZsBEG"
        ACCESS_KEY_SECRET = "tWHCgNI4Nst9Ha04mm4np28YnvOGUP"
        REGION = "cn-hangzhou"

        self.client = client.AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
        region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

    def _send_sms(self, business_id, phone_numbers, sign_name, template_code, template_param=None):
        smsRequest = SendSmsRequest.SendSmsRequest()
        # 申请的短信模板编码,必填
        smsRequest.set_TemplateCode(template_code)

        # 短信模板变量参数
        if template_param is not None:
            smsRequest.set_TemplateParam(template_param)

        # 设置业务请求流水号，必填。
        smsRequest.set_OutId(business_id)

        # 短信签名
        smsRequest.set_SignName(sign_name)

        # 短信发送的号码列表，必填。
        smsRequest.set_PhoneNumbers(phone_numbers)

        # 调用短信发送接口，返回json
        smsResponse = self.client.do_action_with_exception(smsRequest)

        # print 'sms:=================================================='
        # print smsResponse
        # {"Message":"OK","RequestId":"93044703-E24B-4925-BE30-27DD942234AA","BizId":"507517905893843184^0","Code":"OK"}
        # {"Message":"触发号码天级流控Permits:40","RequestId":"45E70A54-3D4B-4FB0-8513-1144246E1EDD","Code":"isv.BUSINESS_LIMIT_CONTROL"}
        # {"Message":"触发小时级流控Permits:5","RequestId":"B8C0E2BE-A5D9-4627-9C2F-643A069064EE","Code":"isv.BUSINESS_LIMIT_CONTROL"}

        return smsResponse

    def send_vcode(self, mobile, vcode, template_no):
        mobile = str(mobile)
        business_id = uuid.uuid1()
        params = "{\"code\":\"" + vcode + "\"}"
        resp = self._send_sms(business_id, mobile, settings.APP_NAME, template_no, params)  # SMS_97890029,SMS_95630267
        try:
            resp = json.loads(resp)

            if resp['Code'] == 'OK':
                return True
            else:
                print resp
                return False
        except Exception, e:
            print resp, e
            return False

    def send_order(self, mobile):
        mobile = str(mobile)
        business_id = uuid.uuid1()
        resp = self._send_sms(business_id, mobile, settings.APP_NAME, 'SMS_126876430')  # SMS_97890029,SMS_95630267
        try:
            resp = json.loads(resp)

            if resp['Code'] == 'OK':
                return True
            else:
                return False
        except Exception, e:
            print resp, e
            return False

    def send_ask_done(self, mobile):
        mobile = str(mobile)
        business_id = uuid.uuid1()
        resp = self._send_sms(business_id, mobile, settings.APP_NAME, 'SMS_129760992')  # SMS_97890029,SMS_95630267
        try:
            resp = json.loads(resp)

            if resp['Code'] == 'OK':
                return True
            else:
                return False
        except Exception, e:
            print resp, e
            return False