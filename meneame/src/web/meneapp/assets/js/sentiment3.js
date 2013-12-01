'use strict';

//var dayOfWeekChart = dc.rowChart('#day-week-chart');
var moveChart = dc.barChart('#day-week-chart');
var scatterChart = dc.bubbleChart('#move-chart');
var sentimentChart = dc.compositeChart("#sentiment-chart");

d3.json('assets/data/sentiment_description.json', function(data) {
	var dateFormat = d3.time.format('%Y-%m-%d');
	
    data.forEach(function(d) {
		d.dd = dateFormat.parse(d.date);
        d.week = d3.time.week(d.dd);
        d.votes = +d.votes;
        d.titles = d.title;
		d.arousal = +d.arousal;
		d.valence = +d.valence;
	});

	var ndx = crossfilter(data);
	var all = ndx.groupAll();

    var dayDimension = ndx.dimension(function(d) {
        return d.dd;
    });

    var sentDimension = ndx.dimension(function(d) {
        return [+d.arousal, +d.valence, d.titles];
    });

    var dailyArousal = dayDimension.group().reduceSum(function(d) {
        return d.arousal;
    });

    var dailyValence = dayDimension.group().reduceSum(function(d) {
        return d.valence;
    });

    var dailyVotes = dayDimension.group().reduceSum(function(d) {
        return d.votes;
    });

    var sentGroup = sentDimension.group();

    // compose the given charts in the array into one single composite chart
    sentimentChart
        .width(990)
        .height(300)
        .elasticY(true)
        .brushOn(false)
        .x(d3.time.scale().domain([new Date(2012, 9, 1), new Date(2013, 9, 1)]))
        .round(d3.time.day)
        .xUnits(d3.time.weeks)
    .compose([
    // when creating sub-chart you need to pass in the parent chart
     dc.lineChart(sentimentChart)
        .renderArea(true)
        .transitionDuration(1000)
        .margins({top: 30, right: 50, bottom: 25, left: 40})
        .dimension(dayDimension)
        .mouseZoomable(true)

        .rangeChart(moveChart)  
        .renderHorizontalGridLines(true)
        .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5))
        .brushOn(false)
        .group(dailyArousal, "Daily Valence Average")
        .valueAccessor(function (d) {
            return d.value;
        }),
        dc.lineChart(sentimentChart)
            .renderArea(true)
            .transitionDuration(1000)
            .margins({top: 30, right: 50, bottom: 25, left: 40})
            .dimension(dayDimension)
            .mouseZoomable(true)
            .colors(["#a60000"])
            .rangeChart(moveChart)  
            .renderHorizontalGridLines(true)
            .legend(dc.legend().x(800).y(10).itemHeight(13).gap(5))
            .brushOn(false)
            .group(dailyValence, "Daily Valence Average")
            .valueAccessor(function (d) {
                return d.value;
            })
    ] );

    moveChart
        .width(1000)
        .height(100)
        .margins({top: 20, right: 50, bottom: 20, left: 40})
        .dimension(dayDimension)
        .group(dailyVotes)
        .ordinalColors(['#fd8d3c'])
        .centerBar(true)
        .gap(15)
        .x(d3.time.scale().domain([new Date(2012, 9, 1), new Date(2013, 9, 1)]))
        .round(d3.time.day)
        .xUnits(d3.time.weeks);

    scatterChart
        .width(990) // (optional) define chart width, :default = 200
        .height(990)  // (optional) define chart height, :default = 200
        .transitionDuration(1500) // (optional) define chart transition duration, :default = 750
        .margins({top: 10, right: 50, bottom: 30, left: 40})
        .dimension(sentDimension)
        .group(sentGroup)
        .colors(colorbrewer.RdYlGn[9]) // (optional) define color function or array for bubbles
        .colorDomain([0, 24]) //(optional) define color domain to match your data domain if you want to bind data or color
        .colorAccessor(function (p) {
            if (p.key[0] > 5.48 && p.key[1] > 5.48) {
                return 24;
            }
            if (p.key[1] > 5.48 && p.key[0] < 5.48) {
                return 18;
            }
            if (p.key[1] < 5.48 && p.key[0] > 5.48) {
                return 12;
            }
            if (p.key[1] < 5.48 && p.key[0] < 5.48) {
                return 6;
            }
        })
        .keyAccessor(function (p) {
            return p.key[0];
        })
        .valueAccessor(function (p) {
            return p.key[1];
        })
        .radiusValueAccessor(function (p) {
            return 5;
        })
        .maxBubbleRelativeSize(0.3)
        .x(d3.scale.linear().domain([0, 12]))
        .y(d3.scale.linear().domain([0, 12]))
        .r(d3.scale.linear().domain([0, 4000]))
        .elasticY(true)
        .elasticX(true)
        .renderLabel(false)
        .renderTitle(true) // (optional) whether chart should render titles, :default = false
        .title(function (p) {
            return [p.key[2]];
        })
        .renderHorizontalGridLines(true) // (optional) render horizontal grid lines, :default=false
        .renderVerticalGridLines(true) // (optional) render vertical grid lines, :default=false
        .xAxisLabel('Arousal') // (optional) render an axis label below the x axis
        .yAxisLabel('Valence'); // (optional) render a vertical axis lable left of the y axis

   	dc.renderAll();

});