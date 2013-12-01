'use strict';

var dayOfWeekChart = dc.rowChart('#day-week-chart');
var moveChart = dc.barChart('#move-chart');
var sentimentChart = dc.lineChart("#sentiment-chart");

d3.json('assets/data/sentiment.json', function(data) {
	var dateFormat = d3.time.format('%a, %d %b %Y %H:%M:%S %Z');

	data.forEach(function(d) {
		d.dd = dateFormat.parse(d.published);
		d.month = d3.time.month(d.dd);
		d.votes = +d.votes;
		d.arousal = +d.sentiments.description.arousal;
		d.valence = +d.sentiments.description.valence;
	});

	var ndx = crossfilter(data);
	var all = ndx.groupAll();

	var dateDimension = ndx.dimension(function (d) {
		return d.dd;
	});

	var monthlyDimension = ndx.dimension(function (d) {
		return d.month;
	});

	var voteDimension = ndx.dimension(function (d) {
		return d.votes;
	});

	var arousalDimension = ndx.dimension(function (d) {
		return d.arousal;
	});

	var dayOfWeek = ndx.dimension(function (d) {
        var day = d.dd.getDay();
        var name=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
        return day+"."+name[day];
     });

    var dayOfWeekGroup = dayOfWeek.group();

	var monthlyArousalGroup = monthlyDimension.group().reduceSum(function (d) {
		return d.arousal;
	});

	var monthlyValenceGroup = monthlyDimension.group().reduceSum(function (d) {
		return d.valence;
	});

	var valenceAvgByMonthGroup = monthlyDimension.group().reduceSum(function (d) {
		return d.valence;
    });

	dayOfWeekChart.width(180)
        .height(260)
        .margins({top: 20, left: 10, right: 10, bottom: 20})
        .group(dayOfWeekGroup)
        .dimension(dayOfWeek)
        .ordinalColors(colorbrewer.Oranges[7])
        .label(function (d) {
            return d.key.split(".")[1];
        })
        .title(function (d) {
            return d.value;
        })
        .elasticX(true)
        .xAxis().ticks(4);

   	sentimentChart
        .renderArea(true)
        .width(990)
        .height(200)
        .transitionDuration(1000)
        .margins({top: 30, right: 50, bottom: 25, left: 40})
        .dimension(monthlyDimension)
        .mouseZoomable(true)
        .rangeChart(moveChart)
        .x(d3.time.scale().domain([new Date(2012, 7, 1), new Date(2013, 9, 1)]))
        .round(d3.time.month.round)
        .xUnits(d3.time.months)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5))
        .brushOn(false)
        .group(valenceAvgByMonthGroup, "Monthly Index Average")
        .valueAccessor(function (d) {
            return d.value;
        })
        .stack(monthlyValenceGroup, "Monthly Index Move", function (d) {
            return d.value;
        })
        .title(function (d) {
            var value = d.value.avg ? d.value.avg : d.value;
            if (isNaN(value)) value = 0;
            return dateFormat(d.key) + "\n" + value;
        });

  	 moveChart.width(990)
        .height(200)
        .margins({top: 20, right: 50, bottom: 20, left: 40})
        .dimension(monthlyDimension)
        .group(monthlyValenceGroup)
        .ordinalColors(['#fd8d3c'])
        .centerBar(true)
        .gap(10)
        .x(d3.time.scale().domain([new Date(2012, 7, 1), new Date(2013, 9, 1)]))
        .round(d3.time.month.round)
        .xUnits(d3.time.months);

   	dc.renderAll();

});