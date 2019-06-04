function createIcon(map, id, url, point){
    var layer = new Careland.Layer('point', id);
    map.addLayer(layer);
    var style = new Careland.PointStyle({offsetX:-20,offsetY:-40,textOffsetX:-5,textOffsetY:-30,src:url});
    var marker = new Careland.Marker('image');
    marker.setStyle(style);
    marker.setPoint(point);
    layer.add(marker);

    return marker;
}

function renderMessage(map, data, excludeId){
    var n=0;
	for(var k in data){
		var row = data[k];
		if(excludeId == row.id)
		    continue;

		var markerPoint;

		if(row.range == "1"){
		    //alert(row.cld_x_y)
			var pos = row.cld_x_y.split(',');
			markerPoint = new Careland.Point(parseInt(pos[0]),parseInt(pos[1]));
		}else{
			var points = row.cld_x_y.split(';');
			var polyarray = new Array();

			for(var i = 0; i < points.length - 1; i++){
				var p = points[i].split(',');
				var cpoint = new Careland.Point(parseInt(p[0]),parseInt(p[1]));
				polyarray.push(cpoint);
			}

            var layer = new Careland.Layer('polyline', 'marker_'+n);
            map.addLayer(layer);
            var polyline = new Careland.Polyline();
            polyline.setPoints(polyarray);
            polyline.setStyle(new Careland.LineStyle({color:'red',size:2}));
            layer.add(polyline);

			markerPoint = polyarray[0];
			n++;
		}

		var marker = createIcon(map, 'marker_message_'+k, "/media/" + row.event_type_icon, markerPoint);

		marker.addEventListener("click", function(e, obj){
		    var d = data[obj.index];

			var content = d.road_name + d.start_km + "公里至" + d.end_km + "公里" + d.section;
			content += "<br>详情：" + d.content;
			content += "<br>发布时间：" + d.happen_time + "<br>预计结束时间：" + d.duration;
			content += "<br>事件后果：" + d.consequences;

            var opts = {
                id: "win_msg",
                width : 400,
                height: 250,
                offset: new Careland.Size(0,-20),
                title : '路况信息',
                content: content,
                enableAutoPan: true
            };
            var mapInfoWin = new Careland.InfoWindow(opts);
            map.openInfoWindow(mapInfoWin, obj.point);
		}, {index:k, point:markerPoint});
	}
}

function renderAccidentSection(map, data){
	for(var k in data){
		var item = data[k];
		var markerPoint = new Careland.Point(parseInt(item.cld_x),parseInt(item.cld_y));

		var marker = createIcon(map, 'marker_as_'+k, item.icon, markerPoint);

		marker.addEventListener("click", function(e, obj){
			var d = data[obj.index];
			var content = "预警类别：" + d.consequences_text + "<br>" + d.warn_content;
			var opts = {
			  id: "win_msg",
			  width : 200,
			  height: 100,
			  title : '事故易发路段',
              offset: new Careland.Size(0,-20),
              content: content,
              enableAutoPan: true
			}
            var mapInfoWin = new Careland.InfoWindow(opts);
            map.openInfoWindow(mapInfoWin, obj.point);
		}, {index:k, point:markerPoint});
	}
}

function renderReport(map, data){
	for(var k in data){
		var item = data[k];
		var markerPoint = new Careland.Point(parseInt(item.cld_x),parseInt(item.cld_y));

		var marker = createIcon(map, 'marker_report_'+k, "/static/images/ico_report.png", markerPoint);

		marker.addEventListener("click", function(e, obj){
			var d = data[obj.index];
			var content = "用户：" + d.create_username + "<br>时间：" + d.create_time + "<br>爆料：" + d.text + "<div style='padding:5px'>";
			if(d.image) content += "<br><a href='/media/"+d.image+"' target='_blank'><img src='/media/"+d.image+"' width='50px'></a>"
			if(d.voice) content += "<a href='/media/"+d.voice+"' target='_blank'><img src='/static/images/play.png' style='float:right;margin-top:20px'></a>"
			content += "</div>";
			var opts = {
			  id: "win_msg",
			  width : 300,
			  height: 150,
			  title : "网友互动",
              offset: new Careland.Size(0,-20),
              content: content,
              enableAutoPan: true
			}
            var mapInfoWin = new Careland.InfoWindow(opts);
            map.openInfoWindow(mapInfoWin, obj.point);
		}, {index:k, point:markerPoint});
	}
}

function renderAlarm(map, data){
	for(var k in data){
		var item = data[k];
		var markerPoint = new Careland.Point(parseInt(item.cld_x),parseInt(item.cld_y));
		var marker = createIcon(map, 'marker_alarm_'+k, "/static/images/ico_alerm_"+item.status+".png", markerPoint);

		marker.addEventListener("click", function(e, obj){
			var d = data[obj.index];
			var content = "用户：" + d.create_uuid + "<br>时间：" + d.create_time + "<br>手机：" + d.create_number;
			var opts = {
			  id: "win_msg",
			  width : 250,
			  height: 100,
			  title : '报警',
              offset: new Careland.Size(0,-20),
              content: content,
              enableAutoPan: true
			}
            var mapInfoWin = new Careland.InfoWindow(opts);
            map.openInfoWindow(mapInfoWin, obj.point);
		}, {index:k, point:markerPoint});
	}
}


function renderCamera(map, data){
	for(var k in data){
		var item = data[k];
		var markerPoint = new Careland.Point(parseInt(item.cld_x),parseInt(item.cld_y));
		var marker = createIcon(map, 'marker_camera_'+k, "/static/images/ico_camera.png", markerPoint);

		marker.addEventListener("click", function(e, obj){
			var d = data[obj.index];
			var content = "";
			if(d.image) content += "<a href='/media/"+d.image+"' target='_blank'><img src='/media/"+d.image+"' width='352px'></a>"

			var opts = {
			  id: "win_msg",
			  width : 360,
			  height: 288,
              offset: new Careland.Size(0,-20),
              title: d.road,
              content: content,
              enableAutoPan: true
			}
            var mapInfoWin = new Careland.InfoWindow(opts);
            map.openInfoWindow(mapInfoWin, obj.point);
		}, {index:k, point:markerPoint});
	}
}

function renderWeather(map, data){
	for(var k in data){
		var item = data[k];
		var markerPoint = new Careland.Point(parseInt(item.cld_x),parseInt(item.cld_y));
		var marker = createIcon(map, 'marker_camera_'+k, "/static/images/weather/" + item.icon, markerPoint);

		marker.addEventListener("click", function(e, obj){
			var d = data[obj.index];
			var content = "天气：" + d.weather + "<br>温度：" + d.temputer;
			var opts = {
			  id: "win_msg",
			  width : 15,
			  height: 60,
              offset: new Careland.Size(0,-20),
              title : d.city,
              content: content,
              enableAutoPan: true
			}
            var mapInfoWin = new Careland.InfoWindow(opts);
            map.openInfoWindow(mapInfoWin, obj.point);
		}, {index:k, point:markerPoint});
	}
}