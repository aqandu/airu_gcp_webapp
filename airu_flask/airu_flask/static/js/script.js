let projectId = "scottgale";
let datasetId = "airu_dataset_iot";
let tableName = "airU_sensor";
let map;
let email_login = "no_user";        // Used to store the email address of the user that is logged in
                                    // If no user is logged in the value is "no_user"
let state = "NO_DATA";
let main_data;
let historical_data;
let historical_days = 1;
let current_device_id = "";


// Make the DIV element draggable:
dragElement(document.getElementById("scale"));

function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (document.getElementById(elmnt.id + "_header")) {
        // if present, the header is where you move the DIV from:
        document.getElementById(elmnt.id + "_header").onmousedown = dragMouseDown;
    } else {
        // otherwise, move the DIV from anywhere inside the DIV:
        elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

function pageSetup() {
    console.log("pageSetup()");

    let svg_height = document.getElementById("svg_historical").getBoundingClientRect().height;
    let svg_width = document.getElementById("svg_historical").getBoundingClientRect().width;

    let h = svg_height - 50;

    // Add the g containers for the path, circles, axes and axes lables for historical plot
    let g_path = d3.select("#svg_historical")
        .append("g")
        .attr("id", "g_path")
        .attr("transform", "translate(0,0)");



    let g_circles = d3.select("#svg_historical")
        .append("g")
        .attr("id", "g_circles")
        .attr("transform", "translate(0,0)")
        .attr("height", svg_height)
        .attr("width", svg_width);


    let xAxisGroup = d3.select("#svg_historical")
        .append("g")
        .attr("id", "xAxis")
        .attr("class", "axis")
        .attr("transform", "translate(50," + h + ")");

    let yAxisGroup = d3.select("#svg_historical")
        .append("g")
        .attr("id", "yAxis")
        .attr("class", "axis")
        .attr("transform", "translate(90,0)");


    let email = document.getElementById("user_email");
    if (email) {
        email_login = email.innerText;
        console.log(email_login);
    }
    else {
        email_login = "none";
        console.log(email_login);
    }
    let data = {request:email_login};
    let json_request = JSON.stringify(data);
    console.log(json_request);
    if (state==="NO_DATA") {
        console.log("Loading data from DB");
        $.ajax({
            type: "GET",
            url: "/request_data_flask/" + json_request + "/"
        }).done(function(x){
            //console.log(x);
            main_data = JSON.parse(x);
            //console.log(main_data);
            //console.log(main_data[0]);
            load_active_sensors(main_data);
        });
        state="DATA";
    }
    else {
        load_active_sensors(main_data);
    }
}

let color_scale = d3.scaleThreshold()
    .domain([0, 4, 8, 12, 20, 28, 35, 42, 49, 55, 150, 250, 350])
    .range(["#A6A6A6", "#00FF00", "#99FF99", "#CCFFCC", "#FFFF99", "#E6E600", "#FFCC00", "#FF9900", "#FF6600", "#CC6600", "#FF3333", "#C00000", "#800000"]);


function clear_page(){
    console.log("clear_page()");
    // Clear css from sensor circles
    reset_circles();
    // Clear "Current Conditions" ***************************************************
    document.getElementById("txtTime").innerHTML = "";
    document.getElementById("txtDevId").innerHTML = "";
    document.getElementById("txtTemp").innerHTML = "";
    document.getElementById("txtHum").innerHTML = "";
    document.getElementById("txtPM1").innerHTML = "";
    document.getElementById("txtPM25").innerHTML = "";
    document.getElementById("txtPM10").innerHTML = "";
    document.getElementById("txtCO").innerHTML = "";
    document.getElementById("txtNOX").innerHTML = "";

    // Clear Historical Data
    d3.selectAll(".tick").remove();
    d3.select("#g_circles").selectAll("circle").remove();
    d3.selectAll("path").remove();
    d3.select("#svg_historical").selectAll("text").remove();
}

function reset_circles(){
    // Reset all circles to default
    let allCircles = d3.select("#div_circle").selectAll("circle")
        .classed("selected_circle", false)
        .classed("default_circle", true);
}


//*****EVENT HANDLERS**************
function sensor_click(data) {
    console.log("sensor_click()");
    clear_page();
    // If deselecting a circle then clear all the data fields / visualizaitions
    if (current_device_id === data.value.DEVICE_ID) {
        // Clear global data variables
        current_device_id = "";
        historical_data = "";
        document.getElementById("current_conditions").style.visibility = "hidden";
    }
    else {
        // Validate user has permission to view detailed information
        validate_user(data);
    }
}

function validate_user(data){
    console.log("validate_user()");
    let email = document.getElementById("user_email");
    if (email) {
        email_login = email.innerText;
        //console.log(email_login);
    }
    else {
        return false;
    }
    let json_data = {"EMAIL": email_login,
        "DEVICE_ID": data.value.DEVICE_ID};
    let json_request = JSON.stringify(json_data);
    //console.log(json_request);
    $.ajax({
        type: "POST",
        url: "/validate_user/" + json_request + "/"
    }).done(function(x){
        if (x==="true") {
            // user is validated proceed with displaying data
            show_data(data);
            document.getElementById("current_conditions").style.visibility = "visible";
        }
        else{
            current_device_id = "";
        }
    });
}

function show_data(data){
    // Highlight the selected circle
    let sensorHighlight = d3.select("#" + data.value.DEVICE_ID)
        .classed("selected_circle", true);

    let display_date = new Date(data.value.TIMESTAMP).toLocaleString();

    // let display_date = new Date(data.value.TIMESTAMP);
    // let string_date = display_date.getDate() + "/" + display_date.getMonth() + "/" + display_date.getFullYear();
    // let string_hour = String(display_date.getHours());
    // let string_minutes = String(display_date.getMinutes());
    // if (string_minutes.length == 1){
    //     string_minutes = "0" + string_minutes
    // }

    current_device_id =  data.value.DEVICE_ID;
    let pm_units = "\u03BCg/m" + "3".sup();
    let temp_units = "\xB0C";


    //Display current data ***************************************************
    document.getElementById("txtTime").innerHTML = display_date;
    document.getElementById("txtDevId").innerHTML = current_device_id.substring(1);
    document.getElementById("txtTemp").innerHTML = parseFloat(data.value.TEMP).toFixed(2) + " " + temp_units;
    document.getElementById("txtHum").innerHTML = parseFloat(data.value.HUM).toFixed(2) + "%";
    document.getElementById("txtPM1").innerHTML = parseFloat(data.value.PM1).toFixed(2) + " " + pm_units;
    document.getElementById("txtPM25").innerHTML = parseFloat(data.value.PM25).toFixed(2) + " " + pm_units;
    document.getElementById("txtPM10").innerHTML = parseFloat(data.value.PM10).toFixed(2) + " " + pm_units;
    document.getElementById("txtCO").innerHTML = parseInt(data.value.CO);
    document.getElementById("txtNOX").innerHTML = parseInt(data.value.NOX);

    let popup = document.getElementById("current_conditions");
    popup.classList.toggle("show");

    // Display historical data *************************************************
    // Query the DB for the historical
    console.log("Loading historical data from DB");
    query_database();
}

function query_database(){

    let data_request = {"DEVICE_ID": current_device_id,
                    "DAYS": historical_days};
    data_request = JSON.stringify(data_request);
    console.log(data_request);
    $.ajax({
        type: "GET",
        url: "/request_historical/" + data_request + "/"
    }).done(function(x){
        // Turn the data in JSON
        historical_data = JSON.parse(x);
        historical_data.forEach(function(d){
            d.D_TIME = new Date(d.D_TIME);
            if (d.AVG_PM25 < 0){
                d.AVG_PM25 = 0.0001;    // I use this later to indicate bad data
            }
        });
        console.log(historical_data);
        draw_historical(historical_data);
    });
}

function redraw(){
    console.log("redraw()");
    if (current_device_id !== ""){
        draw_historical(historical_data);
    }
}

function radio_click(){
    console.log("radio_click()");
    if (document.getElementById("1day").checked){
        historical_days = 1;
    }
    else if (document.getElementById("3day").checked){
        historical_days = 3;
    }
    else {
        historical_days = 7;
    }
    if (current_device_id !== ""){
        query_database();
    }
}

function checkbox_click() {
    load_active_sensors(main_data);
}

function draw_historical(data){
    console.log("draw_historical()");
    // Clean up old html / svg / other items
    d3.selectAll(".tooltip_pm25").remove();

    // SETUP SCALES
    let w = document.getElementById("svg_historical").getBoundingClientRect().width-5;
    let h = document.getElementById("svg_historical").getBoundingClientRect().height-5;
    let xPadding = 50;          // For PM2.5 Label on y axis
    let yPadding = 10;

    d3.select("#date_time_label").remove();

    // let xAxisLabel = d3.select("#svg_historical")
    //     .append('text')
    //     .classed('axis-label', true)
    //     .text("DATE / TIME")
    //     .style("text-anchor", "middle")
    //     .attr("transform", "translate(" + ((w/2)+xPadding) + ",175)")
    //     .attr("id", "date_time_label");

    let yAxisLabel = d3.select("#svg_historical")
        .append('text')
        .classed('axis-label', true)
        .text("PM 2.5")
        .style("text-anchor", "middle")
        .attr("transform", "translate(40,55) rotate(270)");

    let xScale = d3.scaleTime()
        .domain([
            d3.min(data, function(d){ return d.D_TIME; }),
            d3.max(data, function(d) { return d.D_TIME; })
        ])
        .range([xPadding, w-xPadding]);

    let yScale = d3.scaleLinear()
        .domain([0, 255])  //.domain([0, d3.max(data, function(d){return d.AVG_PM25; })])
        .range([h-50,yPadding])
        .nice();

    // SETUP AXES
    let xAxis = d3.axisBottom()
        .scale(xScale);

    let yAxis = d3.axisLeft()
        .scale(yScale);

    // Used to format the number of labels associated with the x-axis
    let x_ticks;
    if (data.length <=24)
        x_ticks = data.length;
    else
        x_ticks = 24;

    // Displays the axes within the established <g>
    let xAx = d3.select("#xAxis").call(xAxis.ticks(x_ticks))  //xAxis.ticks(data.length)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("class", "axis_font")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)" );

    let yAx = d3.select("#yAxis").call(yAxis.ticks(5))
        .attr("class", "axis_font");

    // Line generator
    let line = d3.line()
        .x(function(d){ return xScale(d.D_TIME)+xPadding; })
        .y(function(d) { return yScale(d.AVG_PM25); });

    let tooltip_div = d3.select("#historical_data").append("div")
        .attr("class", "tooltip_pm25")
        .style("opacity", 0);

    let svg = d3.select("#svg_historical");

    // REMOVE PREVIOUS PATH
    svg.selectAll(".line").remove();

    // DRAW PATH
    let path = svg.select("#g_path").append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line);

    // DRAW CIRCLES

    let dataCircles = svg.select("#g_circles").selectAll("circle")
        .data(data);
    dataCircles.exit().remove();
    dataCircles = dataCircles.enter().append("circle").merge(dataCircles);

    dataCircles.attr("class", "hist_circles")
        .attr("cx", function(d){
            return xScale(d.D_TIME) + xPadding;
        })
        .attr("cy", function(d){
            if (d.AVG_PM25 >= 255){
                return yScale(255);
            }
            else{
                return yScale(d.AVG_PM25);
            }

        })
        .attr("fill", function(d){
            if (d.AVG_PM25 === 0.0001){
                return color_scale(-1);         // Color gray to indicate bad data
            }
            return color_scale(d.AVG_PM25);
        })
        .on("mouseover", function(d) {
            tooltip_div.transition()
                .style("opacity", .9);
            tooltip_div.html(d.AVG_PM25)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY-15) + "px");
        })
        .on("mouseout", function(d) {
            tooltip_div.transition()
                .style("opacity", 0);
        });
}

