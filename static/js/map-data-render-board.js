function renderMessage(data){
	for(var k in data){
		var item = data[k];
		var markerPoint;

		if(item.range == "1"){
			var pos = item.longitude_latitude.split(',');
			markerPoint = new BMap.Point(parseFloat(pos[0]),parseFloat(pos[1]));
		}else{
			var points = item.longitude_latitude.split(';');
			var polyarray = new Array();

			for(var i = 0; i < points.length - 1; i++){
				var p = points[i].split(',');
				var bpoint = new BMap.Point(parseFloat(p[0]),parseFloat(p[1]));
				polyarray.push(bpoint);
			}

			var polyline = new BMap.Polyline(polyarray, {strokeColor:"red", strokeWeight:6, strokeOpacity:0.8});
			map.addOverlay(polyline);
			overlays.push(polyline);

			markerPoint = polyarray[0];
		}
		
		var icon = new BMap.Icon("/media/" + item.event_type_icon, new BMap.Size(50,63));
		var marker = new BMap.Marker(markerPoint, {icon:icon});
		marker.index = k;
		map.addOverlay(marker);
		overlays.push(marker);

		marker.addEventListener("click", function(){  
			var d = data[this.index];
			var opts = {
			  width : 300,
			  height: 200,
			  title : '路况信息',
			  enableMessage:false
			}
			
			var content = d.road_name + d.start_km + "公里至" + d.end_km + "公里" + d.section;
			content += "<br>详情：" + d.content;
			content += "<br>发布时间：" + d.happen_time + "<br>预计结束时间：" + d.duration;
			content += "<br>事件后果：" + d.consequences;

			var infoWindow = new BMap.InfoWindow(content, opts);					
			map.openInfoWindow(infoWindow,this.getPosition()); 
		});
	}
}

function renderAccidentSection(data){
	for(var k in data){
		var item = data[k];
		var pt = new BMap.Point(parseFloat(item.longitude),parseFloat(item.latitude));

		var icon = new BMap.Icon("/static/images/ico_accident_section.png", new BMap.Size(40,50));
		var marker = new BMap.Marker(pt, {icon:icon});
		marker.index = k;
		map.addOverlay(marker);
		overlays.push(marker);

		marker.addEventListener("click", function(){  
			var d = data[this.index];
			var opts = {
			  width : 200,
			  height: 100,
			  title : '事故易发路段',
			  enableMessage:false
			}
			var content = "预警类别：" + d.consequences_text + "<br>" + d.warn_content;
			var infoWindow = new BMap.InfoWindow(content, opts);					
			map.openInfoWindow(infoWindow,this.getPosition()); 
		});
	}
}

function renderReport(data){
	for(var k in data){
		var item = data[k];
		var pt = new BMap.Point(parseFloat(item.longitude),parseFloat(item.latitude));

		var icon = new BMap.Icon("/static/images/ico_report.png", new BMap.Size(40,50));
		var marker = new BMap.Marker(pt, {icon:icon});
		marker.index = k;
		map.addOverlay(marker);
		overlays.push(marker);

		marker.addEventListener("click", function(){  
			var d = data[this.index];
			var opts = {
			  width : 300,
			  height: 150,    
			  title : "网友互动",
			  enableMessage:false
			}
			var content = "用户：" + d.create_user_name + "<br>时间：" + d.create_time + "<br>爆料：" + d.text + "<div style='padding:5px'>";
			if(d.image) content += "<br><a href='"+d.image+"' target='_blank'><img src='/media/"+d.image+"' width='50px'></a>"
			if(d.voice) content += "<a href='/media/"+d.voice+"' target='_blank'><img src='/static/images/play.png' style='float:right;margin-top:20px'></a>"
			content += "</div>";
			var infoWindow = new BMap.InfoWindow(content, opts);					
			map.openInfoWindow(infoWindow,this.getPosition()); 
		});
	}
}

function renderAlarm(data){
	for(var k in data){
		var item = data[k];
		var pt = new BMap.Point(parseFloat(item.longitude),parseFloat(item.latitude));

		var icon = new BMap.Icon("/static/images/ico_alerm_"+item.status+".png", new BMap.Size(40,50));
		var marker = new BMap.Marker(pt, {icon:icon});
		marker.index = k;
		map.addOverlay(marker);
		overlays.push(marker);

		marker.addEventListener("click", function(){  
			var d = data[this.index];
			var opts = {
			  width : 250,
			  height: 100,    
			  title : '报警',
			  enableMessage:false
			}
			var content = "用户：" + d.create_uuid + "<br>时间：" + d.create_time + "<br>手机：" + d.create_number;
			var infoWindow = new BMap.InfoWindow(content, opts);					
			map.openInfoWindow(infoWindow,this.getPosition()); 
		});
	}
}


function renderCamera(data){
	for(var k in data){
		var item = data[k];
		var pt = new BMap.Point(parseFloat(item.longitude),parseFloat(item.latitude));

		var icon = new BMap.Icon("/static/images/ico_camera.png", new BMap.Size(40,50));
		var marker = new BMap.Marker(pt, {icon:icon});
		marker.index = k;
		map.addOverlay(marker);
		overlays.push(marker);

		marker.addEventListener("click", function(){  
			var d = data[this.index];
			var opts = {
			  width : 352,
			  height: 288,
			  title : d.road,
			  enableMessage:false
			}
			var content = "";
			if(d.image) content += "<a href='/media/"+d.image+"' target='_blank'><img src='/media/"+d.image+"' width='352px'></a>"

			var infoWindow = new BMap.InfoWindow(content, opts);
			map.openInfoWindow(infoWindow,this.getPosition()); 
		});
	}
}

function renderWeather(data){
	for(var k in data){
		var item = data[k];
		var pt = new BMap.Point(parseFloat(item.longitude),parseFloat(item.latitude));

		var icon = new BMap.Icon("/static/images/weather/" + item.icon, new BMap.Size(40,50));
		var marker = new BMap.Marker(pt, {icon:icon});
		marker.index = k;
		map.addOverlay(marker);
		overlays.push(marker);

		marker.addEventListener("click", function(){  
			var d = data[this.index];
			var opts = {
			  width : 15,
			  height: 60,    
			  title : d.city,
			  enableMessage:false
			}
			var content = "天气：" + d.weather + "<br>温度：" + d.temputer;
			var infoWindow = new BMap.InfoWindow(content, opts);					
			map.openInfoWindow(infoWindow,this.getPosition()); 
		});
	}
}