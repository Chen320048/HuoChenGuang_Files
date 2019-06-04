#coding=utf-8

"""JSON helper functions"""
import json
import urllib2

from django.http import HttpResponse

def JsonResponse(data, dump=True):
    try:
        data['errors']
    except KeyError:
        data['success'] = 1
    except TypeError:
        pass

    return HttpResponse(
        json.dumps(data) if dump else data
    )

def JsonError(error_string):
    data = {
        'success': 0,
        'errors': error_string,
    }
    return JSONResponse(data)

def JsonTokenExpired():
    data = {
        'success': 2,
        'errors': '登录授权已过期',
    }
    return JSONResponse(data)

def JsonErrorCode(code,error):
    data = {
        'success': code,
        'errors': error,
    }
    return JSONResponse(data)

def DataGridResponse(data, total, footer=None):
    result = {
        'rows': data,
        'total': total,
    }
    if footer:
        result['footer'] = footer
    return JsonResponse(result)

# For backwards compatability purposes
JSONResponse = JsonResponse
DataGridJSONResponse = DataGridResponse
JSONError = JsonError
JSONErrorCode = JsonErrorCode
JSONTokenExpired = JsonTokenExpired

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        #print '---302---'
        result.status = code
        return result