$(function(){
    $(".feature").click(function(){
        $(".selected").removeClass('selected');
        $(this).addClass('selected');
        var type = $(this).attr('type');
        var featurevalue = $(this).attr('featurevalue');
        var featurename = $(this).attr('featurename');
        var devicename = $(this).attr('devicename');
        $("#widgetslist").empty();
        $("#widgets").show();
        $("#widgetslist").widget_models({
            type: type,
            featurevalue: featurevalue,
            featurename: featurename,
            devicename: devicename
        });
    });

    $("#widgets").hide();
});

(function($) {
    function ondrop(event, ui) {
        var item = ui.draggable.detach();
        item.removeAttr('style');
        item.addClass('success');
        item.dmg_draggable({
            helper: false,
            revert: false
        });
        $(this).append(item);
        $.addAssociation(item, $(this), 'house', 0);            
        return false;
    }
        
    /* Mini Widget */
    $.ui.widget.subclass("ui.widget_models", {
        // default options
        options: {
        },

        _init: function() {
            var self = this, o = this.options;
            this.element.empty();
            var widgets = get_widgets(o.type);
            $.each(widgets, function(index, id) {
                var woptions = get_widgets_options(id);
//                var filter = woptions.filter
                var widget = $("<li></li>");
                var name = $("<div class='name'>" + woptions.name + "</div>");
                widget.append(name);
                var name = $("<div class='description'>" + woptions.description + "</div>");
                widget.append(name);
                var model = $("<div></div>");
                model.widget_model({
                    id: id,
                    featurevalue: o.featurevalue,
                    featurename: o.featurename,
                    devicename: o.devicename
                });
                model.draggable({
                    helper: "clone",
                    revert: 'invalid',
                    appendTo: 'body',
                    drag: function(event, ui) {
                        $("#panel").hide();
                        var association = $(this).attr('id');
                        if (association) {
                            $.getREST(['base', 'feature_association', 'del', association],
                                function(data) {
                                    var status = (data.status).toLowerCase();
                                    if (status == 'ok') {
                                        $.getREST(['base', 'ui_config', 'del', 'by-reference', 'association', association],
                                            function(data) {
                                                var status = (data.status).toLowerCase();
                                                if (status == 'ok') {
                                                } else {
                                                    $.notification('error', data.description);                                          
                                                }
                                            }
                                        );
                                    } else {
                                        $.notification('error', data.description);                                          
                                    }
                                }
                            );
                        }
                    },
                    stop: function(event, ui) {
                        $("#panel").show();
                        self._init();
                        if($(this).hasClass("success")) {
                            $(this).removeClass("success");
                        } else {
                            $(this).remove();			
                        }
                    }
                });
                widget.append(model);
                self.element.append(widget); 
            });
        },
	
        update: function() {
            this._init();
        }
    });
    
    $.ui.widget.subclass("ui.widget_model", {
        // default options
        options: {
        },

        _init: function() {
            var self = this, o = this.options;
            var woptions = get_widgets_options(o.id)
            if (woptions) {
                o = $.extend ({}, woptions, o);
            }

            this.element.addClass('model')
                .attr('role', 'listitem')
			    .attr("widgetid", o.id)
				.addClass('size' + o.width + 'x' + o.height)
                .attr("tabindex", 0)
	            .attr('featurevalue', o.featurevalue)
                .text(o.width + 'x' + o.height);
			this._identity = $("<canvas class='identity' width='60' height='60'></canvas>")
			this.element.append(this._identity);				
			var canvas = this._identity.get(0);
			if (canvas.getContext){
				var ctx = canvas.getContext('2d');
				ctx.beginPath();
				ctx.font = "6pt Arial";
				ctx.textBaseline = "top"
				ctx.fillText(o.devicename, 15, 5);
				ctx.translate(5,60);
				ctx.rotate(-(Math.PI/2));
				ctx.fillText(o.featurename, 0, 0);  
			}
        },
        
        hasSize: function(width, height) {
            var woptions = get_widgets_options(this.options.id)
            return (width == woptions.width && height == woptions.height);
        }
    });
    
    $.extend({
        addAssociation: function(model, zone) {
            var page_type = zone.attr('page_type');
            var page_id = zone.attr('page_id');
            var widget_id = model.attr('widgetid');
            var place_id = zone.attr('place');
            $.getREST(['base', 'feature_association', 'add', 'feature_id', model.attr('featurevalue'), 'association_type', page_type, 'association_id', page_id],
                function(data) {
                    var status = (data.status).toLowerCase();
                    if (status == 'ok') {
                        var id = data.feature_association[0].id;
                        $.getREST(['base', 'ui_config', 'set', 'name', 'association', 'reference', id, 'key', 'widget', 'value', widget_id],
                            function(data) {
                                var status = (data.status).toLowerCase();
                                if (status == 'ok') {
                                    $.getREST(['base', 'ui_config', 'set', 'name', 'association', 'reference', id, 'key', 'place', 'value', place_id],
                                        function(data) {
                                            var status = (data.status).toLowerCase();
                                            if (status == 'ok') {
                                            } else {
                                                $.notification('error', data.description);                                          
                                            }
                                        }
                                    );
                                } else {
                                    $.notification('error', data.description);                                          
                                }
                            }
                        );
                    } else {
                        $.notification('error', data.description);                                          
                    }
                }
            );
        },
        
        initAssociations: function(page_type, page_id) {
            $('.maininfo').droppable({
                    activeClass: 'state-active',
                    hoverClass: 'state-hover',
                    accept: function(draggable) {
                        return (($(".model", this).length  < 1) && draggable.widget_model('hasSize', 1, 1));
                    },
                    drop: ondrop
            }).attr('place', 'maininfo')
                .attr('page_type', page_type)
                .attr('page_id', page_id);
            
            $('.mainactions').droppable({
                    activeClass: 'state-active',
                    hoverClass: 'state-hover',
                    accept: function(draggable) {
                        return (($(".model", this).length  < 4) && draggable.widget_model('hasSize', 1, 1));
                    },
                    drop: ondrop
            }).attr('place', 'mainactions')
                .attr('page_type', page_type)
                .attr('page_id', page_id);
            
            $('.otheractions').droppable({
                    activeClass: 'state-active',
                    hoverClass: 'state-hover',
                    drop: ondrop
            }).attr('place', 'otheractions')
                .attr('page_type', page_type)
                .attr('page_id', page_id);
    
            var options = null;
            if (page_type == 'house') {
                options = ['base', 'feature_association', 'list', 'by-house']
            } else {
                options = ['base', 'feature_association', 'list', 'by-' + page_type, page_id];
            }
            $.getREST(options,
                function(data) {
                    var status = (data.status).toLowerCase();
                    if (status == 'ok') {
                        $.each(data.feature_association, function(index, association) {
                            $.getREST(['base', 'ui_config', 'list', 'by-reference', 'association', association.id],
                                function(data) {
                                    var status = (data.status).toLowerCase();
                                    if (status == 'ok') {
                                        var widget = null;
                                        var place = null;
                                        $.each(data.ui_config, function(index, item) {
                                            if (item.key == 'widget') widget = item.value;
                                            if (item.key == 'place') place = item.value;
                                        });
                                        $.getREST(['base', 'feature', 'list', 'by-id', association.device_feature_id],
                                            function(data) {
                                                var status = (data.status).toLowerCase();
                                                if (status == 'ok') {
                                                    var model = $("<div id='" + association.id + "' role='listitem'>1x1</div>");
                                                    model.attr('association', association.id);
                                                    model.widget_model({
                                                        id: widget,
                                                        featurevalue: association.device_feature_id,
                                                        featurename: data.feature[0].device_feature_model.name,
                                                        devicename: data.feature[0].device.name
                                                    })
                                                    .draggable({
                                                        helper: false,
                                                        revert: false,
                                                        appendTo: 'body',
                                                        drag: function(event, ui) {
                                                            $("#panel").hide();
                                                            var association = $(this).attr('id');
                                                            if (association) {
                                                                $.getREST(['base', 'feature_association', 'del', 'id', association],
                                                                    function(data) {
                                                                        var status = (data.status).toLowerCase();
                                                                        if (status == 'ok') {
                                                                            $.getREST(['base', 'ui_config', 'del', 'by-reference', 'association', association],
                                                                                function(data) {
                                                                                    var status = (data.status).toLowerCase();
                                                                                    if (status == 'ok') {
                                                                                    } else {
                                                                                        $.notification('error', data.description);                                          
                                                                                    }
                                                                                }
                                                                            );
                                                                        } else {
                                                                            $.notification('error', data.description);                                          
                                                                        }
                                                                    }
                                                                );
                                                            }
                                                        },
                                                        stop: function(event, ui) {
                                                            $("#panel").show();
                                                            $("#widgetslist").widget_models('update');
                                                            if($(this).hasClass("success")) {
                                                                $(this).removeClass("success");
                                                            } else {
                                                                $(this).remove();			
                                                            }
                                                        }
                                                    });
                                                    $("." + place).append(model);
                                                } else {
                                                    $.notification('error', data.description);                                          
                                                }
                                            }
                                        );
                                    } else {
                                        $.notification('error', data.description);                                          
                                    }
                                }
                            );
                        });
                    } else {
                        $.notification('error', data.description);                                          
                    }
                }
            );
        }
    });
})(jQuery);