function load_active_sensors(d){
    console.log("load_active_sensors()");
    //console.log(d);
    let data = [];
    // Eliminate all data with not associated with selected version (VER)
    for (let i = 0; i < d.length; i++) {
        if (document.getElementById("v1").checked && d[i].VER === '1'){
           data.push(d[i]);
        }
        if (document.getElementById("v2").checked && d[i].VER === '2'){
            data.push(d[i]);
        }
        if (document.getElementById("v3").checked && d[i].VER === '3'){
            data.push(d[i]);
        }
        if (d[i].VER === ""){  // Add sensors without a version
            data.push(d[i]);
        }
    }
    //console.log(data);

    // Clear all old markers / circles
    d3.select("#div_circle").remove();
    d3.selectAll(".tooltip").remove();

    let overlay = new google.maps.OverlayView();
    // Add the container when the overlay is added to the map.
    overlay.onAdd = function () {
        //let layer = d3.select(this.getPanes().overlayLayer).append("div")
        let layer = d3.select(this.getPanes().overlayMouseTarget).append("div")
            .attr("id", "div_circle")
            .attr("class", "sensors");

        // Draw each marker as a separate SVG element.
        // We could use a single SVG, but what size would it have?
        overlay.draw = function () {
            let projection = this.getProjection(),
                padding = 10;   // original value was 10
            let marker = layer.selectAll("svg")
                .data(d3.entries(data))
                .each(transform) // update existing markers
                .enter().append("svg")
                .each(transform)
                .attr("class", "marker");

            let tooldiv = d3.select("#map").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

            // Add a circle.
            marker.append("circle")
                .attr("id", (d)=>d.value.DEVICE_ID)
                .attr("class", "default_circle")
                .attr("cx", padding)
                .attr("cy", padding)
                .attr("fill", (d=> {
                    let val = d.value.PM25;
                    let sense_date = new Date(d.value.TIMESTAMP).getTime();
                    let now = Date.now();
                    // Get number of hours between now and when the sensor last reported
                    // If the sensor has not reported in the last hour it has gone offline
                    // Every sensor should be reporting at least once an hour
                    let x = (now-sense_date)/(3600*1000);
                    if (x>1){
                        val = -1;
                    }
                    //console.log (val);
                    return color_scale(val);
                }))
                .on("mouseover", (d=> {
                    //console.log(d);
                    map.setOptions({draggableCursor:'pointer'});
                    tooldiv.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooldiv.html("Sensor: " + d.value.DEVICE_ID.substring(9) + "<br/>"  + "PM2.5: " + d.value.PM25)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY-100) + "px");

                }))
                .on("mouseout", (d=>{
                    map.setOptions({draggableCursor:''});
                    tooldiv.transition()
                        .duration(500)
                        .style("opacity", 0);
                }))
                .on("click", (d=>{
                    sensor_click(d);
                }));


            // Add a label.
            /*marker.append("text")
                .attr("class", "sensor_label")
                .attr("x", padding + 10)
                .attr("y", padding)
                .attr("dy", ".30em")
                .text(function (d) {
                    //console.log(d.value.DEVICE_ID);
                    return d.value.DEVICE_ID.substring(9);
                });*/

            function transform(d) {
                //console.log(d);
                d = new google.maps.LatLng(d.value.LAT, d.value.LON);
                d = projection.fromLatLngToDivPixel(d);
                return d3.select(this)
                    .style("left", (d.x - padding) + "px")
                    .style("top", (d.y - padding) + "px");
            }
        };
    };
    // Bind our overlay to the map…
    overlay.setMap(map);
}

