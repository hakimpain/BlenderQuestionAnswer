//may refresh browser with ctrl + shif + r to update the browser cache

function onClickOption(option,requestUrl,is_logged)
{
    dropdownBtn = document.getElementById('dropdownBtn');
    if (option == 'None') dropdownBtn.innerText = 'Pick a version';
    else{
        dropdownBtn.innerText = option;
        if(is_logged == 'True') loadSessionHistory(requestUrl)
    }
}

function loadSessionHistory(requestUrl){
    fetch(requestUrl, {
    method: 'GET'
    })
    .then(response => response.json()) 
    .then(data => onReceiveHistory(data))
    .catch(error => console.error('Error:', error));
}

function onReceiveHistory(data)
{
    document.getElementById('messages_list').innerHTML = '';

    for(i=0;i<data.length;i++){
        msg = data[i]
        addUserQuestion(msg['question'])
        addAIAnswer(msg['answer'],msg['suggestions'])
    }
}

function cleanMemoryHistory(clean_history_url){
    selected_version = getSelectedVersion()
    if(isNaN(selected_version)) return;

    const formData = new FormData();
    formData.append('version', selected_version);
    const session_id = sessionStorage.getItem('session_id');
    if (session_id) formData.append('session_id', session_id);

    fetch(clean_history_url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    },
    body: formData
    })
    .then(response => response.json()) 
    .then(data => onCleanHistory(data))
    .catch(error => console.error('Error:', error));
}

function onCleanHistory(data){
    if('msg' in data){
        document.getElementById('messages_list').innerHTML = '';
        window.alert(data['msg'])
    }
}

function getSelectedVersion()
{
    dropdownBtn = document.getElementById('dropdownBtn');
    selected_version = parseFloat(dropdownBtn.innerText);
    return selected_version
}

function showAdvancedOptions()
{
    adv_options = document.getElementById('adv_options_div');
    caret_icon = document.getElementById('caret_icon');
    if (adv_options.classList.contains('d-none') > 0){
        adv_options.classList.remove('d-none');
        caret_icon.className = 'fa-solid fa-caret-up'
    }
    else{
        adv_options.classList.add('d-none');
        caret_icon.className = 'fa-solid fa-caret-down'
    }
}

function addUserQuestion(question)
{
    messagesList = document.getElementById('messages_list');

    const newDiv = document.createElement('div');
    const title = document.createElement('p');
    const contentP = document.createElement('p');

    newDiv.className = 'individual_msg p-2 m-2 user_msg'
    //newDiv.textContent = question;
    contentP.textContent = question;
    title.textContent = 'QUESTION'

    newDiv.appendChild(title)
    newDiv.appendChild(document.createElement('hr'))
    newDiv.appendChild(contentP)


    messagesList.appendChild(newDiv);
}

function addAIAnswer(answer,suggestions)
{
    let messagesList = document.getElementById('messages_list');
    const newDiv = document.createElement('div');
    newDiv.className = 'individual_msg p-2 m-2 ai_msg'

    const title = document.createElement('p');
    title.textContent = 'ANSWER';

    newDiv.appendChild(title);
    newDiv.appendChild(document.createElement('hr'));


    if (answer.length > 0){
        const answerP = document.createElement('p');
        answerP.textContent  = answer;
        newDiv.appendChild(answerP);
    }
    if (suggestions.length > 0){
        const suggestionP = document.createElement('p');
        suggestionP.textContent = suggestions;
        newDiv.appendChild(document.createElement('hr'));
        newDiv.appendChild(suggestionP);
    }

    messagesList.appendChild(newDiv);
}

function request_answer(get_answer_url){
    message_input = document.getElementById('message_input');
    question = message_input.value.trim();

    if (question.length == 0) return;
    selected_version = getSelectedVersion();
    if(isNaN(selected_version)) return;
    message_input.value = "";

    addUserQuestion(question)

    use_memory_cb = document.getElementById('use_memory_cb').checked;
    const session_id = sessionStorage.getItem('session_id');

    const formData = new FormData();
    formData.append('question', question);
    formData.append('version', selected_version);
    formData.append('use_memory', use_memory_cb);

    if(session_id) formData.append('session_id',session_id)

    send_msg_btn = document.getElementById('send_msg_btn')
    send_msg_btn.disabled = true

    send_msg_btn_icon = document.getElementById('send_msg_btn_icon')
    send_msg_btn_icon.className = 'fa-solid fa-spinner fa-spin'

    fetch(get_answer_url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    },
    body: formData
    })
    .then(response => response.json()) 
    .then(data => on_get_answer(data))
    .catch(error => console.error('Error:', error));

}

function on_get_answer(data)
{
    if ('error' in data){
        window.alert(data['error'])
        return
    }

    //console.log(data)
    if ('session_id' in data){
        sessionStorage.setItem('session_id', data['session_id']);
    }
    
    let answer = ''
    let suggestions = ''
    if ('answer' in data) answer = data['answer']
    if ('suggestions' in data) suggestions = data['suggestions']
    addAIAnswer(answer,suggestions)

    document.getElementById('send_msg_btn').disabled = false;
    document.getElementById('send_msg_btn_icon').className = 'fas fa-search';
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function onRequestVersion(request_version_url){

    const selected_version = getSelectedVersion();
    if(isNaN(selected_version)) return;

    const formData = new FormData();
    formData.append('version', selected_version);

    fetch(request_version_url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
    },
    body: formData
    })
    .then(response => response.json()) 
    .then(data => onVersionRequestResponse(data))
    .catch(error => console.error('Error:', error));
}

function onVersionRequestResponse(data){
    if ('msg' in data){
        window.alert(data['msg'])
    }
}


