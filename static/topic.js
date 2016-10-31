var polling = undefined;

function changeRankOf(name,action)
{
	var relevance = (action == 'yes') ? 1 : 0;
	var json = JSON.stringify( [{name:name, relevance:relevance}] );
	$('#loading-'+name).css('visibility','visible');
	$.ajax('/v1/relevance', {
		'method':'post',
		'content-type':'application/json',
		'data': json
	}).then( response => {
		$('#loading-'+name).css('visibility','hidden')
	});
}

function changeRank(event)
{
	var action = event.target.value;
	var name = event.target.name;
	changeRankOf(name,action);
}

function changeRankToYes(event)
{
	var name = $(event.target).data('name');
	changeRankOf(name,'yes');
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

function clickableSpan(text,onclick,name)
{
	var result = $('<span></span>');
	result.on('click',onclick);
	result.css('cursor','pointer');
	result.data('name',name);
	result.append(text);
	return result
}

function button(text,onclick,name)
{
	var result = $('<input type="button">');
	result.attr('value', text);
	result.on('click', onclick);
	result.data('name',name);
	return result;
}

function clickDoc(event)
{
	var url = $(event.target).data('name');
	var json = JSON.stringify({url:url});
	$.ajax('v1/docinfo', {
		'method': 'post',
		'content-type': 'application/json',
		'data': json
	}).then( response => {
		elements = [];
		elements.push( response.url );
		elements.push( $('<br>') );
		elements.push( 'Word count: ' + response.wordCount );
		elements.push( $('<br>') );
		response.words.sort( (a,b) => (b.contribution - a.contribution) * 1000000000 + b.wordScore - a.wordScore );
		for (var i = 0; i < response.words.length; i++)
		{
			var word = response.words[i];
			if (word.relevance < 0.5)
			{
				elements.push( button('+', changeRankToYes, word.word ) );
			}
			elements.push( word.contribution.toFixed(5) + ' ' + word.word );
			elements.push( $('<br>') );
		}
		$('#content').empty();
		$('#content').append(elements);
	});
	noTab();
}

function isRelevant(kw)
{
	return kw.relevance != null && kw.relevance >= 0.5;
}

function isIrrelevant(kw)
{
	return kw.relevance != null && kw.relevance < 0.5;
}

function noTab()
{
	$('.tab').removeClass('active');
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
			var url = doc.url;
			elements.push( doc.score.toFixed(2) + ' ' );
			elements.push( clickableSpan( url, clickDoc, url ) );
			elements.push( $('<br>') );
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
	$.ajax('/v1/spider/visit', {
		'method': 'post',
		'content-type': 'application/json',
		'data': json
	});
	resumePolling();
}

function resumeSpider()
{
	$.ajax('/v1/spider/resume', {
		'method': 'post',
		'content-type': 'application/json',
		'data': '{}'
	});
	resumePolling();
}

function stopSpider()
{
	$.ajax('/v1/spider/stop', {
		'method': 'post',
		'content-type': 'application/json',
		'data': '{}'
	});
}

function recalculateKeywordFrequencies()
{
	$.ajax('/v1/spider/stopAndRecalculate', {
		'method': 'post',
		'content-type': 'application/json',
		'data': '{}'
	});
}

function poll()
{
	$.ajax('/v1/spider/status').then( response => {
		$('#status').text( response.status );
		if (!response.running)
		{
			stopPolling();
		}
	});
}

function resumePolling()
{
	if (polling == undefined)
	{
		polling = window.setInterval( poll, 500 );
	}
}

function stopPolling()
{
	if (polling != undefined)
	{
		window.clearInterval(polling);
		polling = undefined;
	}
}