//************DRAWING TOOL / QUERY GENERATION************************************

function setUpDrawingTools() {
    // Initialize drawing manager
    let drawingManager = new google.maps.drawing.DrawingManager({
        //drawingMode: google.maps.drawing.OverlayType.CIRCLE  USE THIS TO SET A DEFAULT DRAWING MODE
        drawingControl: true,
        drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_LEFT,
            drawingModes: [
                google.maps.drawing.OverlayType.CIRCLE,
                google.maps.drawing.OverlayType.POLYGON,
                google.maps.drawing.OverlayType.RECTANGLE,
                google.maps.drawing.OverlayType.MARKER
            ]
        },
        circleOptions: {
            fillOpacity: 0
        },
        polygonOptions: {
            fillOpacity: 0
        },
        rectangleOptions: {
            fillOpacity: 0
        }
    });
    drawingManager.setMap(map);

    // Event listeners
    drawingManager.addListener('rectanglecomplete', rectangle => {
        rectangleQuery(rectangle.getBounds());
    });

    drawingManager.addListener('circlecomplete', circle => {
        circleQuery(circle);
    });

    drawingManager.addListener('polygoncomplete', polygon => {
        let path = polygon.getPaths().getAt(0).j;
        let queryPolygon = path.map(element => {
            return [element.lng(), element.lat()]
        });
        polygonQuery(queryPolygon);
    });
}

