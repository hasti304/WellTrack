(function () {
  const thread = document.getElementById('coach-thread');
  const form = document.getElementById('coach-form');
  const input = document.getElementById('coach-input');
  const err = document.getElementById('coach-error');
  const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;

  function appendBubble(role, text) {
    const wrap = document.createElement('div');
    wrap.className = 'mb-3 p-2 rounded ' + (role === 'assistant' ? 'bg-white border' : 'bg-light');
    if (role === 'assistant' && typeof marked !== 'undefined') {
      wrap.innerHTML = marked.parse(text);
    } else {
      wrap.textContent = text;
    }
    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
  }

  fetch('/api/smart-coach/history/', { credentials: 'same-origin' })
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      (data.history || []).forEach(function (row) {
        appendBubble(row.role === 'assistant' ? 'assistant' : 'user', row.content);
      });
    })
    .catch(function () {
      err.textContent = 'Could not load history.';
    });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    err.textContent = '';
    const msg = (input.value || '').trim();
    if (!msg) return;
    appendBubble('user', msg);
    input.value = '';
    fetch('/api/smart-coach/', {
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
        let reply = data.reply || '';
        const citations = data.citations || [];
        if (citations.length) {
          reply += '\n\nSources: ' + citations.join(', ');
        }
        appendBubble('assistant', reply);
      })
      .catch(function (ex) {
        err.textContent = ex.message || 'Error';
      });
  });
})();
