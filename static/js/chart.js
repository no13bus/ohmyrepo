$(function () {
            Highcharts.setOptions({
                global: {
                    useUTC: false //开启UTC
                }
            });

            var chart = new Highcharts.Chart({
                chart: {
                    type: 'line',
                    renderTo: 'star_chart'
                },
                title: {
                    text: 'Stars'
                },
                subtitle: {
                    text: 'show stars'
                },
                xAxis: {
                    type: 'datetime',
                    title: {
                        text: 'Time'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Star Number'
                    },

                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',

                    pointFormat: 'time: {point.x:%Y-%m-%e} <br> num: {point.y}'
                },

                series: [{
                    name: 'star number'
                }]
            });


            var stars_data=[];
            var cities_data=[];
            var follows_data = [];
            function getForm(){

                $.ajax({
                    url: "{{ stars_url }}",
                    dataType:"json",
                    async:false,
                    success:function(point){
                  var obj=eval(point);
                  if (obj['status'] == 1) {
                      for (var i=0; i<obj['result'].length; i++){
                        stars_data.push({x:Date.parse(obj['result'][i]['_id']),y:parseFloat(obj['result'][i]['num'])});
                      }
                  }else{
                      $('#star_chart').hide();
                  }
                },
                    error: function(){alert('Show stars map error!')}
                });
                chart.series[0].setData(stars_data);

                $.ajax({
                    url: "{{ cities_url }}",
                    dataType:"json",
                    async:false,
                    success:function(point){
                  var obj=eval(point);
                  if (obj['status'] == 1) {
                      for (var i=0; i<obj['result'].length; i++){
                        cities_data.push({code:obj['result'][i]['_id'], value:obj['result'][i]['num']});
                      }
                  }else{
                      $('#city_chart').hide();
                  }
                },
                    error: function(){alert('Show cities error!')}
                });

                $.ajax({
                    url: "{{ follows_url }}",
                    dataType:"json",
                    async:false,
                    success:function(point){
                  var obj=eval(point);
                  if (obj['status'] == 1) {
                      /// 添加table和tr td
                      for (var i=0; i<obj['result'].length; i++){
                          var $tr = $("<tr></tr>");
                          var $td = $("<td>" + (i+1) + "</td>")
                          var $td1 = $("<td><a target='_blank' href='https://github.com/" + obj['result'][i]['sender_name'] + "'>" + "<img src='" + obj['result'][i]['avatar_url'] + "' style='width: 20px; height:20px;'/>" + obj['result'][i]['sender_name'] + "</a></td>");
                          var $td2 = $("<td>" + obj['result'][i]['followers'] + "</td>");
                          var $td3 = $("<td><a name=" + obj['result'][i]['sender_name'] +" id='follow' href='/f?u=" + obj['result'][i]['sender_name'] + "' class='btn btn-info btn-sm' role='button'><i class='fa fa-github-alt'></i>Follow</a></td>");
                          $tr.append($td);
                          $tr.append($td1);
                          $tr.append($td2);
                          $tr.append($td3);
                          $("#follow_chart").append($tr);
                      }

                  }else{
                      $('#follow_chart').hide();
                  }
                },
                    error: function(){alert('Show followers error!')}
                });


            }
            getForm();
            $('a#follow').each(function(i){
                $(this).click(function(){
                        var $that = $(this);
                        var f_url = $that.attr("href");
                        $.ajax({
                            url: f_url,
                            dataType:"json",
                            async:false,
                            success:function(resp) {
                                var obj=eval(resp);
                                console.log(obj);
                                if (obj['status'] == 1){
                                    if ($that.text() == 'Unfollow'){
                                        $that.attr("href", "/f?u="+$that.attr("name"));
                                        $that.attr("class", "btn btn-info btn-sm");
                                        $that.html("<i class='fa fa-github-alt'></i>Follow");
                                    }else{
                                        $that.attr("href", "/uf?u="+$that.attr("name"));
                                        $that.attr("class", "btn btn-default btn-sm");
                                        $that.html("<i class='fa fa-github-alt'></i>Unfollow");
                                    }
                                }else{
                                    alert('follow faiture!');
                                }
                            },
                            error: function(XMLHttpRequest, textStatus, errorThrown){
                               alert("You should login first or maybe there are some errors in the server.")

                            }
                        });
                        return false;
                    }
                );


            });


            $('#city_chart').highcharts('Map', {
                    chart : {
                        type: 'map'
                    },
                    title : {
                        text : 'Followers'
                    },
                    subtitle : {
                        text : 'show followers'
                    },
                  mapNavigation: {
                        enabled: true,
                        buttonOptions: {
                            verticalAlign: 'bottom'
                        }
                    },

                    colorAxis: {
                        min: 0,
                        stops: [
                            [0, '#EFEFFF'],
                            [0.5, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).brighten(-0.5).get()]
                        ]
                    },
                    series : [{
                        name: 'Follows',
                        mapData: Highcharts.maps['custom/world'],
                        data: cities_data,
                        states: {
                            hover: {
                                borderWidth: 1
                            }
                        },
                        joinBy: ['iso-a2', 'code'],
                        tooltip: {
                            valueSuffix: ''
                        }
                    }]
                });





});