// Used only for loading local files . . . and debugging.
function load_data() {
    // Perform the query to get active sensors in the last hour
    console.log("load_data()");
    // Request data from the server to view on the map


    d3.json("static/data/sensor_last_hour.json").then(d => {
        load_active_sensors(d);
    });
}

function rectangleQuery(latLngBounds){
    console.log(latLngBounds);
    let queryString = rectangleSQL(latLngBounds.getNorthEast(), latLngBounds.getSouthWest());
    sendQuery(queryString);
}

function rectangleSQL(ne, sw){
    let queryString = 'SELECT LAT, LON ';
    queryString +=  'FROM `' + projectId +'.' + datasetId + '.' + tableName + '`';
    queryString += ' WHERE LAT > ' + sw.lat();
    queryString += ' AND LAT < ' + ne.lat();
    queryString += ' AND LON > ' + sw.lng();
    queryString += ' AND LON < ' + ne.lng();
    queryString += ' LIMIT ' + recordLimit;
    return queryString;
}

function circleQuery(circle){
    let queryString = haversineSQL(circle.getCenter(), circle.radius);
    sendQuery(queryString);
}

// Calculate a circular area on the surface of a sphere based on a center and radius.
function haversineSQL(center, radius){
    let queryString;
    let centerLat = center.lat();
    let centerLng = center.lng();
    let kmPerDegree = 111.045;

    queryString = 'CREATE TEMPORARY FUNCTION Degrees(radians FLOAT64) RETURNS FLOAT64 LANGUAGE js AS ';
    queryString += '""" ';
    queryString += 'return (radians*180)/(22/7);';
    queryString += '"""; ';

    queryString += 'CREATE TEMPORARY FUNCTION Radians(degrees FLOAT64) RETURNS FLOAT64 LANGUAGE js AS';
    queryString += '""" ';
    queryString += 'return (degrees*(22/7))/180;';
    queryString += '"""; ';

    queryString += 'SELECT LAT, LON ';
    queryString += 'FROM `' + projectId +'.' + datasetId + '.' + tableName + '` ';
    queryString += 'WHERE ';
    queryString += '(' + kmPerDegree + ' * DEGREES( ACOS( COS( RADIANS(';
    queryString += centerLat;
    queryString += ') ) * COS( RADIANS( LAT ) ) * COS( RADIANS( ' + centerLng + ' ) - RADIANS('
    queryString += ' LON ';
    queryString += ') ) + SIN( RADIANS(';
    queryString += centerLat;
    queryString += ') ) * SIN( RADIANS( LAT ) ) ) ) ) ';

    queryString += ' < ' + radius/1000;
    queryString += ' LIMIT ' + recordLimit;
    return queryString;
}

