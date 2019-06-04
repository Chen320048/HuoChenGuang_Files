//计算文本的字节长度
String.prototype.getBytesLength = function() {    
	return this.replace(/[^\x00-\xff]/gi, "--").length;
}

String.prototype.format = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
}

String.prototype.endsWith = function (suffix) {
  return (this.substr(this.length - suffix.length) === suffix);
}

String.prototype.startsWith = function(prefix) {
  return (this.substr(0, prefix.length) === prefix);
}

$.ajaxSetup({
    beforeSend:function(){
		$("#indicator .mask").height('100%');
        $("#indicator").show();
    },
    complete:function(){
        $("#indicator").hide();
    }
});

$.fn.extend({  
    /** 
     * 修改DataGrid对象的默认大小，以适应页面宽度。 
     *  
     * @param heightMargin 
     *            高度对页内边距的距离。 
     * @param widthMargin 
     *            宽度对页内边距的距离。 
     * @param minHeight 
     *            最小高度。 
     * @param minWidth 
     *            最小宽度。 
     *  
     */  
    resizeDataGrid : function(heightMargin, widthMargin, minHeight, minWidth) {  
        var height = $(document.body).height() - heightMargin - 60;  
        var width = $(document.body).width() - widthMargin;  
  
        height = height < minHeight ? minHeight : height;  
        width = width < minWidth ? minWidth : width;  
  
        $(this).datagrid('resize', {  
            height : height,  
            width : width  
        });  
		//alert(height+'--'+width)
    }  
});

$.extend($.fn.datagrid.methods, {
    //显示遮罩
    loading: function(jq){

    },
    //隐藏遮罩
    loaded: function(jq){

    }
});

function detectIE(){
    var ua = window.navigator.userAgent;

    var msie = ua.indexOf('MSIE ');
    if (msie > 0) {
        // IE 10 or older => return version number
        return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
    }

    var trident = ua.indexOf('Trident/');
    if (trident > 0) {
        // IE 11 => return version number
        var rv = ua.indexOf('rv:');
        return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
    }

    var edge = ua.indexOf('Edge/');
    if (edge > 0) {
       // IE 12 => return version number
       return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
    }

    // other browser
    return false;
}

function getPrintWidth(){
    if(detectIE() == 11)
        return "182mm";
    else
        return "182mm";
}

function object2str(obj){
	var arr = new Array();
	for (var k in obj){
		var item = k + "=" + obj[k];
		arr.push(item.replace(' ', '%20'));
	}
	return arr.join('&');
}

function undulpicate(array){  
    for(var i=0;i<array.length;i++) {  
        for(var j=i+1;j<array.length;j++) {
            if(array[i]===array[j]) {  
                array.splice(j,1);  
                j--;  
            }  
        }  
    }  
    return array;  
}

function toDecimal2(x) {
    var f = x;
    if (isNaN(f)) {
        return '';
    }
    var f = Math.round(x*100)/100;
    var s = f.toString();
    var rs = s.indexOf('.');
    if (rs < 0) {
        rs = s.length;
        s += '.';
    }
    while (s.length <= rs + 2) {
        s += '0';
    }
    return s;
}

function EncodeUtf8(s1) {
	var stringArray = new Array();
	for(var j=0; j<s1.length;j++){
		stringArray[j] = escape(s1.charAt(j)).replace("%",""); 
	}

	var sa = stringArray;
	
	var retV = "";
	
	for (var i = 0; i < sa.length; i++) {		
		if (sa[i].length > 1 && sa[i].substring(0, 1) == "u") {
			retV += Hex2Utf8(Str2Hex(sa[i].substring(1, 5)));
		}else if(sa[i].length == 2){
			//转义字符和标点符号
			retV += "%" + sa[i];
		} else {
			retV += sa[i];                
		}
	}
	return retV;
}

function Str2Hex(s) {
    var c = "";
    var n;
    var ss = "0123456789ABCDEF";
    var digS = "";
    for (var i = 0; i < s.length; i++) {
        c = s.charAt(i);
        n = ss.indexOf(c);
        digS += Dec2Dig(eval(n));
    }
//return value;
    return digS;
}
function Dec2Dig(n1) {
    var s = "";
    var n2 = 0;
    for (var i = 0; i < 4; i++) {
        n2 = Math.pow(2, 3 - i);
        if (n1 >= n2) {
            s += "1";
            n1 = n1 - n2;
        } else {
            s += "0";
        }
    }
    return s;
}
function Dig2Dec(s) {
    var retV = 0;
    if (s.length == 4) {
        for (var i = 0; i < 4; i++) {
            retV += eval(s.charAt(i)) * Math.pow(2, 3 - i);
        }
        return retV;
    }
    return -1;
}
function Hex2Utf8(s) {
    var retS = "";
    var tempS = "";
    var ss = "";

    if (s.length == 16) {
        tempS = "1110" + s.substring(0, 4);
        tempS += "10" + s.substring(4, 10);
        tempS += "10" + s.substring(10, 16);
        var sss = "0123456789ABCDEF";
        for (var i = 0; i < 3; i++) {
            retS += "%";
            ss = tempS.substring(i * 8, (eval(i) + 1) * 8);
            retS += sss.charAt(Dig2Dec(ss.substring(0, 4)));
            retS += sss.charAt(Dig2Dec(ss.substring(4, 8)));
        }
        return retS;
    }
    return "";
}

