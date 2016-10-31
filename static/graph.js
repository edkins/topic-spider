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

// pseudorandom number generator
var m_w = 123456789;
var m_z = 987654321;
var mask = 0xffffffff;

// Takes any integer
function seed(i) {
    m_w = i;
    m_z = 987654321;
}

// Returns number between 0 (inclusive) and 1.0 (exclusive),
// just like Math.random().
function random()
{
    m_z = (36969 * (m_z & 65535) + (m_z >> 16)) & mask;
    m_w = (18000 * (m_w & 65535) + (m_w >> 16)) & mask;
    var result = ((m_z << 16) + m_w) & mask;
    result /= 4294967296;
    return result + 0.5;
}

function plotGraph(data)
{
	var w = $('svg').width();
	var h = $('svg').height();

	var links = [];
	seed( 123456789 );
	for (var i = 0; i < data.length; i++)
	{
		var source = data[i];
		for (var j = 0; j < source.links.length; j++)
		{
			target = findUrl(data, source.links[j]);
			if (target != undefined)
			{
				var twoWay = (target.links.indexOf(source) != -1);
				links.push( {source: source, target: target, twoWay: twoWay });
			}
		}
		data[i].x = (data[i].url.indexOf('/',8) - 12) * w / 24;
		data[i].y = data[i].score * h * 2 + h/4;
	}

	d3.select('svg').call(d3.drag().on('drag',drag));
	sim = d3.forceSimulation( data ).on('tick', () => {
		showNodes( data );
	} ).on('end', () => {
		showEdges( links );
	} ).force('link', d3.forceLink(links).distance( d => d.twoWay ? 2 : 20 ) ).force('manyBody',d3.forceManyBody().strength(-1.5));
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

function urlColour( url, score )
{
	score = Math.min( 1, score * 8 );
	if (url.indexOf('en.wikipedia.org') != -1)
	{
		return rgba(0,0,255,score);
	}
	else if (url.indexOf('wikipedia.org') != -1)
	{
		return rgba(0,255,255,score);
	}
	else if (url.indexOf('.againstmalaria.com') != -1)
	{
		return rgba(255,128,0,score);
	}
	else if (url.indexOf('givewell.org') != -1)
	{
		return rgba(128,0,128,score);
	}
	else if (url.indexOf('givingwhatwecan.org') != -1)
	{
		return rgba(255,0,0,score);
	}
	else if (url.indexOf('effective-altruism.wikia') != -1 || url.indexOf('wiki.effectivealtruismhub.com') != -1)
	{
		return rgba(255,0,255,score);
	}
	else if ((url.indexOf('effectivealtruismhub.com/groups') != -1 || url.indexOf('eahub.org/groups') != -1) && url.indexOf('resources') == -1)
	{
		return rgba(0,192,0,score);
	}
	else if (url.indexOf('effectivealtruismhub.com') != -1 || url.indexOf('eahub.org') != -1)
	{
		return rgba(0,128,128,score);
	}
	else if (url.indexOf('effective-altruism.com') != -1)
	{
		return rgba(128,0,255,score);
	}
	else if (url.indexOf('facebook.com') != -1)
	{
		return rgba(192,192,0,score);
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
	circles.attr('r', d => d.url.indexOf('/',8) == d.url.length - 1 ? 3 : 2);
	circles.attr('cx', d => offsetx + d.x);
	circles.attr('cy', d => offsety + d.y);
	circles.attr('fill', d => urlColour(d.url,d.score) );
}

function showEdges( links )
{
	var lines = d3.select('#graph-lines').selectAll('line');
	lines = lines.data( links );
	lines.enter().append('line').attr('stroke','rgba(0,0,0,0.03)').attr('stroke-width','0.1');
	lines.exit().remove();
	lines = d3.select('#graph-lines').selectAll('line');
	lines.attr('x1', d => offsetx + d.source.x );
	lines.attr('y1', d => offsety + d.source.y );
	lines.attr('x2', d => offsetx + d.target.x );
	lines.attr('y2', d => offsety + d.target.y );
}

function showGraph()
{
	var svg = $('<svg width="800" height="800"><g id="graph-lines"></g><g id="graph-circles"></g></svg>');
	$('#content').empty();
	$('#content').append('<span id="urltip"></span><br>');
	$('#content').append(svg);

	$.ajax('/v1/links').then( (data) => {
		plotGraph(data);
	});
}
