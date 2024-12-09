var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function() {
    $messages.mCustomScrollbar();
    firstClairvoyantMessage();
});

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function clairvoyantMessage(message) {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure>' + message + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    updateScrollbar();
}

function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
        $('<div class="checkmark-sent-delivered">&check;</div>').appendTo($('.message:last'));
        $('<div class="checkmark-read">&check;</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
        return false;
    }
    escapeHtml(msg);
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();

    if (i === 0) {
        let nameMsg = JSON.stringify({ subject: "name", name: msg });
        getMessageClairvoyant(nameMsg);
        i++;
    } else {
        let Msg = JSON.stringify({ subject: "question", question: msg });
        getMessageClairvoyant(Msg);
    }
}

function escapeHtml(msg) {
    if (typeof msg !== 'string') {
        console.error("Invalid value passed to escapeHtml:", msg);
        return '';
    }
    return msg
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

const token = '{{csrf_token}}';

function getMessageClairvoyant(msg) {
    $.ajax({
        type: 'POST',
        headers: { "X-CSRFToken": token },
        url: '{% url "clairvoyante" %}',
        dataType: 'json',
        data: {
            messageInput: msg,
        },
        success: function (data) {
            $('.message.loading').remove();
            updateScrollbar();
            if (data.subject == "menu") {
                $('.message.loading').remove();
                menuChoices(data);
            }
            if (data.subject == "one_card") {
                $('.message.loading').remove();
                oneCardResponse(data);
                continueChoice();
            }
            if (data.subject == "rec_no") {
                $('.message.loading').remove();
                menuChoices(data);
            }
            if (data.subject == "sorry") {
                $('.message.loading').remove();
                clairvoyantMessage(data.message);
            }

            if (data.subject == "cut") {
                $('.message.loading').remove();
                displayMessageCut(data);
            }
            if (data.subject == "choose_deck") {
                $('.message.loading').remove();
                chooseCutDeck(data);
            }
            if (data.subject == "propose to choose five cards") {
                $('.message.loading').remove();
                proposeToChoose(data.message);

            }
            if (data.subject == "prediction") {
                $('.message.loading').remove();
                displayChosenCards(data);             
                clairvoyantMessage(data.predictions);
                              
            }

            if (data.subject == "No") {
                $('.message.loading').remove();
                clairvoyantMessage(data.message); 
                RedirectionJavascript();
            }
        },
    });
};

function Redirect() 
{  
    document.location.href = "/"; 
} 

function RedirectionJavascript() {    
    setTimeout(Redirect, 2000); 
}

$('.message-submit').click(function() {
    insertMessage();
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
});

$(window).on('keydown', function(e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    };
});

$('#message-form').submit(function(event) {
    event.preventDefault();
    insertMessage();

});