function isDate(dateString){
	if(dateString.trim()=="")return true;
	var r=dateString.match(/^(\d{1,4})(-|\/)(\d{1,2})\2(\d{1,2})$/); 
	if(r==null)
		return false;
	
	var d=new Date(r[1],r[3]-1,r[4]);   
	var num = (d.getFullYear()==r[1]&&(d.getMonth()+1)==r[3]&&d.getDate()==r[4]);
	return (num!=0);
}

function dateAdd(interval, number, date) {
    switch (interval) {
    case "y": {
        date.setFullYear(date.getFullYear() + number);
        return date;
        break;
    }
    case "q": {
        date.setMonth(date.getMonth() + number * 3);
        return date;
        break;
    }
    case "m": {
        date.setMonth(date.getMonth() + number);
        return date;
        break;
    }
    case "w": {
        date.setDate(date.getDate() + number * 7);
        return date;
        break;
    }
    case "d": {
        date.setDate(date.getDate() + number);
        return date;
        break;
    }
    case "h": {
        date.setHours(date.getHours() + number);
        return date;
        break;
    }
    case "m": {
        date.setMinutes(date.getMinutes() + number);
        return date;
        break;
    }
    case "s": {
        date.setSeconds(date.getSeconds() + number);
        return date;
        break;
    }
    default: {
        date.setDate(date.getDate() + number);
        return date;
        break;
    }
    }
}

Date.prototype.diff = function(date){
  return Math.ceil((this.getTime() - date.getTime())/(24 * 60 * 60 * 1000));
}

function randomNumber(length) {
    var chars = '0123456789'.split('');

    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }

    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
}

function randomString(length) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');

    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }

    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
}

extArray = new Array(".png");
function limitAttach(file) {
	allowSubmit = false;
	if (!file) 
		return true;

	while (file.indexOf("\\") != -1)
		file = file.slice(file.indexOf("\\") + 1);
	ext = file.slice(file.indexOf(".")).toLowerCase();
	for (var i = 0; i < extArray.length; i++) {
		if (extArray[i] == ext) { allowSubmit = true; break; }
	}

	if (allowSubmit) 
		return true;
	else{
		alert("只能上传:" + (extArray.join("  ")) + "格式，请重新选择文件再上传.");
		return false;
	}
}

function getObjectURL(file) {
	var url = null ; 
	if (window.createObjectURL!=undefined) { // basic
		url = window.createObjectURL(file) ;
	} else if (window.URL!=undefined) { // mozilla(firefox)
		url = window.URL.createObjectURL(file) ;
	} else if (window.webkitURL!=undefined) { // webkit or chrome
		url = window.webkitURL.createObjectURL(file) ;
	}
	return url ;
}

function readURL(input, img, width) {
	if (input.files && input.files[0]) {
		var reader = new FileReader();
		reader.onload = function (e) { 
			$(img).attr('src', e.target.result);//.width(size.width).height(size.height);
		};
		reader.readAsDataURL(input.files[0]);
	} else {
		//IE下，使用滤镜
		var docObj = document.getElementByIdx_x('doc');
		docObj.select();
		//解决IE9下document.selection拒绝访问的错误
		docObj.blur();
		var imgSrc = document.selection.createRange().text;
		var localImagId = document.getElementByIdx_x("localImag");
		$(img).width(size.width).height(size.height); //必须设置初始大小
		//图片异常的捕捉，防止用户修改后缀来伪造图片
		try {
			localImagId.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale)";
			localImagId.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").src = imgSrc;
		} catch (e) {
			alert("您上传的图片格式不正确，请重新选择!"); 
			return false;
		}
	}
}

