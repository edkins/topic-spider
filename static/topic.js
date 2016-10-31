function changeRank(event)
{
	var action = event.target.value;
	var name = event.target.name;
	var relevance = (action == 'yes') ? 1 : 0;
	$('#loading-'+name).css('visibility','visible');
	var json = JSON.stringify( [{name:name, relevance:relevance}] );
	$.ajax('/v1/relevance', {
		'method':'post',
		'content-type':'application/json',
		'data': json
	}).then( response => {
		$('#loading-'+name).css('visibility','hidden')
	});
}

function radio(name, value, onchange, selected)
{
	var result = $('<input type="radio">');
	result.attr('name', name);
	result.attr('value', value);
	if (selected)
	{
		result.attr('checked', 'checked');
	}
	result.on('change', onchange);
	return result;
}

function image(name, src, width, height, visibility)
{
	var result = $('<image>');
	result.attr('src', src);
	result.attr('width', width);
	result.attr('height', height);
	result.css('visibility',visibility);
	return result;
}

function isRelevant(kw)
{
	return kw.relevance != null && kw.relevance >= 0.5;
}

function isIrrelevant(kw)
{
	return kw.relevance != null && kw.relevance < 0.5;
}

function clickTab(event)
{
	var name = event.target.id;
	if (name.startsWith('tab-kw-'))
	{
		var type = name.substr( 'tab-kw-'.length );
		showKeywords(type);
	}
	else if (name.startsWith('tab-doc-'))
	{
		var type = name.substr( 'tab-doc-'.length );
		showDocuments(type);
	}
	else
	{
		$('#content').empty();
	}
	$('.tab').removeClass('active');
	$(event.target).addClass('active');
}

function showDocuments(type)
{
	$.ajax('/v1/documents/' + type).then( response => {
		elements = [];
		for (var i = 0; i < response.length; i++)
		{
			var doc = response[i];
			elements.push( doc.url + ' ' + doc.score );
		}
		$('#content').empty();
		$('#content').append(elements);
	});
}

function showKeywords(type)
{
	$.ajax('/v1/keywords/' + type).then( response => {
		elements = ['yes/no', $('<br>')];
		for (var i = 0; i < response.length; i++)
		{
			var kw = response[i];
			var radioYes = radio( kw.word, 'yes', changeRank, isRelevant(kw) );
			var radioNo = radio( kw.word, 'no', changeRank, isIrrelevant(kw) );
			var loadingImg = image( 'loading-' + kw.word, '/static/pageloader.gif', 16, 16, 'hidden')
			var br = $('<br>');
			elements.push( radioYes, radioNo, kw.word, loadingImg, br );
		}
		$('#content').empty();
		$('#content').append(elements);
	});
}

function onload()
{
	showKeywords('unranked');
}

function spider()
{
	var url = $('#spider-url').val();
	var json = JSON.stringify({url:url});
	$.ajax('/v1/spider', {
		'method': 'post',
		'content-type': 'application/json',
		'data': json
	});
}

