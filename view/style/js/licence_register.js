var permissions = []
var duties = []
var prohibitions = []

var updateRuleDisplay = function() {
    ruleDisplay = $('#rule-list-template').clone()
    insertRulesOfType('permission', permissions, ruleDisplay.find('#duty-header'))
    insertRulesOfType('duty', duties, ruleDisplay.find('#prohibition-header'))
    insertRulesOfType('prohibition', prohibitions, ruleDisplay.find('#end-rule-list'))
    $('#rule-list').html(ruleDisplay.html())
}

var insertRulesOfType = function(rule_type, rule_list, destination) {
    for (i = 0; i < rule_list.length; i++) {
        template = $('#rule-item-template').clone().children()
        template.find('a').text(rule_list[i]['LABEL']).attr('href', rule_list[i]['LINK'])
        template.addClass(rule_type + '-item')
        if (rule_list[i]['ASSIGNORS'].length > 0)
            template.find('.assignors').removeAttr('hidden').text('Assignors: ' + rule_list[i]['ASSIGNORS'].join(', '))
        if (rule_list[i]['ASSIGNEES'].length > 0)
            template.find('.assignees').removeAttr('hidden').text('Assignees: ' + rule_list[i]['ASSIGNEES'].join(', '))
        template.insertBefore(destination)
    }
}

// Adds items to rule list
$('body').on('click', '.add-rule', function() {
    var modal = $(this).closest('.modal')
    var list
    if (modal.attr('id') == 'addPermissionModal')
        list = permissions
    else if (modal.attr('id') == 'addDutyModal')
        list = duties
    else if (modal.attr('id') == 'addProhibitionModal')
        list = prohibitions
    selectInputField = modal.find('.modal-body').find('select')
    selectedAction = selectInputField.find('option:selected').first()
    actionLabel = selectedAction.text()
    actionURI = selectedAction.attr('data-action-uri')
    actionLink = selectedAction.attr('data-action-link')
    assignors = []
    assignees = []
    modal.find('.assignor-list').find('.list-group-item-label').each(function() {
        assignors.push($(this).text())
    })
    modal.find('.assignee-list').find('.list-group-item-label').each(function() {
        assignees.push($(this).text())
    })
    list.push({
        'LABEL': actionLabel,
        'URI': actionURI,
        'LINK': actionLink,
        'ASSIGNORS': assignors,
        'ASSIGNEES': assignees
    })
    updateRuleDisplay()
    selectedAction.hide()
    selectInputField.val([])
    selectInputField.children(':visible').first().attr('selected', 'selected')
    modal.find('.assignor-list').children(':not(".active")').remove()
    modal.find('.assignee-list').children(':not(".active")').remove()
})

// Removes items from rule list when X clicked
$('body').on('click', '.delete-rule-item', function() {
    var list
    var selectInputField
    if ($(this).closest('li').hasClass('permission-item')) {
        list = permissions
        selectInputField = $('#addPermissionModal').find('select')
    }
    else if ($(this).closest('li').hasClass('duty-item')) {
        list = duties
        selectInputField = $('#addDutyModal').find('select')
    }
    else if ($(this).closest('li').hasClass('prohibition-item')) {
        list = prohibitions
        selectInputField = $('#addProhibitionModal').find('select')
    }
    itemLabel = $(this).siblings('a').first().text()
    var index = -1
    for (i = 0; i < list.length; i++) {
        if (list[i]['LABEL'] == itemLabel)
            index = i
    }
    if (index == -1)
        return
    list.splice(index, 1)
    selectInputField.find('option:contains("' + itemLabel + '")').show()
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
            updateSearchResults(data['perfect_licences'], data['extra_licences'], data['insufficient_licences'])
        }
    })
})

var updateSearchResults = function(perfect_licences, extra_licences, insufficient_licences) {
    //If there is an element with id 'results-all', all results should be displayed
    //If there is an element with id 'results-best', only the perfect fits should be displayed
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
            licence_entry.find('a').attr('href', perfect_licences[i]['LINK'])
            licence_entry.find('td:eq(0)').text(perfect_licences[i]['PERMISSIONS'].join(', '))
            licence_entry.find('td:eq(1)').text(perfect_licences[i]['DUTIES'].join(', '))
            licence_entry.find('td:eq(2)').text(perfect_licences[i]['PROHIBITIONS'].join(', '))
            licence_entry.find('td:eq(3)').text(perfect_licences[i]['ASSIGNORS'].join(', '))
            licence_entry.find('td:eq(4)').text(perfect_licences[i]['ASSIGNEES'].join(', '))
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
    entry.find('a').attr('href', licence_info['LINK'])
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

// Submits chosen permissions, duties and prohibitions with form
$('#licence-create-form').submit(function(event) {
    var permissions_input = $('<input>').attr('type', 'hidden').attr('name', 'permissions').attr('class', 'hidden-rule-input').val(JSON.stringify(permissions))
    var duties_input = $('<input>').attr('type', 'hidden').attr('name', 'duties').attr('class', 'hidden-rule-input').val(JSON.stringify(duties))
    var prohibitions_input = $('<input>').attr('type', 'hidden').attr('name', 'prohibitions').attr('class', 'hidden-rule-input').val(JSON.stringify(prohibitions))
    $('#licence-create-form').append(permissions_input)
    $('#licence-create-form').append(duties_input)
    $('#licence-create-form').append(prohibitions_input)
})

// Removing hidden inputs just in case the back button was used
$(window).on('unload', function() {
    $('.hidden-rule-input').remove()
})

// Adding assignors/assignees to a permission
$('body').on('click', '.add-party', function() {
    addParty($(this).parent().siblings('input').first())
})
$('body').on('focusout', '.party-input', function() {
    addParty($(this))
})
$('body').on('keyup', '.party-input', function(event) {
    if (event.keyCode === 13)
        addParty($(this))
})
var addParty = function(input_field) {
    if (input_field.val().length <= 0)
        return
    party = input_field.val()
    input_field.val('')
    var new_list_item = $('#party-item-template').clone().children()
    new_list_item.find('div').text(party)
    input_field.closest('.input-group').prev().append(new_list_item)
}

// Removes assignor/assignee from a permission
$('body').on('click', '.delete-party-item', function() {
    $(this).parent().remove()
})

updateRuleDisplay()