$(document).ready(function(){
	//slides the element with class "menu_body" when paragraph with class "menu_head" is clicked 
	$("p.menu_head").click(function()
    {
		var self = $(this);
		self.next("ul.menu_body").slideToggle(300, function(){
			var img = $(this).css('display') == "none" ? 'arrow_down.png' : 'arrow_up.png';
			self.children("span").css({backgroundImage:"url(/static/images/"+img+")"});
		});
		
		var others = self.parent().siblings();
		others.children("ul.menu_body").slideUp("slow");
		others.children("span").css({backgroundImage:"url(/static/images/arrow_up.png)"});
       	//$(this).parent().siblings().children("p").children("span").css({backgroundImage:"url(/static/images/arrow_down.png)"});
	});

	$("#nav a").click(function()
    {
		$("#nav a").removeClass("current");
		$(this).addClass("current");
		$("#page").attr("src", $(this).attr("page"));
	});


	$(window).resize();
});

$(window).resize(function() {
	$("#container").height($(window).height() - $("#header").height());
	$("#page").height($(window).height() - $("#header").height());
	$("#page").width($(window).width() - 231);
});


function showDialog(title, callback){
	$('#dlg').dialog('open').dialog('setTitle',title);
	if(callback != undefined)
		callback();
}

function closeDialog() {
    $('#dlg').dialog('close');
}

