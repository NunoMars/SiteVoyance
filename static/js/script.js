$(window).load(function() {
    $messages.mCustomScrollbar();
    sendMessageClairvoyant("Bonjour");
    firstClairvoyantMessage();
});

var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

const clairvoyanteSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/clairvoyante/'
);

clairvoyanteSocket.onmessage = function(e) {
    console.log("Raw message: ", e.data); // Ajoutez cette ligne pour vérifier le message brut
    let data;
    try {
        data = JSON.parse(e.data);
    } catch (error) {
        console.log("Error parsing JSON: ", error);
        return;
    }
    $('.message.loading').remove();
    displayMessagePart(data.message);
    RedirectionJavascript();
};

clairvoyanteSocket.onopen = function() {
    console.log("WebSocket connection opened.");
};

clairvoyanteSocket.onerror = function(error) {
    console.log("WebSocket error: ", error);
};

clairvoyanteSocket.onclose = function() {
    console.log("WebSocket connection closed.");
};

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function displayMessagePart(message) {
    let index = 0;
    const interval = setInterval(() => {
        if (index < message.length) {
            const part = message.slice(0, index + 1);
            $('.message.new').last().text(part);
            index++;
            updateScrollbar();
        } else {
            clearInterval(interval);
        }
    }, 50); // Ajustez l'intervalle de temps pour contrôler la vitesse d'affichage
}

function clairvoyantMessage(message) {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container')).addClass('new');
    displayMessagePart(message);
    setDate();
    updateScrollbar();
}