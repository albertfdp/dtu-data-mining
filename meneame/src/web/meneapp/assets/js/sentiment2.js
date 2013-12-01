'use strict';

//var dayOfWeekChart = dc.rowChart('#day-week-chart');
var moveChart = dc.barChart('#move-chart');
var sentimentChart = dc.lineChart("#sentiment-chart");

d3.json('assets/data/sentiment.json', function(data) {
	var dateFormat = d3.time.format('%a, %d %b %Y %H:%M:%S %Z');

	data.forEach(function(d) {
		d.dd = dateFormat.parse(d.published);
		d.week = d3.time.week(d.dd);
        d.month = d3.time.month(d.dd);
		d.votes = +d.votes;
		d.arousal = +d.sentiments.comments.arousal;
		d.valence = +d.sentiments.comments.valence;
	});

	var ndx = crossfilter(data);
	var all = ndx.groupAll();

    var dateDimension = ndx.dimension(function(d) {
        return d.dd;
    });

    var weeklyDimension = ndx.dimension(function(d) {
        return d.dd;
    })

    var monthlyDimension = ndx.dimension(function(d) {
        return d.month;
    });

    var averageArousalByWeekGroup = weeklyDimension.group().reduce(

        function (p, v) {
            ++p.days;
            p.total += v.arousal;
            p.avg = p.total / p.days;
            return p;
        },
        function (p, v) {
            --p.days;
            p.total -= v.arousal;
            p.avg = p.days ? p.total / p.days : 0;
        },
        function () {
            return {days: 0, total: 0, avg: 0};
        }

    );

    var averageValenceByWeekGroup = weeklyDimension.group().reduce(

        function (p, v) {
            ++p.days;
            p.total += v.valence;
            p.avg = p.total / p.days;
            return p;
        },
        function (p, v) {
            --p.days;
            p.total -= v.valence;
            p.avg = p.days ? p.total / p.days : 0;
        },
        function () {
            return {days: 0, total: 0, avg: 0};
        }

    );

    var weeklyVotesGroup = weeklyDimension.group().reduceSum(function(d) {
        return d.votes;
    });

    var monthlyVotesGroup = monthlyDimension.group().reduceSum(function(d) {
        return d.votes;
    });

    sentimentChart
        .renderArea(true)
        .width(990)
        .height(300)
        .transitionDuration(1000)
        .margins({top: 30, right: 50, bottom: 25, left: 40})
        .dimension(weeklyDimension)
        .mouseZoomable(true)

        .rangeChart(moveChart)        
        .elasticY(true)
        .x(d3.time.scale().domain([new Date(2012, 9, 1), new Date(2013, 9, 1)]))
        .round(d3.time.week.round)
        .xUnits(d3.time.weeks)
        .renderHorizontalGridLines(true)
        .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5))
        .brushOn(false)
        .group(averageValenceByWeekGroup, "Weekly Valence Average")
        .valueAccessor(function (d) {
            return d.value.avg;
        })
        .stack(averageArousalByWeekGroup, "Weekly Arousal Average", function (d) {
            return d.value.avg;
        })
        .title(function (d) {
            var value = d.value.avg ? d.value.avg : d.value;
            if (isNaN(value)) value = 0;
            return dateFormat(d.key) + "\n" + value;
        });

    moveChart
        .width(1000)
        .height(100)
        .margins({top: 20, right: 50, bottom: 20, left: 40})
        .dimension(monthlyDimension)
        .group(monthlyVotesGroup)
        .ordinalColors(['#fd8d3c'])
        .centerBar(true)
        .gap(1)
        .x(d3.time.scale().domain([new Date(2012, 7, 1), new Date(2013, 9, 1)]))
        .round(d3.time.week.round)
        .xUnits(d3.time.weeks);

   	dc.renderAll();

});