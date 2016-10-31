var offsetx = 0;
var offsety = 0;
var sim = undefined;

function findUrl( data, url )
{
	for (var i = 0; i < data.length; i++)
	{
		if (data[i].url === url)
		{
			return data[i];
		}
	}
	return undefined;
}

function translateUrl(url)
{
	url = url.toLowerCase();
	if (url.startsWith('http://effectivealtruismhub.com'))
	{
		return 'http://eahub.org' + url.substr('http://effectivealtruismhub.com'.length);
	}
	if (url.startsWith('https://www.againstmalaria.com'))
	{
		return 'http://www.againstmalaria.com' + url.substr('https://www.againstmalaria.com'.length);
	}
	return url;
}

function translateUrls(data)
{
	var urlsWeHave = {};
	var newData = [];
	for (var i = 0; i < data.length; i++)
	{
		var newUrl = translateUrl(data[i].url);
		if (!urlsWeHave[newUrl])
		{
			var source = data[i];
			for (var j = 0; j < source.links.length; j++)
			{
				source.links[j] = translateUrl(source.links[j]);
			}
			source.url = newUrl;
			newData.push(source);
			urlsWeHave[newUrl] = true;
		}
	}
	return newData;
}

function site(url)
{
	url = url.substr(url.indexOf('/'));
	return url.substr(0,url.indexOf('/',8));
}

function plotGraph(data)
{
	var w = $('svg').width();
	var h = $('svg').height();

	var links = [];
	data = translateUrls(data);
	for (var i = 0; i < data.length; i++)
	{
		var source = data[i];
		for (var j = 0; j < source.links.length; j++)
		{
			target = findUrl(data, source.links[j]);
			if (target != undefined)
			{
				var twoWay = (target.links.indexOf(source) != -1);
				var sameSite = (site(source.url) == site(target.url));
				links.push( {source: source, target: target, twoWay: twoWay, sameSite: sameSite });
			}
		}
		data[i].x = (data[i].url.indexOf('/',8) - 12) * w / 64;
		data[i].y = data[i].score * h * 2 + h/4;
	}

	d3.select('svg').call(d3.drag().on('drag',drag));
	sim = d3.forceSimulation( data ).on('tick', () => {
		showNodes( data );
		showKey();
	} ).on('end', () => {
		showEdges( links );
	} ).force('link', d3.forceLink(links).distance( d => d.twoWay ? 2 : 20 ) ).force('manyBody',d3.forceManyBody().strength(-0.7));
}

function drag()
{
	offsetx += d3.event.dx;1
	offsety += d3.event.dy;
	sim.restart();
}

function mouseover( d )
{
	$('#urltip').text( d.url );
}

function rgba(r,g,b,a)
{
	return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
}

var urlColours = [
	{"name":"en.wikipedia.org","colour":[0,0,255]},
	{"name":"wikipedia.org","colour":[0,255,225]},
	{"name":"againstmalaria.com","colour":[255,128,0]},
	{"name":"givewell.org","colour":[128,0,128]},
	{"name":"givingwhatwecan.org","colour":[192,0,0]},
	{"name":"youtube.com","colour":[255,0,0]},
	{"name":"effective-altruism.wikia.com","colour":[255,0,255]},
	{"name":"wiki.effectivealtruismhub.com","colour":[255,0,255]},
	{"name":"eahub.org/groups","colour":[0,192,0]},
	{"name":"eahub.org/user","colour":[128,192,0]},
	{"name":"eahub.org","colour":[0,128,128]},
	{"name":"effective-altruism.com","colour":[128,255,0]},
	{"name":"goodventures.org","colour":[128,0,255]},
	{"name":"thelifeyoucansave.org","colour":[255,0,224]},
	{"name":"facebook.com","colour":[192,180,0]},
	{"name":"imperial.ac.uk","colour":[255,160,0]},
	{"name":"evidenceaction.org","colour":[255,160,0]},
	{"name":"givedirectly.org","colour":[255,160,0]},
	{"name":"","colour":[0,0,0]}
];

function urlColour( url, score )
{
	var s = Math.min( 1, score * 8 );
	var t = 1 - s;
	for (var i = 0; i < urlColours.length; i++)
	{
		if (url.indexOf(urlColours[i].name) != -1)
		{
			var col = urlColours[i].colour;
			return rgba(Math.floor(col[0]*s + 255*t),Math.floor(col[1]*s + 255*t),Math.floor(col[2]*s + 255*t), 1);
		}
	}
	return rgba(0,0,0,score);
}

function showNodes( data )
{
	var circles = d3.select('#graph-circles').selectAll('circle');
	circles = circles.data( data );
	circles.enter().append('circle').on('mouseover',mouseover);
	circles.exit().remove();
	circles = d3.select('#graph-circles').selectAll('circle');
	circles.attr('r', d => d.url.indexOf('/',8) == d.url.length - 1 ? 3 : 1.5);
	circles.attr('cx', d => offsetx + d.x);
	circles.attr('cy', d => offsety + d.y);
	circles.attr('fill', d => urlColour(d.url,d.score) );
}

function showEdges( links )
{
	var lines = d3.select('#graph-lines').selectAll('line');
	lines = lines.data( links );
	lines.enter().append('line').attr('stroke-width','0.1');
	lines.exit().remove();
	lines = d3.select('#graph-lines').selectAll('line');
	lines.attr('stroke', d => d.sameSite ? 'rgba(128,128,128,0.01)' : 'rgba(128,128,128,0.03)');
	lines.attr('x1', d => offsetx + d.source.x );
	lines.attr('y1', d => offsety + d.source.y );
	lines.attr('x2', d => offsetx + d.target.x );
	lines.attr('y2', d => offsety + d.target.y );
}

function showKey()
{
	var circles = d3.select('#graph-key').selectAll('circle');
	circles = circles.data( urlColours );
	circles.enter().append('circle').attr( 'r', 2 );
	circles.exit().remove();
	circles = d3.select('#graph-key').selectAll('circle');
	circles.attr('cx', d => 10);
	circles.attr('cy', (d,i) => 10 + 10 * i);
	circles.attr('fill', d => rgba(d.colour[0],d.colour[1],d.colour[2],1) );

	var text = d3.select('#graph-key').selectAll('text').attr('font-family','sans-serif').attr('font-size',10);
	text = text.data( urlColours );
	text.enter().append('text');
	text.exit().remove();
	text = d3.select('#graph-key').selectAll('text');
	text.attr('x', d => 15);
	text.attr('y', (d,i) => 13 + 10 * i);
	text.text( d => d.name || 'other' );
}

function showGraph()
{
	var svg = $('<svg width="1200" height="800"><g id="graph-lines"></g><g id="graph-circles"></g><g id="graph-key"></g></svg>');
	$('#content').empty();
	$('#content').append('<span id="urltip"></span><br>');
	$('#content').append(svg);

	$.ajax('/v1/links').then( (data) => {
		plotGraph(data);
	});
}