function firstClairvoyantMessage() {
    if ($('.message-input').val() != '') {
        return false;
    }
    sentence = "Bonjour, je suis Mme T, votre voyante virtuelle. Je vous propose d'éclairer votre avenir a l'aide du tarot! Mais avant tout, il nous faut faire connaissance. Quel est votre prénom svp?"

    let msg = "<div class='col'><div class='cta-inner text-center rounded'>" +
        "<p class='mb-0'>" +
        sentence +
        "</p> "
    clairvoyantMessage(msg);
        $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function displayMessageCut(data) {
    message_cut = "<div class='cta-inner text-center rounded'>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<p><h4>" + "Merci beaucoup " + data.user_name.charAt(0).toUpperCase() + data.user_name.slice(1) + " !</h4></p>" +
        " <p>" + "Encore une chose svp!" + "</p>" +
        " <p>" + "Cliquez afin de couper le jeu de cartes!" +
        "</p></div></div>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<input id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageCut();'/></div>" +
        "</div></div></div>"
    clairvoyantMessage(message_cut);
        $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function continueChoice() {
    msg = "<div class='cta-inner text-center rounded'>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<p><h3>" + "Voulez-vous refaire un autre tirage?" + "</h3></p></div></div>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<p><h6>" + "OUI" + "</h6></p>" +
        "<p><input id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageYes();'/></p></div>" +
        "<div class='col'>" + "<p><h6>" + "NON" + "</h6></p>" +
        "<p><input id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageNo();'/></p></div>" +
        "</div></div>"
    clairvoyantMessage(msg);
        $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function menuChoices(data) {
    menu = "<div class='cta-inner text-center rounded'>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<p><h6>" + "Merci beaucoup " + data.user_name.charAt(0).toUpperCase() + data.user_name.slice(1) + " !</h6></p>" +
        "<p><h5>" + " Je mélange les lâmes du tarot..." + "</h5></p></div></div>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<p><h5>" + "Choisissiez le domaine de la question!" + "</h5></p>" +
        "<p><h6>" + "Cliquez sur le paquet de cartes svp!" + "</h6></p></div></div>" +
        "<div class='row'>" +
        "<div class='col'>" +
        "<p><h6>" + "TIRAGE AMOUR" + "<h6></p>" +
        "<p><button id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageLove();'/></button></p></div>" +
        "<div class='col'>" +
        "<p><h6>" + "TIRAGE TRAVAIL" + "</h6></p>" +
        "<p><button id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageWork();'/></button></p></div>" +
        "<div class='col'>" +
        "<p><h6>" + " TIRAGE GENERAL" + "</h6></p>" +
        "<p><button id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageGen();'/></button></p></div>" +
        "<div class='col'>" +
        "<p><h6>" + "TIRAGE RAPIDE" + "</h6></p>" +
        "<p><button id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageOneCard();'/></button></p></div>" +
        "</div></div>"
    clairvoyantMessage(menu);
        $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};


function proposeToChoose(deck_data) {
    if (!deck_data || deck_data.length === 0) {
        console.error("Deck data is empty or undefined.");
        return;
    }

    let selectedCards = [];
    let cardsHtml = `
        <div id="cards-container" style="display: flex; flex-direction: column; align-items: center;">
            <p><h5>Veuillez sélectionner 5 cartes pour révéler les mystères de votre avenir.</h5></p>
            <div style="display: flex; flex-wrap: wrap; justify-content: center;">
    `;

    deck_data.forEach(card => {
        if (!card.name || !card.image_url) {
            console.warn("Invalid card data:", card);
            return;
        }

        const escapedName = escapeHtml(card.name);
        
        cardsHtml += `
            <img class='card' src='/static/img/cards/Back.jpg' 
                 data-id='${escapedName}' 
                 data-image-url='${card.image_url}' 
                 alt='${escapedName}' 
                 style='width: 100px; height: 150px; margin: 10px; cursor: pointer;'>
        `;
    });
    cardsHtml += '</div></div>';

    clairvoyantMessage(cardsHtml);

    const cardElements = document.querySelectorAll('.card');
    if (!cardElements) {
        console.error("Card elements not found.");
        return;
    }

    cardElements.forEach(cardElement => {
        cardElement.addEventListener('click', () => {
            if (cardElement.classList.contains('selected') || selectedCards.length >= 5) {
                return; // Prevent changing the selection or selecting more than 5 cards
            }

            cardElement.classList.add('selected');
            cardElement.src = cardElement.dataset.imageUrl;
            selectedCards.push(cardElement.dataset.id);

            // Automatically submit when exactly 5 cards are selected
            if (selectedCards.length === 5) {
                let msg = JSON.stringify({ subject: "list of chosed cards", "list of chosed cards": selectedCards });
                getMessageClairvoyant(msg);
            }
        });
    });
     $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
}
function displayChosenCards(data) {
    let {cards, predictions} = data;
    if (!cards || cards.length === 0) {
        console.error("No cards to display.");
        return;
    }
    if (!predictions) {
        console.error("No predictions to display.");
        return;
    }

    let displayHtml = `
        <div class='text-center'>
            <div class='row'>
                <div class='col'>
                    <h5>${escapeHtml(cards[0].name)}</h5>
                    <h6>${escapeHtml(predictions.carte1?.nom || "Nom non disponible")}</h6>
                    <img class='card' src='${cards[0].image_url}' alt='${escapeHtml(cards[0].name)}' style='width: 100px; height: 150px; margin: 10px;'>
                    <p>${escapeHtml(predictions.carte1?.signification || "Signification non disponible")}</p>
                </div>
            </div>
            <div class='row'>
                <div class='col'>
                    <h5>${escapeHtml(cards[1].name)}</h5>
                    <h6>${escapeHtml(predictions.carte2?.nom || "Nom non disponible")}</h6>
                    <img class='card' src='${cards[1].image_url}' alt='${escapeHtml(cards[1].name)}' style='width: 100px; height: 150px; margin: 10px;'>
                    <p>${escapeHtml(predictions.carte2?.signification || "Signification non disponible")}</p>
                </div>
            </div>
            <div class='row'>
                <div class='col'>
                    <h5>${escapeHtml(cards[2].name)}</h5>
                    <h6>${escapeHtml(predictions.carte3?.nom || "Nom non disponible")}</h6>
                    <img class='card' src='${cards[2].image_url}' alt='${escapeHtml(cards[2].name)}' style='width: 100px; height: 150px; margin: 10px;'>
                    <p>${escapeHtml(predictions.carte3?.signification || "Signification non disponible")}</p>
                </div>
            </div>
            <div class='row'>
                <div class='col'>
                    <h5>${escapeHtml(cards[3].name)}</h5>
                    <h6>${escapeHtml(predictions.carte4?.nom || "Nom non disponible")}</h6>
                    <img class='card' src='${cards[3].image_url}' alt='${escapeHtml(cards[3].name)}' style='width: 100px; height: 150px; margin: 10px;'>
                    <p>${escapeHtml(predictions.carte4?.signification || "Signification non disponible")}</p>
                </div>
            </div>
            <div class='row'>
                <div class='col'>
                    <h5>${escapeHtml(cards[4].name)}</h5>
                    <h6>${escapeHtml(predictions.carte5?.nom || "Nom non disponible")}</h6>
                    <img class='card' src='${cards[4].image_url}' alt='${escapeHtml(cards[4].name)}' style='width: 100px; height: 150px; margin: 10px;'>
                    <p>${escapeHtml(predictions.carte5?.signification || "Signification non disponible")}</p>
                </div>
            </div>
            <div class='row'>
                <div class='col'>
                    <h5>Prédiction</h5>
                    <p>${escapeHtml(predictions.prediction || "Prédiction non disponible")}</p>
                </div>
            </div>
            <div class='row'>
                <div class='col'>
                    <h5>Réponse à la question</h5>
                    <p>${escapeHtml(predictions.reponse || "Réponse non disponible")}</p>
                </div>
            </div>
        </div>
    `;
    document.querySelector('.mCSB_container').innerHTML += displayHtml;
    updateScrollbar();
}

function oneCardResponse(data) {
    card_response = "<div class='col cta-inner text-center rounded'>" +
        "<h2>" + data.user_name.charAt(0).toUpperCase() + data.user_name.slice(1) + " vois-ci ce que le Tarot a vous dire!" + "</h2>" +
        "<a href='#'><img class='img-fluid card' src='" + '/static/img/cards/Back.jpg' + "'" +
        "onmouseover=" + '"this.src=' + "'" + data.card_image + "'" + '"' +
        " alt='' width='18%'/>" +
        "<p><h3>" + data.card_name.charAt(0).toUpperCase() + data.card_name.slice(1) + "</h3></p>" +
        "<div class='mb-0'><h3>" + "Attention" + "</h3></div>" +
        "<p class='mb-0'>" + data.card_signification_warnings + "</p>" +
        "<div class='mb-0'><h4>" + "En general" + "</h4></div>" +
        "<p class='mb-0'>" + data.card_signification_gen + "</p>" +
        "<div class='mb-0'><h4>" + "En amour" + "</h4></div>" +
        "<p class='mb-0'>" + data.card_signification_love + "</p>" +
        "<div class='mb-0'><h4>" + "Dans le travail" + "</h4></div>" +
        "<p class='mb-0'>" + data.card_signification_work + "</p>" +
        "</div>"
    clairvoyantMessage(card_response);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function chooseCutDeck(data) {
    deck_choice = "<div class='col'><div class='cta-inner text-center rounded'>" +
        "<p class='mb-0'><h4>" + "Merci !" + "</h4></p>" +
        "<p class='mb-0'>" + "On a donc deux paquets de cartes!" + "</p>" +
        "<p class='mb-0'>" + "Cliques sur celui de votre choix svp!" + "</p></div></div>" +
        "<div class='row'>" +
        "<div class='col''><div class='cta-inner text-center rounded'>" +
        "<h4>Ce paquet a " + data.len_left_deck + " cartes!" +
        "<div class='mb-0'><button id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageLeft();'/></button></div></div></div>" +
        "<div class='col''><div class='cta-inner text-center rounded'>" +
        "<h4>Celui ci a " + data.len_right_deck + " cartes!" +
        "<div class='mb-0'><button id='bouton_card' class='bouton_card img-fluid' onClick='sendMessageRight();'/></button></div></div></div>" +
        "</div>"
    clairvoyantMessage(deck_choice);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function responseCard(data) {
    response_card_message = "<div class='col cta-inner text-center rounded'>" +
        "<h3>" + data.user_name.charAt(0).toUpperCase() + data.user_name.slice(1) +
        " vois-ci votre votre message, ce que le Tarot a vous dire!</h3>" +
        "<a href='#'><img class='img-fluid card' src='/static/img/cards/Back.jpg'" +
        "onmouseover=" + '"this.src=' + "'" + data.card_image + "'" + '"' +
        " alt='arcana card'/>" +
        "<p><h2>" + data.card_name.charAt(0).toUpperCase() + data.card_name.slice(1) + "</h2></p>" +
        "<div class='mb-0'><h3>" + "Réponse" + "</h3></div>" +
        "<p class='mb-0'>" + data.chosed_theme_signification + "</p>" +
        "<h3>Attention Toutefois</h3>" +
        "<p class='mb-0'>" + data.warnings + "</p>" +
        "</div>"
    clairvoyantMessage(response_card_message)
};


$('.button').click(function() {
    $('.menu .items span').toggleClass('active');
    $('.menu .button').toggleClass('active');
});

function sendMessageLove() {
    let msg = JSON.stringify({ subject:"love" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageWork() {
    let msg = JSON.stringify({ subject:"work" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageGen() {
    let msg = JSON.stringify({ subject:"gen" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageOneCard() {
    let msg = JSON.stringify({ subject:"one" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageCut() {
    let msg = JSON.stringify({ subject:"cut" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageLeft() {
    let msg = JSON.stringify({ subject:"left" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageRight() {
    let msg = JSON.stringify({ subject:"right" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageYes() {
    let msg = JSON.stringify({ subject:"yes" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

function sendMessageNo() {
    let msg = JSON.stringify({ subject:"no" });
    getMessageClairvoyant(msg);
    $('<div class="message loading new"><figure class="avatar"><img src= "../static/img/voyante.jpg"/></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
};

$(window).unload(function() {
    $messages.mCustomScrollbar();
    let msg = JSON.stringify({ subject:"quit" });
    getMessageClairvoyant(msg)
});

$('.button').click(function() {
    $('.menu .items span').toggleClass('active');
    $('.menu .button').toggleClass('active');
});