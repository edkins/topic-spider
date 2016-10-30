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