var aCity={11:"北京",12:"天津",13:"河北",14:"山西",15:"内蒙古",21:"辽宁",22:"吉林",23:"黑龙江",31:"上海",32:"江苏",33:"浙江",34:"安徽",35:"福建",36:"江西",37:"山东",41:"河南",42:"湖北",43:"湖南",44:"广东",45:"广西",46:"海南",50:"重庆",51:"四川",52:"贵州",53:"云南",54:"西藏",61:"陕西",62:"甘肃",63:"青海",64:"宁夏",65:"新疆",71:"台湾",81:"香港",82:"澳门",91:"国外"} 
function cidInfo(sId){ 
	var iSum = 0;
	var info = "";
	if(!/^\d{17}(\d|x)$/i.test(sId))
		return false; 

	sId = sId.replace(/x$/i,"a"); 
	if(aCity[parseInt(sId.substr(0,2))]==null)
		return false; 
		//return "Error:非法地区"; 

	sBirthday=sId.substr(6,4)+"-"+Number(sId.substr(10,2))+"-"+Number(sId.substr(12,2)); 
	var d = new Date(sBirthday.replace(/-/g,"/"));
	if(sBirthday!=(d.getFullYear()+"-"+ (d.getMonth()+1) + "-" + d.getDate()))
		return false; 
		//return "Error:非法生日"; 

	for(var i = 17;i>=0;i --) 
		iSum += (Math.pow(2,i) % 11) * parseInt(sId.charAt(17 - i),11) 

	if(iSum%11!=1)
		return false; 
		//return "Error:非法证号"; 

	//alert(aCity[parseInt(sId.substr(0,2))]+","+sBirthday+","+(sId.substr(16,1)%2?"男":"女") );
	//return {province:aCity[parseInt(sId.substr(0,2))],
	//		birthday:sBirthday,
	//		gender:(sId.substr(16,1)%2?"男":"女") };
	return true;
} 

$.extend($.fn.validatebox.defaults.rules, {
    cidInfo: {
        validator: function(value,param){
            return cidInfo(value);
        },
        message: '无效的身份证号'
    },
	mobile: {
	    validator: function(value,param){
            return /^0?(13[0-9]|15[012356789]|17[0678]|18[0-9]|14[57])[0-9]{8}$/i.test(value);
        },
        message: '无效的手机号码'
	},
	equals: {
		validator: function(value,param){
			return value == $(param[0]).val();
		},
		message: '两次输入不一致'
	},
	selectValueRequired: {  
		validator: function(value,param){  
			return $(param[0]).find("option:contains('"+value+"')").val() != '';  
		},  
		message: '此项必选.'  
	}
});

$.extend($.fn.textbox.methods, {
	show: function(jq){
		return jq.each(function(){
			$(this).next().show();
		})
	},
	hide: function(jq){
		return jq.each(function(){
			$(this).next().hide();
		})
	}
})

jQuery.submitValidate = function (fm){
    var valid = $(fm).form('validate');
    if(!valid){
        $.messager.alert('错误', '无法保存，请检查输入框为红色的项目！', 'error');
        //$(fm+' .validatebox-invalid').each(function(){
        //    alert($(this).next().attr('name'))
        //});
    }
    return valid;
}

jQuery.download = function(url, data, method){
    // 获得url和data
    if( url && data ){
        // data 是 string 或者 array/object
        data = typeof data == 'string' ? data : jQuery.param(data);
        // 把参数组装成 form的  input
        var inputs = '';
        jQuery.each(data.split('&'), function(){ 
            var pair = this.split('=');
            inputs+='<input type="hidden" name="'+ pair[0] +'" value="'+ pair[1] +'" />'; 
        });
        // request发送请求
        jQuery('<form action="'+ url +'" method="'+ (method||'post') +'">'+inputs+'</form>')
        .appendTo('body').submit().remove();
    };
};


$.extend($,{ 
    sub_str:function(str,len){
		var a=str.match(/[^\x00-\xff]|\w{1,2}/g);  
		return a.length<length?str:a.slice(0,length).join("");  	
	},
    getParameterByName:function(name) {
        name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }
}); 


jQuery.wordCounter = function(id, maxLength){
	var ele = $('#' + id);
	var limitId = id + '_limit';
	if($('#' + limitId)[0])
		return;

	var span_limit = $('<div id="' + limitId + '"></div>');

	function render() {
		var len = ele.textbox('getText').length;
		if (len >= maxLength){
			ele.textbox('setText', ele.textbox('getText').substr(0, maxLength));			
			len = maxLength;
		}

		span_limit.html("已输入&nbsp;<b>" + len + "</b>&nbsp;字，还能输入&nbsp;<b>" + (maxLength-len) + "</b>&nbsp;字");
	};
	
	ele.textbox({
		inputEvents:$.extend({},$.fn.textbox.defaults.inputEvents,{
			keyup:function(e){
				render();
			}
		})
	})
	ele.next().after(span_limit);
	
	render();
}

Array.prototype.contains = function(obj) {
    var i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
}