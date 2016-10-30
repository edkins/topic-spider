function changeRank(event)
{
	var action = event.target.value
	var name = event.target.name
	$('#loading-'+name).css('visibility','visible')
}
