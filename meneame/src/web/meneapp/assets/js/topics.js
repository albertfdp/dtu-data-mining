// Chart dimensions.
var margin = {top: 50.5, right: 39.5, bottom: 19.5, left: 59.5},
    width = 1160 - margin.right,
    height = 700 - margin.top - margin.bottom;

// Various scales. These domains make assumptions of data, naturally.
var xScale = d3.time.scale().range([0, width]),
    yScale_log = d3.scale.log().range([height, 0]).nice(),
    radiusScale = d3.scale.sqrt().range([0, 40]),
    colorScale = d3.scale.category10();

    yScale_linear = d3.scale.linear().range([height, 0]);

// The x & y axes.
var xAxis = d3.svg.axis().orient("bottom").scale(xScale).ticks(12, d3.format(",d")),
    yAxis = d3.svg.axis().scale(yScale_log).orient("left");

// Create the SVG container and set the origin.
var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


// Add an x-axis label.
svg.append("text")
    .attr("class", "x label")
    .attr("text-anchor", "end")
    .attr("x", width)
    .attr("y", height - 6)
    .text("Date of the Time Slice");

// Add a y-axis label.
svg.append("text")
    .attr("class", "y label")
    .attr("text-anchor", "end")
    .attr("y", 6)
    .attr("dy", ".75em")
    .attr("transform", "rotate(-90)")
    .text("Number of votes of each Topic");
    
    
d3.json('assets/data/topic_news.json', function(data) {
    var dateFormat = d3.time.format('%d-%m-%Y-');
    
    var news = [];    
    for( var i in data ) {
        if (data[i].slice_date != undefined){        
            var t = data[i].slice_date.split("/");
            var date = new Date(t[2],t[1]-1,t[0]);
            news.push({
                "slice_date" : date,
                "week" : d3.time.week(date),
                "description" : data[i].description,
                "title" : data[i].title,
                "votes" : +data[i].votes,
                "slice_id" : +data[i].slice_id,
                "topic_id" : +data[i].topic_id
            });
        }
	};    
    console.log(news);
    /* Create Crossfilter */
    var news_set = crossfilter(news);
    
    /* Dimensions */
    var newsByTopic = news_set.dimension(function(d) { return d.topic_id; });
    var topicPlusDate = news_set.dimension(function(d) { return d.slice_date+"-"+d.topic_id; });
    
    /* Y Axis */
    var topicsGroupedByVotes = newsByTopic.group().reduceSum(function(d) { return d.votes; });
    
    /* Size of Bubble: Number of news per topic */
    var news_per_topic = topicPlusDate.group();

    var dictVotesPerTopic = d3.nest()
        .key(function(d){ return d.key;})
        .map(topicsGroupedByVotes.all().filter(function(d){return d.key!=undefined}), d3.map);
    
    /* Title for each topic */
    var titlesPerTopic = news_set.dimension(function(d) { return d.topic_id+"-"+d.title; });
    /*  dict */
    var titles_dict = d3.nest()
        .key(function(d){ var t = d.key.split("-"); return t[0];})
        .rollup(function(d){
            var aux = ["Meneame News: "+ d.length+" articles",''];
            d.forEach(function(dd){
                var t = dd.key.split("-");
                aux.push(t[1]);
            });  
            return aux.join("\n");      
        
        })
        .map(titlesPerTopic.group().all().filter(function(d){return d.key!=undefined}), d3.map);

    //console.log(titles_dict);
    
    // Create Dataset: Slice_date(x) : {Votes: Y, Radius: N_of_news}
    var total_data = d3.nest()
        .key(function(d) { var t = d.key.split("-"); return t[0]; })
        .rollup(function(d){
            var aux = [];
            d.forEach(function(dd){
                var t = dd.key.split("-");
                if (dictVotesPerTopic.get(t[1]) != undefined)
                    aux.push({
                        "votes": dictVotesPerTopic.get(t[1])[0].value,
                        "radius": dd.value,
                        "titles": titles_dict.get(t[1])});         
            });
            return aux;
            
        })
        .sortKeys(function(a, b) {
                var a = new Date(Date.parse(a)),
                    b = new Date(Date.parse(b))
                return b < a ? 1 : b > a ? -1 : 0;
        })
        .entries(news_per_topic.all());
    
    console.log(total_data);
    
    // Create Viz
    
    // Calculate domains
/*
    xScale.domain([new Date(Date.parse(total_data[0].key)),
                 new Date(Date.parse(total_data[total_data.length-1].key))]);
*/
           
    var ini_date = [new Date(Date.parse(total_data[0].key)),
                 new Date(Date.parse(total_data[total_data.length-1].key))]; 
                             
    xScale.domain([new Date(ini_date[0].getFullYear(),ini_date[0].getMonth()-1,20),
                 new Date(ini_date[1].getFullYear(),ini_date[0].getMonth()+1,10)]);                 
    yScale_log.domain([d3.min(dictVotesPerTopic.values(),function(d){
        return d[0].value;
        }),d3.max(dictVotesPerTopic.values(),function(d){
        return d[0].value;
    })]);

    radiusScale.domain([
        d3.min(newsByTopic.group().all(), function(d){return d.value;})
        ,d3.max(newsByTopic.group().all(), function(d){return d.value;})]);  

    // Add the x-axis.
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    
    // Add the y-axis.
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);
    

    
    console.log([new Date(Date.parse(total_data[0].key)),
                 new Date(Date.parse(total_data[total_data.length-1].key))]);
    console.log([0,d3.max(dictVotesPerTopic.values())[0].value]);
    console.log([0,d3.max(news_per_topic.all(),function(d){return d.value;})]);
    


    svg.append("g").selectAll(".slice")
        .data(total_data,function(d){return d.key;})
    .enter().append("g")
    .attr("transform",function(d){
            return "translate("+xScale(new Date(Date.parse(d.key)))+",0)"; })
    .each(function(dd){
            
        var dot = d3.select(this).selectAll(".dot")
        .data(dd.values)
        .enter().append("circle")
          .attr("class", "dot")
          .style("fill", function(d) { "steelblue"; })
          ;

      // Add a title.
      dot.append("title")
          .text(function(d) { return d.titles; });
          
      dot.attr("cy", function(d) {return yScale_log(d.votes); })
        .attr("r", function(d) { return radiusScale(d.radius); });
    
      dot.on("mouseover",function(d){
        
        d3.select(this).classed("selected",true);
        
      }).on("mouseout",function(d){
        
        d3.select(this).classed("selected",false);
        
      });
            
    });

    

    
    
});

/*
d3.json('assets/data/topic_dist.json', function(data) {
    topics = data;  
});
*/

  

