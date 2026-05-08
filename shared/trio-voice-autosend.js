/* <!-- BEGIN: trio-voice-autosend --> */
window.trioToggleMic = function(){
    var btn = document.getElementById('tw-mic');
    var ta = document.getElementById('tw-input');
    if (!btn || !ta) return;

    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Voice dictation not supported in this browser. Try Chrome, Edge, or Safari.');
      return;
    }

    if (_trioRecognizing) {
      try { _trioRecognition && _trioRecognition.stop(); } catch(e){}
      return;
    }

    _trioRecognition = new SpeechRecognition();
    _trioRecognition.continuous = true;
    _trioRecognition.interimResults = true;
    _trioRecognition.lang = 'en-US';

    var baseText = ta.value;
    var finalText = '';

    _trioRecognition.onstart = function(){
      _trioRecognizing = true;
      btn.classList.add('recording');
      btn.title = 'Tap to stop';
    };
    _trioRecognition.onend = function(){
      _trioRecognizing = false;
      btn.classList.remove('recording');
      btn.title = 'Voice dictation';
      ta.focus();
    };
    _trioRecognition.onerror = function(e){
      _trioRecognizing = false;
      btn.classList.remove('recording');
      console.warn('[trio-voice] error:', e.error);
      if (e.error === 'not-allowed') {
        alert('Microphone permission denied. Enable mic access in your browser settings.');
      }
    };
    var _autoSendTimer = null;
    var _countdownInterval = null;
    var SILENCE_TIMEOUT_MS = 3500;
    var TRIGGER_PHRASES = /\b(send it|send now|send message|fire it|fire away|send)\b\.?\s*$/i;

    function clearAutoSend(){
      if (_autoSendTimer) { clearTimeout(_autoSendTimer); _autoSendTimer = null; }
      if (_countdownInterval) { clearInterval(_countdownInterval); _countdownInterval = null; }
      var statusEl = document.getElementById('tw-status');
      if (statusEl && statusEl.textContent.startsWith('Sending in')) statusEl.textContent = '';
    }

    function fireSend(){
      clearAutoSend();
      try { _trioRecognition && _trioRecognition.stop(); } catch(e){}
      if (window.trioSend && (ta.value || '').trim()) {
        window.trioSend();
      }
    }

    function startCountdown(){
      clearAutoSend();
      var statusEl = document.getElementById('tw-status');
      var seconds = Math.ceil(SILENCE_TIMEOUT_MS / 1000);
      var remaining = seconds;
      if (statusEl) {
        statusEl.style.color = 'var(--orange, #f1420b)';
        statusEl.textContent = 'Sending in ' + remaining + 's... (speak to cancel)';
      }
      _countdownInterval = setInterval(function(){
        remaining--;
        if (statusEl && remaining > 0) statusEl.textContent = 'Sending in ' + remaining + 's... (speak to cancel)';
      }, 1000);
      _autoSendTimer = setTimeout(fireSend, SILENCE_TIMEOUT_MS);
    }

    _trioRecognition.onresult = function(event){
      clearAutoSend();
      var interim = '';
      for (var i = event.resultIndex; i < event.results.length; i++){
        var t = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += t + ' ';
        else interim += t;
      }
      var combined = (baseText + ' ' + finalText + interim).trim();

      // Check for trigger phrase at end → strip + send immediately
      if (TRIGGER_PHRASES.test(combined)) {
        var stripped = combined.replace(TRIGGER_PHRASES, '').trim();
        ta.value = stripped;
        ta.style.height = 'auto';
        ta.style.height = Math.min(240, ta.scrollHeight) + 'px';
        // Small delay so user sees the value before send
        setTimeout(fireSend, 200);
        return;
      }

      ta.value = combined;
      ta.style.height = 'auto';
      ta.style.height = Math.min(240, ta.scrollHeight) + 'px';

      // If we got a final result, start the countdown for auto-send
      var hasNewFinal = false;
      for (var j = event.resultIndex; j < event.results.length; j++){
        if (event.results[j].isFinal) { hasNewFinal = true; break; }
      }
      if (hasNewFinal && combined) startCountdown();
    };

    // Patch the existing onend handler to clear timer
    var _origOnend = _trioRecognition.onend;
    _trioRecognition.onend = function(){
      clearAutoSend();
      if (_origOnend) _origOnend();
    };

    try { _trioRecognition.start(); }
    catch(e){ console.warn('[trio-voice] start failed:', e); }
  };
/* <!-- END: trio-voice-autosend --> */