function polygonQuery(polygon) {
    let request = gapi.client.bigquery.jobs.insert({
        'projectId' : projectId,
        'resource' : {
            'configuration':
                {
                    'query':
                        {
                            'query': polygonSql(polygon),
                            'useLegacySql': false
                        }
                }
        }
    });
    request.execute(response => checkJobStatus(response.jobReference.jobId));
}

function polygonSql(poly){
    let queryString = 'CREATE TEMPORARY FUNCTION pointInPolygon(latitude FLOAT64, longitude FLOAT64) ';
    queryString += 'RETURNS BOOL LANGUAGE js AS """ ';
    queryString += 'var polygon=' + JSON.stringify(poly) + ';';
    queryString += 'var vertx = [];';
    queryString += 'var verty = [];';
    queryString += 'var nvert = 0;';
    queryString += 'var testx = longitude;';
    queryString += 'var testy = latitude;';
    queryString += 'for(coord in polygon){';
    queryString += '  vertx[nvert] = polygon[coord][0];';
    queryString += '  verty[nvert] = polygon[coord][1];';
    queryString += '  nvert ++;';
    queryString += '}';
    queryString += 'var i, j, c = 0;';
    queryString += 'for (i = 0, j = nvert-1; i < nvert; j = i++) {';
    queryString += '  if ( ((verty[i]>testy) != (verty[j]>testy)) &&(testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) ){';
    queryString += '    c = !c;';
    queryString += '  }';
    queryString += '}';
    queryString += 'return c;';
    queryString += '"""; ';
    queryString += 'SELECT LAT, LON, dropoff_latitude, dropoff_longitude, pickup_datetime ';
    queryString += 'FROM `' + projectId + '.' + datasetId + '.' + tableName + '` ';
    queryString += 'WHERE pointInPolygon(LAT, LON) = TRUE ';
    queryString += 'LIMIT ' + recordLimit;
    return queryString;
}


