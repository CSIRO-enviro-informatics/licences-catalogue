rules = []
ruleTypes = ['permission', 'duty', 'prohibition']

var updateRuleDisplay = function() {
    ruleDisplay = $('#rule-list-template').clone()
    for (i = 0; i < rules.length; i++) {
        template = $('#rule-item-template').clone().children()
        template.find('a').text(rules[i]['ACTION']['LABEL']).attr('href', rules[i]['ACTION']['LINK'])
        template.addClass(rules[i]['TYPE_LABEL'].toLowerCase())
        if (rules[i]['ASSIGNORS'].length > 0)
            template.find('.assignors').removeAttr('hidden').text('Assignors: ' + rules[i]['ASSIGNORS'].join(', '))
        if (rules[i]['ASSIGNEES'].length > 0)
            template.find('.assignees').removeAttr('hidden').text('Assignees: ' + rules[i]['ASSIGNEES'].join(', '))
        if (rules[i]['TYPE_LABEL'] == 'permission')
            template.insertBefore(ruleDisplay.find('#duty-header'))
        if (rules[i]['TYPE_LABEL'] == 'duty')
            template.insertBefore(ruleDisplay.find('#prohibition-header'))
        if (rules[i]['TYPE_LABEL'] == 'prohibition')
            template.insertBefore(ruleDisplay.find('#end-rule-list'))
    }
    $('#rule-list').html(ruleDisplay.html())
}

var updateActionDisplay = function(){
    $('.add-rule-modal').each(function(){
        var ruleType
        for (i = 0; i < ruleTypes.length; i++){
            if ($(this).hasClass(ruleTypes[i]))
                ruleType = ruleTypes[i]
        }
        if (ruleType == undefined)
            throw 'Cannot refresh actions - modal has no rule type.'
        selectInputField = $(this).find('.action-select')
        selectInputField.children().each(function(){
            var action_uri = $(this).attr('data-action-uri')
            $(this).prop('hidden', false)
            for (i = 0; i < rules.length; i++){
                if (rules[i]['ACTION']['URI'] == action_uri && (rules[i]['TYPE_LABEL'].toLowerCase() == ruleType || ruleType == 'prohibition' || rules[i]['TYPE_LABEL'] == 'prohibition')){
                    $(this).prop('hidden', true)
                }
            }
        })
        selectInputField.val([])
        selectInputField.children(':visible').first().prop('selected', true)
    })
}

// Adds items to rule list
$('body').on('click', '.add-rule', function() {
    var modal = $(this).closest('.modal')
    selectInputField = modal.find('.modal-body').find('select')
    selectedAction = selectInputField.find('option:selected').first()
    action = {
        'LABEL': selectedAction.text(),
        'URI': selectedAction.attr('data-action-uri'),
        'LINK': selectedAction.attr('data-action-link')
    }
    var typeLabel
    if (modal.hasClass('add-rule-modal'))
        for (i = 0; i < ruleTypes.length; i++) {
            if (modal.hasClass(ruleTypes[i]))
                typeLabel = ruleTypes[i]
        }
    if (typeLabel == undefined)
        throw "Cannot add rule - unknown rule type."
    assignors = []
    assignees = []
    modal.find('.assignor-list').find('.list-group-item-label').each(function() {
        assignors.push($(this).text())
    })
    modal.find('.assignee-list').find('.list-group-item-label').each(function() {
        assignees.push($(this).text())
    })
    rules.push({
        'ACTION': action,
        'TYPE_LABEL': typeLabel,
        'ASSIGNORS': assignors,
        'ASSIGNEES': assignees
    })
    updateRuleDisplay()
    updateActionDisplay()
    modal.find('.assignor-list').children(':not(".active")').remove()
    modal.find('.assignee-list').children(':not(".active")').remove()
})

// Removes items from rule list when X clicked
$('body').on('click', '.delete-rule-item', function() {
    listItem = $(this).closest('li')
    var ruleTypeLabel
    for (i = 0; i < ruleTypes.length; i++) {
        if (listItem.hasClass(ruleTypes[i]))
            ruleTypeLabel = ruleTypes[i]
    }
    if (ruleTypeLabel == undefined)
        throw 'Cannot remove rule - unknown rule type.'
    actionLabel = $(this).siblings('a').first().text()
    var index = -1
    for (i = 0; i < rules.length; i++) {
        if (rules[i]['ACTION']['LABEL'] == actionLabel && rules[i]['TYPE_LABEL'].toLowerCase() == ruleTypeLabel)
            index = i
    }
    if (index == -1)
        throw "Cannot remove rule - rule index not found."
    rules.splice(index, 1)
    updateRuleDisplay()
    updateActionDisplay()
})

// AJAX request to get search results
$('body').on('click', '.search-button', function() {
    $.ajax({
        dataType: 'json',
        url: '/_search_results',
        data: {
            rules: JSON.stringify(rules),
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

// Submits chosen rules with form
$('#licence-create-form').submit(function(event) {
    var rulesInput = $('<input>').attr('type', 'hidden').attr('name', 'rules').attr('class', 'hidden-rule-input').val(JSON.stringify(rules))
    $('#licence-create-form').append(rulesInput)
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