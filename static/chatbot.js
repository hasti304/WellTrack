(function () {
  const thread = document.getElementById('chat-thread');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const err = document.getElementById('chat-error');
  const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;

  function appendLine(who, text) {
    const wrap = document.createElement('div');
    wrap.className = 'mb-2' + (who === 'Welltrack' ? ' text-primary' : '');
    wrap.innerHTML = '<strong>' + who + ':</strong> <span class="chat-content"></span>';
    wrap.querySelector('.chat-content').textContent = text;
    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    err.textContent = '';
    const msg = (input.value || '').trim();
    if (!msg) return;
    appendLine('You', msg);
    input.value = '';
    fetch('/api/chatbot/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify({ message: msg }),
    })
      .then(function (r) {
        return r.json().then(function (data) {
          if (!r.ok) throw new Error(data.error || 'Request failed');
          return data;
        });
      })
      .then(function (data) {
        appendLine('Welltrack', data.reply || '');
      })
      .catch(function (ex) {
        err.textContent = ex.message || 'Error';
      });
  });
})();
