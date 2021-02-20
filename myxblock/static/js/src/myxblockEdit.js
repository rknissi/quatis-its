function MyXBlockEdit(runtime, element) {

  var handleUrl = runtime.handlerUrl(element, 'submit_data');

  $('#save_button', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      problemTitle: el.find('input[name=problemTitle]').val(),
      problemDescription: el.find('input[id=problemDescription]').val(),
      problemCorrectRadioAnswer: el.find('input[id=problemCorrectRadioAnswer]').val(),
      problemCorrectSteps: el.find('input[id=problemCorrectSteps]').val(),
      problemTipsToNextStep: el.find('input[id=problemTipsToNextStep]').val(),
      problemDefaultHint: el.find('input[id=problemDefaultHint]').val(),
      problemAnswer1: el.find('input[id=problemAnswer1]').val(),
      problemAnswer2: el.find('input[id=problemAnswer2]').val(),
      problemAnswer3: el.find('input[id=problemAnswer3]').val(),
      problemAnswer4: el.find('input[id=problemAnswer4]').val(),
      problemAnswer5: el.find('input[id=problemAnswer5]').val(),
      problemSubject: el.find('input[id=problemSubject]').val(),
      problemTags: el.find('input[id=problemTags]').val()
    };

    $.ajax({
      type: "POST",
      url: handleUrl,
      data: JSON.stringify(data),
      success: function (data) {
          window.location.reload(false);
      }   
  });

  });

  $('#cancel_button', element).click(function(eventObject) {
    runtime.notify('cancel', {});
  });
}
