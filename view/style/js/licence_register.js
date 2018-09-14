var permissions = []
var duties = []
var prohibitions = []

var updateRuleDisplay = function() {
    ruleDisplay = $('#rule-list-template').clone()
    for (i = 0; i < permissions.length; i++) {
        permissionTemplate = $('#permission-item-template').clone().children()
        permissionTemplate.find('span').text(permissions[i]['LABEL'])
        permissionTemplate.insertBefore(ruleDisplay.find('#duty-header'))
    }
    for (i = 0; i < duties.length; i++) {
        dutyTemplate = $('#duty-item-template').clone().children()
        dutyTemplate.find('span').text(duties[i]['LABEL'])
        dutyTemplate.insertBefore(ruleDisplay.find('#prohibition-header'))
    }
    for (i = 0; i < prohibitions.length; i++) {
        prohibitionTemplate = $('#prohibition-item-template').clone().children()
        prohibitionTemplate.find('span').text(prohibitions[i]['LABEL'])
        ruleDisplay.append(prohibitionTemplate)
    }
    $('#rule-list').html(ruleDisplay.html())
}

// Adds items to rule list when dropdown selected
$('body').on('click', '.dropdown-item', function() {
    var list
    if ($(this).hasClass('permission-item'))
        list = permissions
    else if ($(this).hasClass('duty-item'))
        list = duties
    else if ($(this).hasClass('prohibition-item'))
        list = prohibitions
    actionLabel = $(this).text()
    actionURI = $(this).attr('data-action-uri')
    list.push({'LABEL': actionLabel, 'URI': actionURI})
    updateRuleDisplay()
})

// Removes items from rule list when X clicked
$('body').on('click', '.delete-item', function() {
    var list
    if ($(this).parent().hasClass('permission-item'))
        list = permissions
    else if ($(this).parent().hasClass('duty-item'))
        list = duties
    else if ($(this).parent().hasClass('prohibition-item'))
        list = prohibitions
    itemLabel = $(this).siblings('span').first().text()
    var index = -1
    for (i = 0; i < list.length; i++) {
        if (list[i]['LABEL'] == itemLabel)
            index = i
    }
    if (index == -1)
        return
    list.splice(index, 1)
    updateRuleDisplay()
})

// AJAX request to get search results
$('body').on('click', '.search-button', function() {
    $.ajax({
        dataType: 'json',
        url: '/_search_results',
        data: {
            permissions: JSON.stringify(permissions.map(x => x['URI'])),
            duties: JSON.stringify(duties.map(x => x['URI'])),
            prohibitions: JSON.stringify(prohibitions.map(x => x['URI']))
        },
        success: function(data) {
            console.log(data)
            updateSearchResults(data['perfect_licences'], data['extra_licences'], data['insufficient_licences'])
        }
    })
})

var updateSearchResults = function(perfect_licences, extra_licences, insufficient_licences) {
    resultsTemplate = $('#results-template').clone()
    if ($('#results-all').length > 0) {
        if (perfect_licences.length > 0)
            resultsTemplate.find('#perfect-licence-header').removeAttr('hidden')
        if (extra_licences.length > 0)
            resultsTemplate.find('#extra-licence-header').removeAttr('hidden')
        if (insufficient_licences.length > 0)
            resultsTemplate.find('#insufficient-licence-header').removeAttr('hidden')
        for (i = 0; i < perfect_licences.length; i++)
            addLicenceEntry('perfect', perfect_licences[i], resultsTemplate.find('#perfect-licence-header'))
        for (i = 0; i < extra_licences.length; i++)
            addLicenceEntry('extra', extra_licences[i], resultsTemplate.find('#extra-licence-header'))
        for (i = 0; i < insufficient_licences.length; i++) {
            addLicenceEntry('insufficient', insufficient_licences[i], resultsTemplate.find('#insufficient-licence-header'))
        }
        $('#results-all').html(resultsTemplate.children())
    }
    else if ($('#results-best').length > 0) {
        if (perfect_licences.length > 0) {
            resultsTemplate.find('#suggested-licences-found').removeAttr('hidden')
            licence_entry = $('#licence-template').clone()
            licence_entry.find('h5').text(perfect_licences[i]['LABEL'])
            licence_entry.find('.card-header').attr('data-target', '#licence-' + i)
            licence_entry.find('.collapse').attr('id', 'licence-' + i)
            licence_entry.find('a').attr('href', perfect_licences[i]['URI'])
            resultsTemplate.append(licence_entry.children())
        }
        else
            resultsTemplate.find('#suggested-licences-not-found').removeAttr('hidden')
        $('#results-best').html(resultsTemplate.children())
    }

}

var addLicenceEntry = function(licence_type, licence_info, destination) {
    entry = $('#' + licence_type + '-licence-template').clone()
    entry.find('.card-header').attr('data-target', '#' + licence_type + '-licence-' + i)
    entry.find('.collapse').attr('id', licence_type + '-licence-' + i)
    entry.find('.card-header').children().text(licence_info['LABEL'])
    entry.find('a').attr('href', licence_info['URI'])
    if (licence_type == 'extra' || licence_type == 'insufficient') {
        if (licence_info['PROHIBITIONS'].length > 0)
            entry.find('td:eq(2)').text(licence_info['PROHIBITIONS'].join(', '))
        else
            entry.find('tr:eq(2)').remove()
        if (licence_info['DUTIES'].length > 0)
            entry.find('td:eq(1)').text(licence_info['DUTIES'].join(', '))
        else
            entry.find('tr:eq(1)').remove()
        if (licence_info['PERMISSIONS'].length > 0)
            entry.find('td:eq(0)').text(licence_info['PERMISSIONS'].join(', '))
        else
            entry.find('tr:eq(0)').remove()
    }
    entry.children().insertAfter(destination)
}

//Moves to next step in form
$('body').on('click', '.previous-button', function() {
    $('.nav-link.active').parent().prev('li').find('a').trigger('click')
})
//Moves to previous step in form
$('body').on('click', '.next-button', function() {
    $('.nav-link.active').parent().next('li').find('a').trigger('click')
})

updateRuleDisplay()