function initMap() {
    console.log("initMap()");
    map = new google.maps.Map(document.getElementById("map"), {
        center: {lat: 40.72, lng: -111.900},
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP,     //ROADMAP, TERRAIN, SATELITE, HYBRID
    styles:
        [
            {
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#f5f5f5"
                    }
                ]
            },
            {
                "elementType": "labels.icon",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#616161"
                    }
                ]
            },
            {
                "elementType": "labels.text.stroke",
                "stylers": [
                    {
                        "color": "#f5f5f5"
                    }
                ]
            },
            {
                "featureType": "administrative.land_parcel",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#bdbdbd"
                    }
                ]
            },
            {
                "featureType": "poi",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#eeeeee"
                    }
                ]
            },
            {
                "featureType": "poi",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#757575"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#e5e5e5"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "geometry.fill",
                "stylers": [
                    {
                        "visibility": "on"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#9e9e9e"
                    }
                ]
            },
            {
                "featureType": "road",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#6F726F"      // Color of the roads
                    }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "geometry.fill",
                "stylers": [
                    {
                        "color": "#4D4F4D"
                    }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "labels.text",
                "stylers": [
                    {
                        "color": "#4a4a4a"
                    }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#686868"
                    }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "labels.text.stroke",
                "stylers": [
                    {
                        "color": "#ffffff"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#dadada"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry.fill",
                "stylers": [
                    {
                        "color": "#4D4F4D"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "labels.text",
                "stylers": [
                    {
                        "color": "#4a4a4a"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#4a4a4a"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "labels.text.stroke",
                "stylers": [
                    {
                        "color": "#ffffff"
                    }
                ]
            },
            {
                "featureType": "road.local",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#686868"
                    }
                ]
            },
            {
                "featureType": "road.local",
                "elementType": "labels.text.stroke",
                "stylers": [
                    {
                        "color": "#ffffff"
                    }
                ]
            },
            {
                "featureType": "transit.line",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#e5e5e5"
                    }
                ]
            },
            {
                "featureType": "transit.station",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#eeeeee"
                    }
                ]
            },
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#c9c9c9"
                    }
                ]
            },
            {
                "featureType": "water",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#9e9e9e"
                    }
                ]
            }
        ]
    });
    setUpDrawingTools();
}


// Event Listeners **********************************************************

window.addEventListener('load', pageSetup, false);
// Redraw based on the new size whenever the browser window is resized.
window.addEventListener("resize", redraw);

$('input[type="radio"]').on('click', radio_click);
$('input[type="checkbox"]').on('click', checkbox_click);


