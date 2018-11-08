var PERMISSION_URI = 'http://www.w3.org/ns/odrl/2/permission'
var DUTY_URI = 'http://www.w3.org/ns/odrl/2/duty'
var PROHIBITION_URI = 'http://www.w3.org/ns/odrl/2/prohibition'
var rules = []

jQuery(document).ready(function($){

    //Updates the display of currently selected rules for searching using data in the global variable 'rules'
    //Populates #filter-rule-list using the following templates:
    //  #rule-item-template
    //  #rule-item-with-parties-template
    var updateRuleDisplay = function() {
        var filterRuleList = $('#filter-rule-list')
        filterRuleList.find('.rule-section').empty()
        for (var i = 0; i < rules.length; i++) {
            for (var j = 0; j < rules[i]['ACTIONS'].length; j++){
                var action = rules[i]['ACTIONS'][j]
                if (rules[i]['ASSIGNORS'].length > 0 || rules[i]['ASSIGNEES'].length > 0) {
                    var template = $('#rule-item-with-parties-template').clone().children()
                    template.find('.action-label').attr('href', action['LINK'])
                    if (rules[i]['ASSIGNORS'].length > 0) {
                        template.find('.assignors-heading').removeAttr('hidden')
                        for (var x = 0; x < rules[i]['ASSIGNORS'].length; x++) {
                            var assignor = rules[i]['ASSIGNORS'][x]
                            var list_item = $('<li></li>').attr('class', 'small')
                            var link = $('<a></a>').attr('class', 'reversed').attr('href', assignor['URI']).attr('target', '_blank').text(assignor['LABEL'])
                            template.find('ul:eq(0)').append(list_item.append(link))
                        }
                    }
                    if (rules[i]['ASSIGNEES'].length > 0) {
                        template.find('.assignees-heading').removeAttr('hidden')
                        for (var x = 0; x < rules[i]['ASSIGNEES'].length; x++) {
                            var assignee = rules[i]['ASSIGNEES'][x]
                            var list_item = $('<li></li>').attr('class', 'small')
                            var link = $('<a></a>').attr('class', 'reversed').attr('href', assignee['URI']).attr('target', '_blank').text(assignee['LABEL'])
                            template.find('ul:eq(1)').append(list_item.append(link))
                        }
                    }
                }
                else {
                    var template = $('#rule-item-template').clone().children()
                    template.find('a').attr('href', action['LINK'])
                }
                template.find('.action-label').text(action['LABEL'])
                template.attr('data-rule-type', rules[i]['TYPE_URI'])
                template.attr('data-action-uri', action['URI'])
                filterRuleList.find('.rule-section[data-rule-type="' + rules[i]['TYPE_URI'] + '"]').append(template)
            }
        }
        // Enable all bootstrap tooltips on page
        $('[data-toggle="tooltip"]').tooltip()
    }

    //Determines which actions should be available and which unavailable in the action select input
    //Decides this based on the rules that are currently selected
    //e.g. Read cannot be picked as Permission if it is already selected as a Prohibition
    var updateActionDisplay = function(){
        $('.add-rule-modal').each(function(){
            var ruleType = $(this).attr('data-rule-type')
            var selectInputField = $(this).find('.action-select')
            selectInputField.children().each(function(){
                $(this).prop('hidden', false)
                for (var i = 0; i < rules.length; i++){
                    for (var j = 0; j < rules[i]['ACTIONS'].length; j++){
                        action = rules[i]['ACTIONS'][j]
                        if (action['URI'] == $(this).attr('data-action-uri')
                            && (rules[i]['TYPE_URI'] == ruleType
                            || ruleType == PROHIBITION_URI
                            || rules[i]['TYPE_URI'] == PROHIBITION_URI)){
                            $(this).prop('hidden', true)
                        }
                    }
                }
            })
            selectInputField.val([])
            selectInputField.children().filter(function(){
                return $(this).css('display') != 'none'
            }).first().prop('selected', true)
        })
    }

    // Takes information entered into the Add Rule Modal and adds a rule to the global list of current rules.
    // Also updates the rule and action displays.
    // Also updates the search results.
    $('body').on('click', '.add-rule', function() {
        var modal = $(this).closest('.modal')
        var selectInputField = modal.find('select')
        var selectedAction = selectInputField.find('option:selected').first()
        var action = {
            'LABEL': selectedAction.text(),
            'URI': selectedAction.attr('data-action-uri'),
            'LINK': selectedAction.attr('data-action-link')
        }
        var assignors = []
        var assignees = []
        modal.find('.assignor-list').find('.list-group-item-label').each(function() {
            assignors.push({
                'URI': $(this).attr('data-uri'),
                'LABEL': $(this).text(),
                'COMMENT': $(this).attr('data-comment'),
                'LINK': $(this).attr('data-link')
            })
        })
        modal.find('.assignee-list').find('.list-group-item-label').each(function() {
            assignees.push({
                'URI': $(this).attr('data-uri'),
                'LABEL': $(this).text(),
                'COMMENT': $(this).attr('data-comment'),
                'LINK': $(this).attr('data-link')
            })
        })
        rules.push({
            'ACTIONS': [action],
            'TYPE_URI': modal.attr('data-rule-type'),
            'ASSIGNORS': assignors,
            'ASSIGNEES': assignees
        })
        updateRuleDisplay()
        updateActionDisplay()
        modal.find('.assignor-list').children(':not(".active")').remove()
        modal.find('.assignee-list').children(':not(".active")').remove()
        modal.find('.party-select').children().show()
        search()
    })

    // Removes items from rule list when X clicked
    $('body').on('click', '.delete-rule', function() {
        var listItem = $(this).closest('li')
        var index = -1
        for (var i = 0; i < rules.length; i++) {
            for (var j = 0; j < rules[i]['ACTIONS'].length; j++){
                action = rules[i]['ACTIONS'][j]
                if (action['URI'] == listItem.attr('data-action-uri')
                    && rules[i]['TYPE_URI'] == listItem.attr('data-rule-type'))
                    index = i
            }
        }
        if (index == -1)
            throw "Cannot remove rule - rule index not found."
        rules.splice(index, 1)
        updateRuleDisplay()
        updateActionDisplay()
        search()
    })

    // Search when search button is pressed
    $('body').on('click', '.search-button', function() {
        search()
    })

    // AJAX request to get search results
    var search = function(){
        search_url = $('#search-url').attr('data-url')
        if (search_url == undefined)
            throw 'Search URL not found'
        $.ajax({
            dataType: 'json',
            url: search_url,
            data: {
                rules: JSON.stringify(rules),
            },
            success: function(data) {
                updateSearchResults(data['results'])
            }
        })
    }

    // Clear search filter
    // Also updates rule and action displays, and updates the search results
    $('body').on('click', '.clear-filter', function() {
        rules = []
        updateActionDisplay()
        updateRuleDisplay()
        search()
    })

    // Update the search results display
    // Populates #licence-list with the results
    // Unhides #licences-not-found if search results are empty. Otherwise, unhides #licences-found
    // Uses template #licence-item-template for each result entry
    var updateSearchResults = function(results) {
        var licenceList = $('#licence-list').empty()
        if (results.length > 0) {
            $('#licences-not-found').prop('hidden', true)
            $('#licences-found').prop('hidden', false)
            for (var i = 0; i < results.length; i++){
                var rules = results[i]['RULES']
                var licenceCard = $('#licence-item-template').clone()
                licenceCard.find('.card__title').text(results[i]['LABEL'])
                licenceCard.find('a').attr('href', results[i]['LINK'])
                if (rules.length > 0) {
                    var permissions = []
                    var duties = []
                    var prohibitions = []
                    for (var j = 0; j < rules.length; j++) {
                        var rule = rules[j]
                        for (var x = 0; x < rule['ACTIONS'].length; x++) {
                           var action = rule['ACTIONS'][x]
                            switch (rule['TYPE_URI']) {
                                case PERMISSION_URI:
                                    permissions.push(action['LABEL'])
                                    break
                                case DUTY_URI:
                                    duties.push(action['LABEL'])
                                    break
                                case PROHIBITION_URI:
                                    prohibitions.push(action['LABEL'])
                                    break
                            }
                        }
                    }
                    if (permissions.length > 0) {
                        licenceCard.find('p:eq(0)').prop('hidden', false)
                        licenceCard.find('p:eq(0) span:eq(1)').text(permissions.join(', '))
                    }
                    if (duties.length > 0) {
                        licenceCard.find('p:eq(1)').prop('hidden', false)
                        licenceCard.find('p:eq(1) span:eq(1)').text(duties.join(', '))
                    }
                    if (prohibitions.length > 0) {
                        licenceCard.find('p:eq(2)').prop('hidden', false)
                        licenceCard.find('p:eq(2) span:eq(1)').text(prohibitions.join(', '))
                    }
                }
                licenceList.append(licenceCard.children())
            }
        }
        else {
            $('#licences-not-found').prop('hidden', false)
            $('#licences-found').prop('hidden', true)
        }
    }

    // Submits chosen rules with form
    $('#licence-create-form').submit(function(event) {
        var rulesInput = $('<input>').attr('type', 'hidden').attr('name', 'rules').attr('class', 'hidden-rule-input').val(JSON.stringify(rules))
        $('#licence-create-form').append(rulesInput)
    })

    // Removing hidden inputs just in case the back button was used
    $(window).on('unload', function() {
        $('.hidden-rule-input').remove()
    })

    // Adding an assignor/assignee selection to the add rule modal
    $('body').on('click', '.party-select option', function() { // Clicking the option normally
        addParty($(this))
    })
    $('body').on('keypress', '.party-select', function(event){ // Selecting option via enter key press for accessibility
        var keycode = event.keyCode || event.which
        if (keycode == 13)
            addParty($(this).children(':selected').first())
    })
    var addParty = function(option){
        console.log(option.val())
        if (option.val().length == 0)
            return
        var new_list_item = $('#party-item-template').clone().children()
        new_list_item.find('.list-group-item-label').text(option.text())
        new_list_item.find('.list-group-item-label').attr('data-comment', option.attr('data-comment'))
        new_list_item.find('.list-group-item-label').attr('data-link', option.attr('data-link'))
        new_list_item.find('.list-group-item-label').attr('data-uri', option.attr('data-uri'))
        option.hide()
        option.parent().children().first().prop('selected', true)
        option.closest('.party-select-group').children('.list-group').first().append(new_list_item)
    }

    // Removes assignor/assignee selection from the add rule modal
    $('body').on('click', '.delete-party-item', function() {
        $(this).closest('.list-group').next().children('[value="' + $(this).prev().attr('data-uri') + '"]').show()
        $(this).closest('li').remove()
    })

    // Update search results with initial data
    if ($('#licences-json').length > 0) {
        var licences_json = JSON.parse($('#licences-json').html())
        updateSearchResults(licences_json)
    }


    // Enable all bootstrap tooltips on page
    $('[data-toggle="tooltip"]').tooltip()

    // For copying permalinks
    $('body').on('click', '#permalink', function() {
        $(this).select()
    });
    $('body').on('click', '.copy-button', function() {
        $('#permalink').focus().select()
        document.execCommand('copy')
    })
})